# Boundary Model

A safety boundary defines what an agent may share, do, agree to, spend, access, or escalate when it acts on a user's behalf.

The core primitive is a discretion rule:

```text
For this category of request, under these circumstances, the agent may decide, must ask, must refuse, or may only collect and report.
```

## Decision Vocabulary

| Decision | Meaning |
| --- | --- |
| `allow` | Inside the approved boundary. |
| `warn` | Adjacent to the boundary; continue carefully. |
| `defer` | Collect details and report back, but do not satisfy the request. |
| `approval_required` | Ask the user before sharing or agreeing. |
| `refuse` | Do not provide or accept this request. |
| `end_and_report` | Stop the interaction and report back. |

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

## Boundary File Contents

`boundary.yaml` should capture:

- the user-authorized objective;
- default allowed disclosures;
- discretion rules for conditional disclosures, costs, commitments, and approvals;
- prohibited disclosures;
- actions that require approval;
- fallback behavior when a third party asks for something outside the boundary;
- safe response text;
- audit settings.

## Request Shape

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
