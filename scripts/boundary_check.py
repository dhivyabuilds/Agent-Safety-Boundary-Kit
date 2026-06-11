#!/usr/bin/env python3
"""Evaluate third-party requests against an Agent Safety Boundary file."""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path
from typing import Any, Mapping


DECISIONS = {
    "allow",
    "warn",
    "defer",
    "approval_required",
    "refuse",
    "end_and_report",
}
MODES = {
    "pre_authorized_conditions",
    "ask_in_the_moment",
    "never_allow",
    "collect_and_report",
}
CHANNELS = {"voice_call", "chat", "website", "email", "agent_to_agent", "other"}
ACTION_TYPES = {
    "payment_or_deposit",
    "commitment",
    "identity_verification",
    "account_change",
    "scope_expansion",
    "memory_or_prompt_access",
    "other",
}


class BoundaryCheckError(ValueError):
    """Raised when boundary or request input is invalid."""


def load_document(path: str | Path) -> Any:
    """Load JSON or a small YAML subset used by boundary files."""

    source_path = Path(path)
    text = source_path.read_text(encoding="utf-8")
    if source_path.suffix.lower() == ".json":
        return json.loads(text)

    try:
        import yaml  # type: ignore
    except ModuleNotFoundError:
        return _parse_simple_yaml(text)
    loaded = yaml.safe_load(text)
    return {} if loaded is None else loaded


def load_boundary(path: str | Path) -> dict[str, Any]:
    boundary = load_document(path)
    if not isinstance(boundary, dict):
        raise BoundaryCheckError("boundary must be an object")
    _validate_boundary(boundary)
    return boundary


def load_request(path: str | Path) -> dict[str, Any]:
    request = load_document(path)
    if not isinstance(request, dict):
        raise BoundaryCheckError("request must be an object")
    validate_request(request)
    return request


def check_boundary(
    boundary: Mapping[str, Any],
    request: Mapping[str, Any],
    proposed_response: str | None = None,
    ledger_path: str | Path | None = None,
) -> dict[str, Any]:
    """Return the boundary decision for a structured third-party request."""

    _validate_boundary(boundary)
    validate_request(request)
    normalized = _normalize_request(request, proposed_response)

    decision = _evaluate(boundary, normalized)
    ledger_event = _build_ledger_event(boundary, normalized, decision)
    result = {
        "decision": decision["decision"],
        "matched_rule": decision["matched_rule"],
        "discretion_mode": decision["discretion_mode"],
        "reason": decision["reason"],
        "safe_response": decision["safe_response"],
        "ledger_event": ledger_event,
    }

    if ledger_path:
        append_ledger_event(ledger_path, ledger_event)
        result["ledger_event"] = {**ledger_event, "ledger_status": "written"}

    return result


def append_ledger_event(path: str | Path, event: Mapping[str, Any]) -> None:
    ledger_path = Path(path)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def validate_request(request: Mapping[str, Any]) -> None:
    missing = [
        field
        for field in ("channel", "third_party", "request_text")
        if field not in request
    ]
    if missing:
        raise BoundaryCheckError(f"request missing required field(s): {', '.join(missing)}")
    if "requested_disclosure" not in request and "requested_action" not in request:
        raise BoundaryCheckError(
            "request must include requested_disclosure or requested_action"
        )
    if request["channel"] not in CHANNELS:
        raise BoundaryCheckError(f"invalid channel: {request['channel']}")
    if "requested_action" in request and request["requested_action"] not in ACTION_TYPES:
        raise BoundaryCheckError(f"invalid requested_action: {request['requested_action']}")
    if not isinstance(request["request_text"], str) or not request["request_text"].strip():
        raise BoundaryCheckError("request_text must be a non-empty string")
    if "amount_usd" in request and (
        not isinstance(request["amount_usd"], (int, float)) or request["amount_usd"] < 0
    ):
        raise BoundaryCheckError("amount_usd must be a non-negative number")
    if "confidence" in request and (
        not isinstance(request["confidence"], (int, float))
        or request["confidence"] < 0
        or request["confidence"] > 1
    ):
        raise BoundaryCheckError("confidence must be between 0 and 1")


def _validate_boundary(boundary: Mapping[str, Any]) -> None:
    required = (
        "agent",
        "default_allowed_disclosures",
        "discretion_rules",
        "never_disclose",
        "fallbacks",
    )
    missing = [field for field in required if field not in boundary]
    if missing:
        raise BoundaryCheckError(f"boundary missing required field(s): {', '.join(missing)}")
    if not isinstance(boundary["discretion_rules"], list):
        raise BoundaryCheckError("boundary.discretion_rules must be a list")
    for rule in boundary["discretion_rules"]:
        if not isinstance(rule, dict):
            raise BoundaryCheckError("each discretion rule must be an object")
        for field in ("id", "request_type", "mode"):
            if field not in rule:
                raise BoundaryCheckError(f"discretion rule missing required field: {field}")
        if rule["mode"] not in MODES:
            raise BoundaryCheckError(f"invalid discretion mode: {rule['mode']}")
        if rule["request_type"] not in ACTION_TYPES | {"disclosure"}:
            raise BoundaryCheckError(f"invalid request_type: {rule['request_type']}")
        if "decision" in rule and rule["decision"] not in DECISIONS:
            raise BoundaryCheckError(f"invalid decision in rule {rule['id']}")
        if "otherwise" in rule and rule["otherwise"] not in DECISIONS:
            raise BoundaryCheckError(f"invalid otherwise decision in rule {rule['id']}")


def _normalize_request(
    request: Mapping[str, Any], proposed_response: str | None
) -> dict[str, Any]:
    normalized = dict(request)
    if proposed_response is not None:
        normalized["proposed_response"] = proposed_response
    disclosure = normalized.get("requested_disclosure")
    if isinstance(disclosure, str):
        normalized["_requested_disclosures"] = _split_scalar_list(disclosure)
    else:
        normalized["_requested_disclosures"] = []
    normalized["_request_type"] = (
        "disclosure" if normalized["_requested_disclosures"] else normalized["requested_action"]
    )
    return normalized


def _evaluate(boundary: Mapping[str, Any], request: Mapping[str, Any]) -> dict[str, str | None]:
    rules = boundary.get("discretion_rules", [])
    for rule in rules:
        if rule["mode"] == "never_allow" and _rule_applies(rule, request):
            return _decision(
                rule.get("decision", "refuse"),
                rule["id"],
                rule["mode"],
                f"{rule['id']} prohibits this request",
                rule.get("safe_response")
                or _safe_response(boundary, "prohibited_request", "refuse"),
            )

    never_fields = set(boundary.get("never_disclose", []))
    for field in request["_requested_disclosures"]:
        if field in never_fields:
            return _decision(
                "refuse",
                f"never_disclose:{field}",
                "never_allow",
                f"{field} is listed in never_disclose",
                _safe_response(boundary, "prohibited_request", "refuse"),
            )

    if request["_request_type"] == "disclosure":
        default_allowed = set(boundary.get("default_allowed_disclosures", []))
        if request["_requested_disclosures"] and all(
            field in default_allowed for field in request["_requested_disclosures"]
        ):
            return _decision(
                "allow",
                "default_allowed_disclosures",
                None,
                "requested disclosure is allowed by default",
                _safe_response(boundary, "allow", "allow"),
            )

    for rule in rules:
        if rule["mode"] != "pre_authorized_conditions" or not _rule_matches_type(rule, request):
            continue
        if not _conditions_match(rule.get("applies_when"), request).matched:
            continue
        condition_result = _conditions_match(rule.get("allowed_when"), request)
        if condition_result.matched:
            return _decision(
                "allow",
                rule["id"],
                rule["mode"],
                f"{rule['id']} allowed conditions matched",
                _safe_response(boundary, "allow", "allow"),
            )
        if condition_result.failed_key in {"vendor_category", "third_party_category", "purpose"}:
            continue
        otherwise = rule.get("otherwise", "approval_required")
        return _decision(
            otherwise,
            rule["id"],
            rule["mode"],
            f"{rule['id']} allowed conditions did not match: {condition_result.reason}",
            rule.get("safe_response")
            or _safe_response(boundary, "approval_needed", otherwise),
        )

    for rule in rules:
        if rule["mode"] == "ask_in_the_moment" and _rule_applies(rule, request):
            return _decision(
                rule.get("decision", "approval_required"),
                rule["id"],
                rule["mode"],
                f"{rule['id']} requires user approval in the moment",
                rule.get("safe_response")
                or _safe_response(boundary, "approval_needed", "approval_required"),
            )

    for rule in rules:
        if rule["mode"] == "collect_and_report" and _rule_applies(rule, request):
            return _decision(
                rule.get("decision", "defer"),
                rule["id"],
                rule["mode"],
                f"{rule['id']} allows collecting details but not satisfying the request",
                rule.get("safe_response")
                or _safe_response(boundary, "defer", "defer"),
            )

    if request.get("pressure_signal") or request.get("false_authority_signal"):
        decision = boundary.get("fallbacks", {}).get("repeated_pressure", "end_and_report")
        return _decision(
            decision,
            "fallback:repeated_pressure",
            None,
            "third party showed pressure or false-authority signals",
            _safe_response(boundary, "repeated_pressure", decision),
        )

    approval_required_for = set(boundary.get("approval_required_for", []))
    if _requires_approval(request, approval_required_for):
        return _decision(
            "approval_required",
            "approval_required_for",
            "ask_in_the_moment",
            "this request category requires user approval",
            _safe_response(boundary, "approval_needed", "approval_required"),
        )

    fallback = boundary.get("fallbacks", {}).get("unapproved_request", "defer")
    return _decision(
        fallback,
        "fallback:unapproved_request",
        None,
        "no discretion rule authorized this request",
        _safe_response(boundary, "unapproved_request", fallback),
    )


def _rule_matches_type(rule: Mapping[str, Any], request: Mapping[str, Any]) -> bool:
    if rule["request_type"] != request["_request_type"]:
        return False
    if rule["request_type"] == "disclosure" and "field" in rule:
        return rule["field"] in request["_requested_disclosures"]
    return True


def _rule_applies(rule: Mapping[str, Any], request: Mapping[str, Any]) -> bool:
    if not _rule_matches_type(rule, request):
        return False
    applies = _conditions_match(rule.get("applies_when"), request)
    allowed = _conditions_match(rule.get("allowed_when"), request)
    return applies.matched and allowed.matched


class _ConditionResult:
    def __init__(
        self, matched: bool, reason: str = "conditions matched", failed_key: str | None = None
    ) -> None:
        self.matched = matched
        self.reason = reason
        self.failed_key = failed_key


def _conditions_match(
    conditions: Mapping[str, Any] | None, request: Mapping[str, Any]
) -> _ConditionResult:
    if not conditions:
        return _ConditionResult(True)
    for key, expected in conditions.items():
        actual = _condition_actual(key, request)
        matched = _value_matches(actual, expected)
        if not matched:
            return _ConditionResult(
                False,
                f"{key} was {_format_value(actual)}, expected {_format_value(expected)}",
                key,
            )
    return _ConditionResult(True)


def _condition_actual(key: str, request: Mapping[str, Any]) -> Any:
    aliases = {
        "vendor_category": "third_party_category",
        "third_party_category": "third_party_category",
        "amount_usd_lte": "amount_usd",
        "max_amount_usd": "amount_usd",
        "amount_usd_gte": "amount_usd",
        "min_amount_usd": "amount_usd",
        "requires_explicit_task_approval": "user_preapproved",
        "user_preapproved_deposits": "user_preapproved",
        "user_preapproved": "user_preapproved",
        "minimum_confidence": "confidence",
        "confidence_gte": "confidence",
    }
    return request.get(aliases.get(key, key))


def _value_matches(actual: Any, expected: Any) -> bool:
    if isinstance(expected, Mapping):
        if "any_of" in expected:
            return actual in expected["any_of"]
        if "none_of" in expected:
            return actual not in expected["none_of"]
        if "equals" in expected:
            return actual == expected["equals"]
        if "lte" in expected:
            return actual is not None and actual <= expected["lte"]
        if "gte" in expected:
            return actual is not None and actual >= expected["gte"]
        if "contains" in expected:
            return isinstance(actual, str) and expected["contains"] in actual
        return all(_value_matches(actual, nested) for nested in expected.values())
    if isinstance(expected, list):
        return actual in expected
    return actual == expected


def _requires_approval(
    request: Mapping[str, Any], approval_required_for: set[str]
) -> bool:
    request_type = request["_request_type"]
    disclosures = set(request["_requested_disclosures"])
    if request_type == "payment_or_deposit":
        return bool({"payment", "deposit", "payment_or_deposit"} & approval_required_for)
    if request_type == "commitment":
        return bool({"commitment", "non_refundable_commitment"} & approval_required_for)
    if request_type in approval_required_for:
        return True
    return bool(disclosures & approval_required_for)


def _safe_response(boundary: Mapping[str, Any], key: str, decision: str) -> str:
    responses = boundary.get("safe_responses", {})
    if key in responses:
        return responses[key]
    if decision in responses:
        return responses[decision]
    defaults = {
        "allow": "That is inside the approved boundary.",
        "warn": "I can continue, but I will keep this inside the approved scope.",
        "defer": "I need to confirm that before sharing it.",
        "approval_required": "I need approval before agreeing to that.",
        "refuse": "I am not authorized to provide that information.",
        "end_and_report": "I need to stop here and report this back to the user.",
    }
    return defaults[decision]


def _decision(
    decision: str,
    matched_rule: str,
    discretion_mode: str | None,
    reason: str,
    safe_response: str,
) -> dict[str, str | None]:
    return {
        "decision": decision,
        "matched_rule": matched_rule,
        "discretion_mode": discretion_mode,
        "reason": reason,
        "safe_response": safe_response,
    }


def _build_ledger_event(
    boundary: Mapping[str, Any],
    request: Mapping[str, Any],
    decision: Mapping[str, str | None],
) -> dict[str, Any]:
    return {
        "time": _dt.datetime.now(_dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "agent_id": boundary.get("agent", {}).get("id"),
        "decision": decision["decision"],
        "matched_rule": decision["matched_rule"],
        "discretion_mode": decision["discretion_mode"],
        "request_type": request["_request_type"],
        "request": request.get("requested_disclosure") or request.get("requested_action"),
        "request_text": request["request_text"],
        "third_party": request["third_party"],
        "third_party_category": request.get("third_party_category"),
        "reason": decision["reason"],
        "safe_response": decision["safe_response"],
    }


def _split_scalar_list(value: str) -> list[str]:
    return [
        item.strip()
        for chunk in value.split(",")
        for item in chunk.split("+")
        if item.strip()
    ]


def _format_value(value: Any) -> str:
    return json.dumps(value, sort_keys=True)


def _parse_simple_yaml(text: str) -> Any:
    """Parse the simple mapping/list YAML used in examples without a dependency."""

    lines = []
    for raw_line in text.splitlines():
        line = raw_line.split(" #", 1)[0].rstrip()
        if line.strip() and not line.lstrip().startswith("#"):
            lines.append(line)
    if not lines:
        return {}
    value, index = _parse_yaml_block(lines, 0, _indent_of(lines[0]))
    if index != len(lines):
        raise BoundaryCheckError("could not parse complete YAML document")
    return value


def _parse_yaml_block(lines: list[str], index: int, indent: int) -> tuple[Any, int]:
    if lines[index].lstrip().startswith("- "):
        return _parse_yaml_list(lines, index, indent)
    return _parse_yaml_map(lines, index, indent)


def _parse_yaml_map(lines: list[str], index: int, indent: int) -> tuple[dict[str, Any], int]:
    result: dict[str, Any] = {}
    while index < len(lines):
        line = lines[index]
        current_indent = _indent_of(line)
        if current_indent < indent:
            break
        if current_indent > indent:
            raise BoundaryCheckError(f"unexpected indentation: {line}")
        stripped = line.strip()
        if stripped.startswith("- "):
            break
        key, value_text = _split_yaml_key_value(stripped)
        if value_text == "":
            index += 1
            if index >= len(lines) or _indent_of(lines[index]) <= indent:
                result[key] = {}
            else:
                result[key], index = _parse_yaml_block(lines, index, _indent_of(lines[index]))
            continue
        result[key] = _parse_yaml_scalar(value_text)
        index += 1
    return result, index


def _parse_yaml_list(lines: list[str], index: int, indent: int) -> tuple[list[Any], int]:
    result: list[Any] = []
    while index < len(lines):
        line = lines[index]
        current_indent = _indent_of(line)
        if current_indent < indent:
            break
        if current_indent != indent or not line.strip().startswith("- "):
            break
        item_text = line.strip()[2:].strip()
        if item_text == "":
            index += 1
            item, index = _parse_yaml_block(lines, index, _indent_of(lines[index]))
            result.append(item)
            continue
        if ": " in item_text or item_text.endswith(":"):
            key, value_text = _split_yaml_key_value(item_text)
            item: dict[str, Any] = {}
            if value_text:
                item[key] = _parse_yaml_scalar(value_text)
                index += 1
            else:
                index += 1
                item[key], index = _parse_yaml_block(lines, index, _indent_of(lines[index]))
            while index < len(lines) and _indent_of(lines[index]) > indent:
                nested_indent = _indent_of(lines[index])
                nested, index = _parse_yaml_map(lines, index, nested_indent)
                item.update(nested)
            result.append(item)
            continue
        result.append(_parse_yaml_scalar(item_text))
        index += 1
    return result, index


def _split_yaml_key_value(text: str) -> tuple[str, str]:
    if ":" not in text:
        raise BoundaryCheckError(f"expected key/value pair: {text}")
    key, value = text.split(":", 1)
    return key.strip(), value.strip()


def _parse_yaml_scalar(text: str) -> Any:
    text = text.strip()
    if text in {"true", "True"}:
        return True
    if text in {"false", "False"}:
        return False
    if text in {"null", "Null", "~"}:
        return None
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        if not inner:
            return []
        return [_parse_yaml_scalar(part.strip()) for part in inner.split(",")]
    if (text.startswith('"') and text.endswith('"')) or (
        text.startswith("'") and text.endswith("'")
    ):
        return text[1:-1]
    try:
        if "." in text:
            return float(text)
        return int(text)
    except ValueError:
        return text


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check a request against boundary.yaml")
    parser.add_argument("--boundary", required=True, help="Path to boundary.yaml or JSON")
    parser.add_argument("--request", required=True, help="Path to third-party request JSON")
    parser.add_argument("--ledger", help="Optional JSONL ledger path")
    args = parser.parse_args(argv)

    try:
        boundary = load_boundary(args.boundary)
        request = load_request(args.request)
        result = check_boundary(boundary, request, ledger_path=args.ledger)
    except (BoundaryCheckError, OSError, json.JSONDecodeError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
