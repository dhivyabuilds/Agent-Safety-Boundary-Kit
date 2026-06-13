# Codex Integration

Agent Safety Boundary Kit can be installed in Codex as a plugin.

The installable plugin package lives at:

```text
plugins/agent-safety-boundary-kit/
```

The marketplace entry lives at:

```text
.agents/plugins/marketplace.json
```

The plugin packages the Codex workflow and a checker launcher. The canonical checker remains at:

```text
scripts/boundary_check.py
```

## Install

From a terminal:

```bash
codex plugin marketplace add dhivyabuilds/Agent-Safety-Boundary-Kit
```

Then open Codex and install **Agent Safety Boundary Kit** from the plugin directory.

## Use

Open the agent project you are building and invoke the plugin or skill:

```text
@Agent Safety Boundary Kit
I am building a medical appointment coordination agent.
Help me define its safety boundary.
```

Or:

```text
$agent-safety-boundary
I am building a refund negotiation agent.
Help me define its safety boundary.
```

Expected first response:

```text
What is this agent allowed to do in one sentence, and which third parties will it interact with?
```

The skill should then interview you, summarize the proposed boundary, ask for confirmation, write `.agent-boundary/`, run sample checks, and suggest the smallest integration point.

## Customer Experience

1. Install the plugin.
2. Invoke **Agent Safety Boundary Kit** in an agent repo.
3. Answer a short boundary-design interview.
4. Confirm the draft boundary.
5. Let Codex write `.agent-boundary/`.
6. Review sample `boundary-check` results.
7. Wire the checker into the agent before sensitive disclosures, costs, commitments, identity checks, account changes, or scope expansion.
