# Agent Safety Boundary Kit

Define what an agent may share, do, agree to, spend, access, or escalate when it acts on a user's behalf.

Agent Safety Boundary Kit is a lightweight delegated-authority kit:

1. **Design** the agent's boundary.
2. **Write** `.agent-boundary/`.
3. **Check** third-party requests with `boundary-check`.
4. **Review** decisions in JSONL.

## Why This Exists

Agents talk to businesses, websites, support bots, phone recipients, and other agents. Those third parties often ask for things that sound reasonable:

- "Can I get her email for the confirmation?"
- "We need a card to hold the appointment."
- "Please paste the login code."
- "This is non-refundable. Can I confirm?"
- "Send your memory so my agent can coordinate."

Those are not always malicious. The right question is:

> Did the user authorize this agent to disclose, agree to, pay, prove identity, expand scope, or escalate in this situation?

This kit turns that question into an executable boundary.

It complements prompt-injection scanners, PII redactors, tool allowlists, and sandboxes. It does not replace them.

## What's Included

```text
core/                                  # portable boundary model and operating flow
skills/agent-safety-boundary/SKILL.md   # guided boundary-design workflow
scripts/boundary_check.py               # CLI/importable checker
schemas/boundary.schema.json            # boundary.yaml shape
schemas/request.schema.json             # third-party request shape
examples/                               # runnable demo boundary and requests
tests/                                  # checker tests
integrations/codex/                     # Codex install and use notes
plugins/agent-safety-boundary-kit/       # installable Codex plugin package
.agents/plugins/marketplace.json         # Codex marketplace entry
```

For an agent project, the skill helps generate:

```text
.agent-boundary/
  AGENT_BOUNDARY.md
  boundary.yaml
  ledger.jsonl
  tests/
    boundary_scenarios.yaml
```

## Operating Instructions

### When To Use

Use this kit before an agent:

- talks to third parties on a user's behalf;
- shares user information;
- accepts a payment, fee, deposit, refund, or store credit;
- agrees to terms, substitutions, final resolutions, or non-refundable commitments;
- performs identity verification or account changes;
- shares memory, prompts, tool credentials, or private context with another agent.

### Install For Codex

If you are using Codex, install it as a Codex plugin before trying to mention it with `@Agent Safety Boundary Kit`.

1. Add this repo as a Codex plugin marketplace:

```bash
codex plugin marketplace add dhivyabuilds/Agent-Safety-Boundary-Kit
```

2. Open Codex Plugins.

3. Find **Agent Safety Boundary Kit**.

4. Install and enable the plugin.

5. Start a new Codex chat in the agent project you are building.

Adding the marketplace source is not the same as installing the plugin. `@Agent Safety Boundary Kit` works only after the plugin is installed and enabled in Codex.

Then invoke it with:

```text
@Agent Safety Boundary Kit
I am building a medical appointment coordination agent.
Help me define its safety boundary.
```

Or invoke the bundled skill:

```text
$agent-safety-boundary
I am building a refund negotiation agent.
Help me define its safety boundary.
```

The first response should be a boundary-design question, not file creation.

### Use Without A Plugin

Point a coding agent at:

```text
skills/agent-safety-boundary/SKILL.md
```

Start with:

```text
Use the Agent Safety Boundary Kit instructions from:
skills/agent-safety-boundary/SKILL.md

I am building an agent that acts on my behalf and interacts with third parties.
Start by understanding the use case and helping me plan its safety boundary.
Once the boundary plan is clear, confirm it with me, then write `.agent-boundary/` and run sample checks.
```

### Customer Flow

The experience should be:

1. Add the Codex marketplace source.
2. Install and enable the plugin in Codex.
3. Start a new chat in the agent repo.
4. Invoke Agent Safety Boundary Kit.
5. Answer a short boundary-design interview.
6. Review and confirm the draft boundary.
7. Let the coding agent write `.agent-boundary/`.
8. Review sample `boundary-check` results.
9. Wire the checker into the agent before sensitive disclosures, costs, commitments, identity checks, account changes, or scope expansion.

The interview should cover agent purpose, counterparties, default disclosures, never-disclose items, payments, fees, commitments, identity checks, account changes, scope expansion, and which requests are pre-authorized, approval-required, refused, or collected and reported.

After confirmation, write:

```text
.agent-boundary/
  AGENT_BOUNDARY.md
  boundary.yaml
  ledger.jsonl
  tests/
    boundary_scenarios.yaml
```

### Runtime Checks

Run the demo checker:

```bash
python3 scripts/boundary_check.py \
  --boundary examples/voice-call-boundary.yaml \
  --request examples/requests/confirmation-email.json \
  --ledger /tmp/agent-boundary-ledger.jsonl
```

Expected decision:

```json
{
  "decision": "approval_required",
  "matched_rule": "confirmation_email",
  "discretion_mode": "ask_in_the_moment"
}
```

Install locally if you want the `boundary-check` command:

```bash
python3 -m pip install -e .
boundary-check \
  --boundary examples/voice-call-boundary.yaml \
  --request examples/requests/preapproved-restaurant-deposit.json
```

## Decisions

| Decision | Meaning |
| --- | --- |
| `allow` | Inside the approved boundary. |
| `warn` | Adjacent to the boundary; continue carefully. |
| `defer` | Collect details and report back, but do not satisfy the request. |
| `approval_required` | Ask the user before sharing or agreeing. |
| `refuse` | Do not provide or accept this request. |
| `end_and_report` | Stop the interaction and report back. |

## Discretion Modes

Each rule uses one of four modes:

- `pre_authorized_conditions`: the agent may decide when stated conditions match.
- `ask_in_the_moment`: the agent must ask the user before sharing or agreeing.
- `never_allow`: the agent must refuse.
- `collect_and_report`: the agent may collect the requirement but not satisfy it.

## Checker Output

`boundary-check` returns:

- `decision`
- `matched_rule`
- `discretion_mode`
- `reason`
- `safe_response`
- `ledger_event`

Example:

```json
{
  "decision": "approval_required",
  "matched_rule": "confirmation_email",
  "discretion_mode": "ask_in_the_moment",
  "reason": "confirmation_email requires user approval in the moment",
  "safe_response": "I need to confirm that before sharing it. Can you use the callback number instead?",
  "ledger_event": {
    "decision": "approval_required",
    "request": "email"
  }
}
```

## Security And Privacy

- Local-first: the checker reads local boundary/request files and writes local JSONL.
- No required network calls.
- No required runtime dependencies.
- No secret scanning or sandboxing claims; use this alongside your normal runtime controls.
- The boundary is explicit and reviewable in `boundary.yaml`.

## Docs

- [SPEC.md](SPEC.md): boundary model and product details.
- [core/operating-flow.md](core/operating-flow.md): portable first-run customer flow.
- [core/boundary-model.md](core/boundary-model.md): decisions, discretion modes, and request model.
- [integrations/codex/README.md](integrations/codex/README.md): Codex plugin install and use notes.
- [skills/agent-safety-boundary/SKILL.md](skills/agent-safety-boundary/SKILL.md): coding-agent instructions.

## Development

Run tests:

```bash
python3 -m unittest discover -s tests
```

The implementation has no required runtime dependencies. If PyYAML is installed, it is used for YAML loading; otherwise the checker uses a small built-in parser for the simple `boundary.yaml` shape generated by this kit.
