# Product document system

Create a coherent set of four artifacts. Adapt the outlines; do not pad documents or overwrite project-specific value.

## Shared rules

- Separate current verified behavior from target design.
- Reuse one vocabulary for users, roles, entities, states, and boundaries.
- Preserve approved scope across all four documents.
- Label assumptions, hypotheses, planned capabilities, and unresolved decisions.
- Use Mermaid only when a relationship, sequence, state, or topology is materially clearer visually. API mapping is such a case: require the topology and business-flow sequences defined in [api-mapping.md](api-mapping.md).
- Verify every local link and never expose secrets or private URLs.

## README.md

Make the landing page impressive through clarity and evidence, not hype.

Recommended adaptive order:

1. Product name, audience, problem, and concrete outcome.
2. Visible current status and most important limitation.
3. Shortest verified first-success path, or "what exists / what is planned" for planning-only work.
4. Core product experience and differentiators.
5. Current or target architecture, explicitly labeled.
6. Capability status with evidence layer.
7. High-value development rules.
8. Existing documentation map.

Never infer runtime success from file existence, an old build log, or a diagram.

## docs/BRIEF.md

Keep the Product Brief concise and non-technical enough for product and engineering alignment:

1. Summary.
2. Context and observable problem.
3. Primary, secondary, collaborative, or administrative users.
4. Jobs-to-be-Done in situation -> progress -> outcome form.
5. Falsifiable product hypothesis.
6. Value proposition.
7. Core experience and user control over automation.
8. MVP boundary.
9. Five to eight product principles.
10. Explicit non-goals.
11. Journey diagram only if sequence is central.
12. Product-learning metrics separated from technical release gates.

The Brief owns intent and boundaries, not low-level implementation.

## docs/PRD.md

Translate approved intent into observable, testable behavior:

1. Header, status, release boundary, and source links.
2. Terms, roles, artifacts, scopes, and states.
3. Product behavior principles.
4. Roles and permission matrix.
5. Functional requirements grouped by domain with stable IDs such as `FR-AUTH-001`.
6. State transitions, triggers, authorization, persistence, failure, retry, ordering, idempotency, privacy, and deletion behavior.
7. Non-functional requirements with stable IDs.
8. Failure-behavior table.
9. Acceptance scenarios traceable to requirement IDs.
10. Non-gating analytics and explicit out-of-scope items.

A requirement must identify actor, precondition, behavior, observable result, persistence effect, authorization, and retry consequence when relevant. Avoid vague terms such as "appropriately" or "securely" without policy.

The PRD owns product behavior. It does not prescribe libraries, folder trees, indexes, or deployment topology unless they are product constraints.

When tracked capability specs are adopted, let PRD own product-wide scope, roles, release boundaries, and the stable requirement index. Link detailed accepted behavior to `openspec/specs/<capability>/spec.md`; do not maintain two diverging full copies. Proposed changes belong in `openspec/changes/<change-id>/` until accepted and applied.

## docs/ARCHITECTURE.md

Turn the PRD into implementable technical decisions:

1. Status, scope, architecture goals, and PRD link.
2. Principles, source of truth, dependency direction, and transaction boundaries.
3. System context and trust boundaries.
4. Deployment/container topology and resource envelope.
5. Component/module ownership before folder trees.
6. Workflow/orchestration, async work, retries, cancellation, and recovery.
7. Data architecture, ERD, ownership, indexes, deletion, and versioning.
8. REST, event, realtime, error, pagination, and idempotency contracts as applicable.
9. Specialized pipelines such as AI, RAG, media, payment, or notification when relevant.
10. Security, privacy, secret handling, log redaction, and abuse boundaries.
11. Capacity targets, verified benchmarks, deployment caps, and scale triggers.
12. Observability, migration, testing, deployment, and rollback strategy.
13. Dependency-ordered implementation path.

For a multi-developer project, also define local service ownership, host/container URL contexts, configuration generation, migration/startup order, and the canonical contributor lifecycle. Keep this operational design conditional; do not impose containers on a project that does not need them.

Architecture implements the PRD without expanding product scope. Label each component `current`, `partial`, `planned`, or `deprecated` where mixed states exist.

## Consistency gate

Before asking for approval, confirm:

- README status matches evidence.
- Every MVP item supports a Brief Job-to-be-Done.
- Every architecturally significant PRD requirement has an Architecture decision.
- Architecture introduces no unapproved product behavior.
- Roles, states, entities, and terminology agree.
- Current and target capabilities cannot be confused.
- Acceptance scenarios can drive implementation tests.
- PRD requirement indexes, accepted capability specs, and active deltas agree without presenting proposals as current behavior.
