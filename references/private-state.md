# Private project state

Private state makes continuation deterministic without exposing the developer's agent workflow in the repository history.

## Location and exclusion

Use this project-local layout:

```text
.easy2dev/
|-- state.yaml
|-- journal.md
|-- decisions/
|-- features/
`-- evidence/
```

Add `/.easy2dev/` to Git's local exclude file at `.git/info/exclude`. Do not add it to tracked `.gitignore` unless the user explicitly prefers a public convention. The initialization script performs this safely and idempotently.

Prefer the standard-library initialization script when a Python interpreter already exists. If it cannot run, create the same directories, initial files, and local exclude entry with the agent's native file and Git tools. Do not install Python, create a virtual environment, invoke a package manager, or leave a tool cache solely to initialize private state.

## State schema

Keep `state.yaml` small and human-readable:

```yaml
schema_version: 2
mode: new
stage: DISCOVERY
status: ACTIVE
active_feature: null
active_change: null
approvals:
  product_docs:
    status: pending
    scope: null
    recorded_at: null
  manual_acceptance:
    status: pending
    scope: null
    recorded_at: null
  cicd:
    status: pending
    scope: null
    recorded_at: null
evidence_summary:
  local_onboarding: NOT_RUN
  spec_contract: NOT_RUN
  static: NOT_RUN
  unit: NOT_RUN
  integration: NOT_RUN
  build: NOT_RUN
  runtime: NOT_RUN
  migration: N_A
next_action: inspect repository and establish current truth
updated_at: null
```

Use uppercase evidence values: `PASS`, `FAIL`, `BLOCKED`, `NOT_RUN`, or `N_A`. Evidence details belong in a feature or evidence file, not in the state summary.

## Journal format

Put the newest entry first:

```markdown
## 2026-08-01T10:00:00Z | DOCS_REVIEW -> SLICE_PLANNING

- Scope: auth-profile-v1
- Decision: Product documents approved.
- Evidence: docs/PRD.md FR-AUTH-001..005; docs/ARCHITECTURE.md section 6
- Result: Next slice may enter planning.
- Next: Map requirements to data and API contracts.

==========
```

Keep entries factual. Do not store internal reasoning transcripts. Do not copy the public proposal, delta, PROJECTSTATUS, or BUILDLOG into this private journal.

## Feature record

Create `.easy2dev/features/<stable-feature-id>.md` for the active slice with:

- requirement IDs and approved outcome;
- affected components and contracts;
- plan and migration notes;
- changed-file list;
- acceptance scenarios;
- evidence pointers and statuses;
- manual acceptance result;
- remaining risks and next action;
- public `openspec/changes/<change-id>/` pointer and accepted capability links when applicable.

Store only identifiers, approvals, current stage, and evidence pointers needed to resume. Public tracked specs and project records remain the shareable source.

## Decision record

Create a short file under `decisions/` only for durable product or architecture choices. Include context, chosen option, alternatives considered, consequence, approval source, and affected documents. Do not create a decision file for routine implementation details.

## Evidence record

Store concise command, environment, timestamp, exit status, and relevant summary. Prefer pointers to repository-native reports over copied full logs. Never store:

- credentials, tokens, connection strings, cookies, private keys, or secret values;
- personal profiles or account identifiers unnecessary for delivery;
- raw private prompts, conversation transcripts, or hidden chain-of-thought;
- full production data or sensitive request/response payloads.

## Reconciliation

On resume:

1. Compare the state with Git, documents, code, migrations, tests, and workflows.
2. Downgrade stale `PASS` claims when their artifact, source identity, or environment no longer matches.
3. Repair stage and next action.
4. Add a journal entry describing the correction.
5. Continue from the earliest uncertain required gate.
