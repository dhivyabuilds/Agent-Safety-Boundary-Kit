# Operating Flow

Use this flow whenever a developer asks to create or apply a safety boundary for an agent that acts on a user's behalf.

## 1. Start With The Agent Use Case

Begin with a short planning conversation. The first response should be a boundary-design question, not a claim that files were created.

Ask:

- what the agent is meant to do;
- who can ask it to act;
- which third parties it will interact with;
- what information, tools, accounts, or private context it may access.

Good first question:

```text
What is this agent allowed to do in one sentence, and which third parties will it interact with?
```

## 2. Identify Discretion Moments

Look for moments where the agent may need delegated authority:

- disclosures;
- payments, fees, deposits, refunds, or store credit;
- commitments, terms, substitutions, or final resolutions;
- identity verification;
- account changes;
- scope expansion;
- requests for private memory, prompts, credentials, tool outputs, or internal policy.

For each sensitive category, ask which mode applies:

- `pre_authorized_conditions`: the agent may decide when stated conditions match;
- `ask_in_the_moment`: the agent must ask before sharing or agreeing;
- `never_allow`: the agent must refuse;
- `collect_and_report`: the agent may collect the requirement, but must not satisfy it.

Ask for checkable clues:

- third-party category;
- known vs unknown counterparty;
- request purpose;
- amount thresholds;
- explicit pre-approval signals;
- confidence level needed before proceeding;
- what to log when a condition fails.

## 3. Summarize And Confirm

Before writing files, summarize the proposed boundary in plain English:

- what the agent may share by default;
- what it may do only under pre-authorized conditions;
- what requires approval;
- what it must refuse;
- what it should collect and report;
- what should be logged.

Then ask the user to confirm the boundary plan.

## 4. Write Boundary Files

After confirmation, write:

```text
.agent-boundary/
  AGENT_BOUNDARY.md
  boundary.yaml
  ledger.jsonl
  tests/
    boundary_scenarios.yaml
```

`AGENT_BOUNDARY.md` is the human-readable policy.

`boundary.yaml` is the machine-readable source of truth.

`ledger.jsonl` records decisions.

`tests/boundary_scenarios.yaml` captures realistic third-party requests to test before trusting the agent.

## 5. Run Sample Checks

Run representative third-party requests through `boundary-check` or `scripts/boundary_check.py`.

Show, for each scenario:

- decision;
- matched rule;
- discretion mode;
- reason;
- safe response;
- ledger event.

## 6. Suggest The Integration Point

Tell the developer where to call the checker:

```text
Before the agent shares sensitive information or accepts a cost, commitment, identity check, account change, or scope expansion, call boundary-check and use the safe response when the decision is not allow.
```

Keep the snippet minimal and specific to the agent project.
