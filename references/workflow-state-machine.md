# Workflow state machine

Use a stage plus a separate status. A stage describes where delivery is; a status describes whether work can proceed.

## Stages

| Stage | Required outcome | Normal next stage | User gate |
|---|---|---|---|
| `DISCOVERY` | Repository mode, current truth, constraints, and evidence are known | `FRAMING`, `LOCAL_ONBOARDING`, or `SLICE_PLANNING` | Only unresolved high-impact choices |
| `FRAMING` | Idea is brainstormed and product decisions are sufficiently clear | `DOCS_REVIEW` | Product choices when needed |
| `DOCS_REVIEW` | README, Brief, PRD, and Architecture agree | `LOCAL_ONBOARDING` or `SLICE_PLANNING` | Explicit document/architecture approval |
| `LOCAL_ONBOARDING` | A contributor can reproduce the local environment through one canonical lifecycle and verify it | `SLICE_PLANNING` or the stage that was previously blocked | Only destructive local data actions or external resources |
| `SLICE_PLANNING` | One approved, traceable delivery slice with an accepted baseline and approved material delta is executable | `IMPLEMENTATION` | Product, spec, scope, or architecture expansion |
| `IMPLEMENTATION` | Code, migrations, and tests for the slice exist | `TECHNICAL_VERIFICATION` | Destructive/local-environment ambiguity only |
| `TECHNICAL_VERIFICATION` | Required local technical gates have recorded evidence | `MANUAL_ACCEPTANCE` | No, unless blocked |
| `MANUAL_ACCEPTANCE` | User accepts behavior or requests changes | `CICD_DECISION` or earlier affected stage | Explicit user acceptance |
| `CICD_DECISION` | User chooses whether CI/CD work is needed now | `CICD_READINESS` or `COMMIT_READY` | Explicit CI/CD approval |
| `CICD_READINESS` | Approved CI/CD and release-readiness gates are configured and verified | `COMMIT_READY` | External release actions remain separate |
| `COMMIT_READY` | Scope, evidence, risks, and exact commit set are ready | `PAUSED` or next `SLICE_PLANNING` | Commit remains user-owned by default |

## Status values

- `ACTIVE`: work can continue inside current authority.
- `WAITING_FOR_USER`: a genuine decision gate is pending.
- `BLOCKED`: a required dependency, permission, environment, or external fact prevents reliable progress.
- `PAUSED`: state is safely persisted for later continuation.
- `COMPLETE`: the agreed project or milestone outcome is complete.

## Transition rules

1. Enter `DOCS_REVIEW` only when the four product artifacts exist or an existing equivalent is identified.
2. Do not enter `IMPLEMENTATION` without approved target behavior and architecture for the slice.
3. Enter `LOCAL_ONBOARDING` only for an explicit onboarding request, an approved multi-developer architecture, a contributor handoff, or measured environment drift. Do not force it on every project.
4. Exit `LOCAL_ONBOARDING` only after the canonical lifecycle, ignored configuration contract, contributor guide, and applicable static/runtime checks are evidenced or honestly blocked.
5. A user request to change accepted behavior returns to `FRAMING`, `DOCS_REVIEW`, or `SLICE_PLANNING` according to impact.
6. A test failure returns to `IMPLEMENTATION`; update documents only if the intended behavior changes.
7. `MANUAL_ACCEPTANCE` can begin with some unavailable environment layers only when they are explicitly `BLOCKED` or `N/A`, the limitation is visible, and the user can still evaluate the intended local behavior safely.
8. Local onboarding authority and CI/CD authority never imply permission to delete data/volumes or change external/production resources.
9. CI/CD approval permits pipeline/configuration work, not commit, push, deploy, production migration, or secret mutation.
10. "Continue" follows the next transition only when the prior gate is evidenced and the next stage is already authorized.
11. When evidence and state disagree, move backward to the earliest uncertain stage and repair the state.
12. Do not exit `SLICE_PLANNING` for a repair until the symptom, owning invariant, root-cause evidence, impact map, and protected behavior are explicit.
13. For an API-backed slice, do not exit `IMPLEMENTATION` until `docs/API_MAPPING.md`, `docs/api-map.json`, authoritative operations, real consumers, API topology, and required Mermaid sequences agree structurally; runtime and E2E remain separate technical gates.
14. For a material behavior change, do not enter `IMPLEMENTATION` until every artifact transitively required by the active OpenSpec apply graph is ready and approved. Under default `spec-driven`, this normally closes over proposal, delta specs, conditional design, and tasks. A repair that restores accepted behavior may link the baseline without a fake delta; skip specs only when the schema explicitly reports that state.
15. After manual acceptance, intelligently sync and verify the delivered delta against accepted capability specs, then archive the complete change before `COMMIT_READY`. Never classify rejected, incomplete, unsynced, or contradicted work as complete even if the OpenSpec archive operation allows a warned override.

## Approval recording

Record approvals as concise facts with time and scope, for example:

```yaml
approvals:
  product_docs:
    status: approved
    scope: auth-profile-v1
    recorded_at: 2026-08-01T10:00:00Z
  cicd:
    status: pending
```

Do not record inferred approval for commit, push, deploy, production migration, destructive data work, or secret changes.
