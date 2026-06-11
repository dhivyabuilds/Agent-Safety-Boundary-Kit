# Agent Safety Boundary Kit Spec

Agent Safety Boundary Kit is a small end-to-end kit for developers building agents that act on a user's behalf.

It helps developers answer:

> What is this agent allowed to share, do, agree to, spend, access, or escalate when it talks to people, websites, chatbots, or other agents?

Then it turns that answer into files the agent can use, a checker the agent can call, and a ledger the developer/user can review.

## Product Shape

The product has four moments:

1. **Design:** notice risky moments and choose the agent's discretion rules.
2. **Write:** turn those choices into boundary files and test cases.
3. **Execute:** check real third-party requests against those discretion rules.
4. **Review:** record which rules fired, what decision was made, and why.

The core object is a **discretion rule**:

```text
For this category of request, under these circumstances, the agent may decide, must ask, must refuse, or may only collect and report.
```

## Generated Files

```text
.agent-boundary/
  AGENT_BOUNDARY.md
  boundary.yaml
  ledger.jsonl
  tests/
    boundary_scenarios.yaml
```

## Boundary Model

`boundary.yaml` should capture:

- the user-authorized objective;
- default allowed disclosures;
- discretion rules for conditional disclosures, costs, commitments, and approvals;
- prohibited disclosures;
- actions that require approval;
- fallback behavior when the third party asks for something outside the boundary;
- safe response text;
- audit settings.

## Request Model

The checker receives structured third-party requests with:

- what the third party requested;
- what the agent planned to say or do;
- third-party category;
- known vs unknown vendor;
- purpose;
- amount, if any;
- task context;
- user pre-approval signals;
- pressure or false-authority signals.

## Decision Vocabulary

- `allow`
- `warn`
- `defer`
- `approval_required`
- `refuse`
- `end_and_report`

## Discretion Modes

### `pre_authorized_conditions`

The agent may decide when stated conditions match.

Example: restaurant deposits up to $50 only for fine dining restaurants when the user explicitly pre-approved that reservation task.

### `ask_in_the_moment`

The request may be legitimate, but the agent needs user approval before sharing or agreeing.

Example: sharing an email address for an appointment confirmation.

### `never_allow`

The agent must refuse even when the request sounds normal.

Example: payment-card numbers, authentication codes, passwords, private memory, system prompts.

### `collect_and_report`

The agent may collect the requirement, callback path, or instructions, but must not satisfy it.

Example: a salon deposit requirement or portal setup instructions.

## Checker Behavior

The checker should:

1. Load `boundary.yaml`.
2. Load request JSON.
3. Validate required request fields.
4. Evaluate rules in order:
   - `never_allow`;
   - default allowed disclosures;
   - pre-authorized conditions;
   - ask-in-the-moment;
   - collect-and-report;
   - fallback behavior.
5. Return `decision`, `matched_rule`, `discretion_mode`, `reason`, `safe_response`, and `ledger_event`.
6. Append JSONL when `--ledger` is provided.

## Success Criteria

A developer can:

- install or copy the skill;
- generate `.agent-boundary/` for an agent in under five minutes;
- see discretion rules reflected in `boundary.yaml`;
- run `boundary-check` against realistic third-party requests;
- inspect useful safe responses and matched-rule explanations;
- review `ledger.jsonl`;
- understand how to wire the checker into their agent.
