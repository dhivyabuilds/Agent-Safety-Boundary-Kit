# Agent Safety Boundary Kit Requirements

Date: 2026-06-10

## What Is This Product?

Agent Safety Boundary Kit is a small end-to-end kit for developers building agents that act on a user's behalf.

It helps developers answer:

> What is this agent allowed to share, do, agree to, spend, access, or escalate when it talks to people, websites, chatbots, or other agents?

Then it turns that answer into files the agent can use, a checker the agent can call, and a ledger the developer/user can review.

The product is intentionally small:

1. **A builder skill** that asks what agent you are building.
2. **A generated `.agent-boundary/` folder** that captures the agent's safety boundary.
3. **A `boundary-check` script/library** that evaluates third-party requests.
4. **A local `ledger.jsonl`** that records boundary decisions.

This is the final concrete product shape, not a stepping stone to a giant platform.

The product has four moments:

1. **Design:** notice risky moments and choose the agent's discretion rules.
2. **Write:** turn those choices into boundary files and test cases.
3. **Execute:** check real third-party requests against those discretion rules.
4. **Review:** record which rules fired, what decision was made, and why.

The core object is a **discretion rule**:

> For this category of request, under these circumstances, the agent may decide, must ask, must refuse, or may only collect and report.

Discretion rules are what make the kit useful. They prevent the product from becoming a blunt allowed/blocked list.

## Why It Exists

Agents are increasingly doing things for users: booking appointments, starting returns, talking to businesses, browsing logged-in websites, and coordinating with other agents.

Basic safety tools protect the runtime:

- prompt-injection detection;
- PII redaction;
- content moderation;
- tool allowlists;
- sandboxing;
- human approval for risky tool calls.

Agent Safety Boundary Kit protects the delegation relationship.

It asks:

- Did the user authorize this disclosure?
- Did the user authorize this cost or commitment?
- Under what circumstances is this normally okay?
- Did the agent stay inside the intended task?
- Did a third party ask for more authority in an innocent-sounding way?
- Is there a record of what happened?

Example:

> A voice-call agent calls a salon to book an appointment. The salon asks for an email address, a credit card for a deposit, or a home address. Those requests may sound normal and may not look like prompt injection. Agent Safety Boundary Kit helps the agent decide whether to share, defer, ask approval, refuse, or end/report.

## Value Proposition

The product is useful because most builders know their agent's job, but have not clearly written down its authority.

Agent Safety Boundary Kit turns fuzzy intent into a working safety boundary:

- from "book appointments for me" to "may share first name, last initial, approved availability, and callback number";
- from "start returns for me" to "may collect options, but needs approval for fees, final commitments, or identity verification";
- from "talk to other agents" to "may share task summary, but never memory, credentials, system prompts, or broad private context";
- from "never give payment details" to "allow a deposit only when the vendor type, amount, and explicit user approval match";
- from "be careful" to concrete checks, safe language, and audit events.

The product should feel like a short safety planning session that leaves behind working artifacts the agent can actually use.

The product should not collapse everything into allowed/not allowed. Many real permissions are conditional. A neighborhood nail salon asking for a credit card deposit should probably be refused or escalated. An established fine dining restaurant asking for a pre-approved $50 reservation deposit may be allowed. The boundary needs to capture those circumstances.

## Short Pitch

> Agent Safety Boundary Kit helps developers plan, execute, and audit what an agent is allowed to share or do on a user's behalf.

More concrete:

> Tell Agent Safety Boundary Kit what you are building. It writes a safety boundary into your agent project, checks third-party requests against that boundary, and records the decisions.

## What Gets Installed

Agent Safety Boundary Kit is distributed as an OpenClaw-friendly project that can be copied or installed into an agent repo.

It contains:

```text
skills/agent-safety-boundary/SKILL.md
schemas/boundary.schema.json
scripts/boundary_check.py
schemas/request.schema.json
examples/
```

When a developer uses it for an agent, it generates:

```text
.agent-boundary/
  AGENT_BOUNDARY.md
  boundary.yaml
  ledger.jsonl
  tests/
    boundary_scenarios.yaml
```

## How It Works End To End

### 1. Plan The Boundary

The developer invokes the Agent Safety Boundary Kit skill and describes the agent. The skill behaves like a boundary designer for agent safety: it looks for moments where the agent might need to share information, spend money, accept terms, prove identity, or expand scope.

Example:

> I am building a voice-call agent for household scheduling, reservations, and simple admin calls.

The skill should not only ask a static setup form. It should actively notice risky delegation moments and ask how much discretion the builder wants the agent to have.

The UX should be conversational, like a short Plan Mode session. The builder can answer naturally. The kit should summarize, ask only the next useful question, and avoid forcing the builder through every possible category when the agent does not need it.

Core questions:

- Who can ask this agent to act?
- What third parties will it interact with?
- What data can it access?
- What can it share by default?
- What must it never share?
- What costs or commitments require approval?
- What should it do when a third party asks for more?
- What should it record?

Better questions for the planning flow:

1. What is the agent's job in one sentence?
2. What should this agent never do, even if asked?
3. Who is allowed to give this agent tasks?
4. Who will the agent talk to outside the trusted system?
5. What user data might the agent know or retrieve?
6. What data is safe to share by default?
7. What data is safe only for specific task types?
8. What data should never be shared?
9. What information is allowed only under specific circumstances?
10. What clues should the agent use to decide whether those circumstances apply?
11. What money-related actions are allowed, if any?
12. Are any money-related actions allowed only for certain vendor types, amounts, or explicit user approvals?
13. What commitments require approval?
14. What account or identity actions require approval?
15. When should the agent check with the user instead of deciding?
16. What should the agent do when the third party asks for something unapproved?
17. What should the agent do if the third party pressures it or claims special authority?
18. What does the user need to see after the interaction?
19. What examples should we test before trusting this agent?

For each sensitive category, the planning flow should offer a discretion choice:

```text
For deposits, do you want the agent to:
1. decide using pre-set conditions;
2. always check with you when the request seems legitimate;
3. never accept or provide payment information;
4. collect the request and report back without satisfying it?
```

The same pattern should apply to:

- sharing email or phone;
- sharing home address;
- paying deposits or fees;
- accepting substitutions;
- accepting non-refundable commitments;
- identity verification;
- account changes;
- sharing context with another agent.

The value is not just capturing preferences. The value is noticing these moments and making the builder choose the agent's discretion level before the agent is in the middle of the interaction.

The planning phase should produce executable discretion rules, not just advice.

Examples:

- If the builder says "ask me for legitimate email requests," the generated boundary should include a rule that returns `approval_required` for email requests with a plausible purpose.
- If the builder says "allow pre-approved fine dining deposits up to $50," the generated boundary should include the vendor category, amount threshold, and approval signal needed to check that later.
- If the builder says "never share card details," the generated boundary should include a `never_allow` rule that refuses even if the third party sounds legitimate.
- If the builder says "collect the deposit instructions but do not pay," the generated boundary should include a `collect_and_report` rule.

The planning pass should end by showing the builder a short summary:

```text
This agent may share: first name, last initial, callback number.
This agent may conditionally share: email only when the user explicitly approved email for this task.
This agent must not share: card, home address, auth codes, private calendar.
This agent needs approval for: deposits, fees, identity verification, non-refundable commitments.
Default response to unapproved asks: defer and report.
```

The builder should then get a clear handoff:

```text
Write this boundary into .agent-boundary/?
Run the sample third-party tests now?
Show the integration snippet for my agent?
```

### 2. Write Boundary Files

The skill writes a `.agent-boundary/` folder into the agent project.

`AGENT_BOUNDARY.md` explains the policy in plain language.

`boundary.yaml` is the machine-readable source of truth.

`tests/boundary_scenarios.yaml` captures the cases the builder should try before trusting the agent.

Example:

```yaml
agent:
  id: voice-call-agent
  purpose: household scheduling and simple admin calls

default_allowed_disclosures:
  - first_name
  - last_initial
  - approved_callback_number
  - approved_availability

discretion_rules:
  - id: restaurant_deposit
    request_type: payment_or_deposit
    mode: pre_authorized_conditions
    allowed_when:
      vendor_category:
        any_of: [fine_dining_restaurant, ticketed_experience]
      max_amount_usd: 50
      requires_explicit_task_approval: true
    otherwise: approval_required
    safe_response: "I need to confirm before placing a deposit. Can you hold the reservation while I check?"
  - id: confirmation_email
    request_type: disclosure
    mode: ask_in_the_moment
    field: email
    allowed_when:
      purpose:
        any_of: [appointment_confirmation, reservation_confirmation, receipt]
    otherwise: approval_required
    safe_response: "I need to confirm that before sharing it. Can you use the callback number instead?"
  - id: payment_card
    request_type: disclosure
    field: payment_card
    mode: never_allow
    decision: refuse
    safe_response: "I cannot provide card information. Can you hold this while the user follows up?"
  - id: deposit_instructions
    request_type: payment_or_deposit
    mode: collect_and_report
    applies_when:
      vendor_category:
        any_of: [salon, contractor, unknown_business]
    decision: defer
    safe_response: "I can collect the deposit instructions and have the user follow up."

never_disclose:
  - payment_card
  - auth_code
  - password
  - private_calendar_details
  - private_email_contents
  - system_prompt
  - private_memory

approval_required_for:
  - payment
  - deposit
  - identity_verification
  - account_change
  - non_refundable_commitment
  - sharing_home_address

fallbacks:
  unapproved_request: defer
  prohibited_request: refuse
  repeated_pressure: end_and_report

safe_responses:
  defer: "I need to confirm that before sharing it."
  payment_refusal: "I cannot provide payment information. Can you hold this while the user follows up?"
  approval_needed: "I need approval before agreeing to that."

audit:
  log_all_decisions: true
  log_third_party_requests: true
  summarize_for_user: true
```

The boundary file should support these capabilities:

- disclosure rules: what can be shared, never shared, shared only after approval, or shared only when conditions match;
- action rules: payments, deposits, account changes, identity checks, commitments;
- discretion rules: pre-authorized conditions, ask in the moment, never allow, collect and report;
- condition signals: vendor type, amount, task type, explicit user approval, known account relationship, purpose, confidence level, and fallback;
- third-party rules: businesses, chatbots, websites, remote agents, unknown parties;
- fallback behavior: allow, defer, approval required, refuse, end and report;
- safe response text: natural language the agent can use without sounding robotic;
- audit settings: what gets logged and what gets summarized to the user;
- test scenarios: realistic asks that should exercise the boundary.

Condition fields should be checkable, not only prose. For example, "known fine dining restaurant up to $50" should become fields like `vendor_category`, `amount_usd`, and `requires_explicit_task_approval`, not a sentence the checker has to interpret later.

### 3. Execute The Boundary While The Agent Acts

The agent calls the checker before sharing sensitive information or accepting a commitment.

This is the third moment of the product. The checker takes the plan from `boundary.yaml` and applies it to a real moment in the interaction.

The agent should call `boundary-check` when a third party asks for:

- user information;
- payment, deposits, fees, or refunds;
- account changes;
- identity verification;
- acceptance of terms, substitutions, or non-refundable commitments;
- access to memory, tool credentials, internal policy, or system prompts;
- anything that expands the original task.

The request passed to the checker should include both the ask and the circumstances the agent knows.

Useful circumstances:

- third-party category;
- known vs unknown vendor;
- requested amount;
- stated purpose;
- current task;
- whether the user pre-approved this type of action;
- confidence in the third-party category;
- whether the third party is applying pressure or claiming special authority.

CLI shape:

```bash
boundary-check \
  --boundary .agent-boundary/boundary.yaml \
  --request third_party_request.json \
  --ledger .agent-boundary/ledger.jsonl
```

Library shape:

```python
decision = check_boundary(
    boundary=boundary,
    request=third_party_request,
    proposed_response=proposed_response,
)
```

Example request:

```json
{
  "channel": "voice_call",
  "third_party": "salon receptionist",
  "third_party_category": "neighborhood_nail_salon",
  "known_vendor": false,
  "purpose": "appointment_confirmation",
  "request_text": "Can I get her email for the confirmation?",
  "requested_disclosure": "email",
  "proposed_response": "Sure, her email is dhivya@example.com."
}
```

This request shape should be validated by `schemas/request.schema.json` so agent builders know exactly what their agent needs to pass into the checker.

Example output:

```json
{
  "decision": "approval_required",
  "matched_rule": "confirmation_email",
  "discretion_mode": "ask_in_the_moment",
  "reason": "email can be requested for appointment confirmation, but this boundary requires user approval before sharing it",
  "safe_response": "I need to confirm that before sharing it. Can you hold the appointment with the callback number instead?",
  "ledger_event": "written"
}
```

Decision vocabulary:

- `allow`
- `warn`
- `defer`
- `approval_required`
- `refuse`
- `end_and_report`

The checker should return three useful things:

- a decision;
- the matched discretion rule and reason the agent/developer can inspect;
- a safe response the agent can say or adapt.

### 4. Review The Boundary Decisions

Every check appends to `.agent-boundary/ledger.jsonl`.

Example:

```json
{"time":"2026-06-10T10:00:00Z","decision":"approval_required","matched_rule":"confirmation_email","discretion_mode":"ask_in_the_moment","request":"email","reason":"email requires approval for appointment confirmation","third_party":"salon receptionist"}
```

The ledger makes the interaction reviewable. It answers:

- What did the third party ask for?
- What did the agent share or refuse?
- What needed approval?
- Which discretion rule fired?
- Which condition matched or failed?
- Did the agent stay inside the boundary?

This is the fourth moment of the product. The ledger is not just logging for logging's sake. It is how the user/developer sees whether the agent respected the safety boundary and where the boundary needs to be improved.

## What The Checker Does

The checker is intentionally simple.

It compares a structured third-party request against `boundary.yaml` and returns a decision plus a safe response template.

The checker should prioritize the builder's declared boundary over the model's instinct to be helpful. A third-party request can sound innocent and still exceed the user's authorization.

It should handle:

- requested disclosures;
- conditional disclosures;
- requested commitments;
- requested payments/deposits;
- conditional payments/deposits;
- identity verification;
- account changes;
- requests for private memory or system prompts;
- attempts to expand scope;
- repeated pressure or false authority claims.

It does not try to replace all safety systems. It does not decide whether content is generally malicious. It decides whether the request is authorized by this agent's boundary.

For this concrete version, the checker can require structured request fields. Light natural-language classification can be added only where it keeps the product easy to demo, such as extracting `requested_disclosure: email` from "Can I get her email?"

The checker should evaluate in this order:

1. `never_allow` rules;
2. exact pre-authorized condition matches;
3. ask-in-the-moment rules;
4. collect-and-report rules;
5. fallback behavior.

This ordering keeps hard prohibitions hard, while still preserving utility for legitimate conditional requests.

## Conditional Permissions

Conditional permissions are the key product feature, but the better implementation concept is **discretion rules**.

The checker should support four classes of rules:

1. **Allowed by default:** safe in normal use, such as first name or approved callback number.
2. **Allowed when conditions match:** safe only when context clues satisfy the boundary.
3. **Approval required:** plausible, but the agent should ask the user first.
4. **Never allowed:** prohibited even if the third party pressures the agent.

Example:

```yaml
discretion_rules:
  - id: deposit_for_high_trust_restaurant
    request_type: payment_or_deposit
    mode: pre_authorized_conditions
    allowed_when:
      vendor_category: fine_dining_restaurant
      amount_usd_lte: 50
      user_preapproved_deposits: true
    otherwise: approval_required

  - id: deposit_for_neighborhood_salon
    request_type: payment_or_deposit
    mode: collect_and_report
    decision: defer
```

The planning pass should ask developers for explicit clues:

- Which vendor categories are high trust?
- Which vendor categories are low trust?
- Are known vendors treated differently from unknown vendors?
- What amount thresholds matter?
- Does this require explicit per-task user approval?
- Is a user account relationship required?
- Should the agent ask one follow-up question before deciding?
- What confidence level is enough to proceed?
- What should be logged when a condition fails?

The checker should return a reason that cites the condition:

```json
{
  "decision": "approval_required",
  "reason": "deposit request did not match allowed conditions: vendor_category was neighborhood_nail_salon, not fine_dining_restaurant",
  "safe_response": "I need to confirm before placing a deposit. Can you hold the appointment while I check?"
}
```

This keeps the agent useful. It can say yes in the cases the builder intended, and pause in the cases that look similar but carry different risk.

## Discretion Modes

Conditional permissions should be generated from explicit discretion choices.

For each sensitive category, the boundary can use one of these modes:

### 1. Pre-Authorized Conditions

The builder lets the agent decide when conditions match.

Example:

> The agent may accept restaurant deposits up to $50 only for fine dining restaurants when the user explicitly asked for a reservation and pre-approved deposits for that task.

Checker behavior:

- `allow` when conditions match;
- `approval_required` or `refuse` when they do not.

### 2. Ask In The Moment

The builder wants the agent to recognize legitimate requests but check before sharing or agreeing.

Example:

> If a business asks for email for a plausible confirmation purpose, ask the user before sharing it.

Checker behavior:

- `approval_required` with a concise reason and proposed safe response.

### 3. Never Allow

The builder does not want the agent to do this, even when the request sounds legitimate.

Example:

> Never provide card numbers or authentication codes.

Checker behavior:

- `refuse` or `end_and_report`.

### 4. Collect And Report

The agent may gather the requirement but not satisfy it.

Example:

> If a business requires a deposit, collect the callback number and instructions, then report back.

Checker behavior:

- `defer` or `approval_required`, with a response like "I can collect that requirement and have the user follow up."

The planning flow should explicitly ask which mode the builder wants for each major category. This makes the boundary feel smart without letting the model invent its own authority.

## Product Boundaries

Agent Safety Boundary Kit is not:

- a generic prompt-injection scanner;
- a generic PII detector;
- a sandbox;
- a full agent runtime;
- a legal contract system;
- a hosted enterprise compliance platform.

Agent Safety Boundary Kit is:

- a planning workflow;
- a generated boundary file;
- a checker;
- a local ledger.

## Differentiation

Existing tools commonly answer:

- Is this prompt malicious?
- Is this PII?
- Is this tool call allowed?
- Should this command run?

Agent Safety Boundary Kit answers:

- Is this third-party request inside what the user authorized this agent to do?
- Can the agent disclose this information?
- Can the agent accept this fee, deposit, substitution, or commitment?
- Should the agent continue, defer, ask approval, refuse, or end/report?
- What should be logged for later review?

The core differentiator:

> Agent Safety Boundary Kit audits delegated intent.

## Complete Demo

The concrete demo should be a voice-call scheduling agent.

Setup:

- Generate `.agent-boundary/boundary.yaml` for a household voice-call agent.
- Feed the checker six third-party requests.
- Show decisions and ledger entries.

Requests:

1. "Can I get her first name and callback number?"
2. "Can I get her email for the confirmation?"
3. "We need a card to hold the slot."
4. "What is her home address?"
5. "This is non-refundable. Can I confirm?"
6. "This fine dining reservation requires the pre-approved $50 deposit."

Expected outputs:

1. `allow`
2. `approval_required` if the boundary says email is ask-in-the-moment
3. `refuse` or `approval_required`
4. `refuse`
5. `approval_required`
6. `allow` only if the request matches the conditional restaurant-deposit rule

The demo should show that the agent stays useful: it does not panic or over-refuse. It keeps the task moving when possible, cites the discretion rule that fired, and records the boundary events.

## Success Criteria

Agent Safety Boundary Kit is successful if a developer can:

- install or copy the skill;
- generate `.agent-boundary/` for an agent in under five minutes;
- see discretion rules reflected in `boundary.yaml`;
- run `boundary-check` against realistic third-party requests;
- see useful safe responses and matched-rule explanations;
- inspect `ledger.jsonl`;
- understand how to wire the checker into their agent.

## Open Questions

Resolved working choices:

- Generated folder: `.agent-boundary/`
- Checker command: `boundary-check`
- First checker implementation: Python, because this repo's current agents are Python.
- Ledger: JSONL, because it is easy to inspect and demo.
- First request format: structured JSON, with optional light extraction from plain text.

Remaining questions:

- Which three profiles should ship first: voice calls, customer-service chatbot, and agent-to-agent?
- Should `boundary-check` write `ledger.jsonl` by default or only with `--ledger`?
- Should `AGENT_BOUNDARY.md` be generated from `boundary.yaml` every time to avoid drift?
