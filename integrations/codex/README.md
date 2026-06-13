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

Install is a two-step Codex flow: add the marketplace source, then install the plugin.

1. From a terminal, add the marketplace:

```bash
codex plugin marketplace add dhivyabuilds/Agent-Safety-Boundary-Kit
```

2. Open Codex Plugins.

3. Find **Agent Safety Boundary Kit**.

4. Install and enable the plugin.

5. Start a new Codex chat in the agent project you are building.

`@Agent Safety Boundary Kit` resolves only after the plugin is installed and enabled. Adding the marketplace source alone is not enough.

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

1. Add the marketplace source.
2. Install and enable the plugin in Codex.
3. Start a new chat in an agent repo.
4. Invoke **Agent Safety Boundary Kit**.
5. Answer a short boundary-design interview.
6. Confirm the draft boundary.
7. Let Codex write `.agent-boundary/`.
8. Review sample `boundary-check` results.
9. Wire the checker into the agent before sensitive disclosures, costs, commitments, identity checks, account changes, or scope expansion.
