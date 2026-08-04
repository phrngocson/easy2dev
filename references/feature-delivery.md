# Feature delivery

Deliver one traceable, reviewable slice at a time. Adapt the sequence to the detected architecture and requirement; do not force backend, database, frontend, AI, or infrastructure work when it is not needed.

Before editing, apply [change-safety.md](change-safety.md) and [spec-driven-development.md](spec-driven-development.md). For any API, event, WebSocket, webhook, or downstream consumer in scope, first open `docs/API_MAPPING.md` and `docs/api-map.json`, then apply [api-mapping.md](api-mapping.md). Create or reconstruct missing contracts before authorized work.

## 1. Slice contract

Before editing, record:

- stable feature ID and requirement IDs;
- user-visible outcome and non-goals;
- actors, permissions, tenant or ownership scope;
- entities, states, transitions, and invariants;
- success, validation, failure, retry, and recovery behavior;
- affected public contracts and compatibility needs;
- acceptance scenarios and required evidence layers.
- accepted capability requirement and active OpenSpec change/artifact graph with the applicable delta, or an explicit schema-backed skip/no-accepted-behavior-change statement.

If the requested behavior is absent from or conflicts with the approved PRD, return to the document gate instead of silently inventing a rule.

## 2. Change map

Map the slice to existing boundaries:

- data/schema and migration;
- domain model and persistence boundary;
- business service and authorization policy;
- transport/API/event contract;
- background worker or external integration;
- consumer/frontend/mobile/IoT integration;
- tests, observability, documentation, and CI.

For a public transport boundary, add the authoritative operation identity, source/runtime parity, real client wrappers, consumer entrypoints, API topology, and business-flow sequences. Mapping is part of the change contract, not documentation cleanup after implementation.

Prefer the existing module shape. Change architecture only when the current shape cannot satisfy the approved requirement safely or maintainably.

## 3. Database and migration path

When schema changes are required:

1. Establish ownership, cardinality, constraints, lifecycle, retention, and query needs.
2. Update the domain model.
3. Create one reviewable, versioned migration for the slice.
4. Inspect the migration graph and generated operations.
5. Identify destructive operations, table rewrites, locks, compatibility windows, and backfill behavior.
6. Prefer expand -> migrate -> switch -> contract when old and new application versions may overlap.
7. Run only against a verified local/test target under current authority.
8. Never modify production directly or assume downgrade is a safe recovery plan.

## 4. Implementation path

- Fix the module that owns the broken invariant; do not distribute symptom patches across callers.
- Keep transport handlers thin and business rules inside the owning domain boundary.
- Derive identity and authorization from trusted server context, not client-supplied ownership identifiers.
- Make mutation idempotency, ordering, concurrency, and retry behavior explicit where relevant.
- Bound external calls with timeouts and observable failure behavior.
- Preserve sensitive-data and tenant boundaries in logs, caches, events, AI context, and errors.
- Avoid broad refactors, new infrastructure, or speculative abstractions outside the slice.
- Keep public contracts stable or version their intentional changes.
- Explain every changed file through the root-cause and impact map; stop and re-plan if the blast radius expands into an unapproved module, contract, schema, or product decision.

## 5. Test path

Create the smallest high-value tests first, then expand by risk:

1. domain/unit behavior;
2. authorization and cross-tenant negatives;
3. persistence and migration behavior;
4. API/event/contract behavior;
5. idempotency, ordering, retry, and recovery;
6. integration with real local boundaries;
7. consumer behavior and user journey;
8. load, concurrency, security, or failure injection when required.

Do not change a correct test merely to accept incorrect implementation. When requirements change, update the requirement, acceptance scenario, and test together.

## 6. Consumer integration

Integrate frontend or other consumers after the relevant contract is stable unless an approved prototype deliberately uses a temporary boundary.

- Use real documented contracts; do not invent routes or duplicate server-owned business behavior.
- Map each consumed operation by stable identity to its shared client wrapper and real entrypoints; update `docs/API_MAPPING.md` plus `docs/api-map.json` on every API or consumer change, then validate the map and Mermaid topology/sequence coverage.
- Keep identity, permissions, state transitions, financial calculations, and other domain rules server-owned unless Architecture explicitly assigns them elsewhere.
- Verify loading, empty, success, validation, conflict, retry, permission, and offline/reconnect states where relevant.
- Present business language and workflows rather than raw internal IDs or developer configuration.

## 7. Slice completion

A slice is ready for manual acceptance when:

- scope and requirement traceability are recorded;
- implementation and migration diffs are scoped;
- required automated gates ran or are honestly blocked;
- public contracts and documentation agree;
- README and status claims reflect the new current implementation state;
- runtime behavior is verified at the strongest locally available layer;
- known risks and manual test steps are visible.
- root-cause evidence, protected behavior, API mapping status, and diagram status are visible when applicable.
- CLI-reported or fallback artifact state agrees with delivered work, accepted specs are intelligently synced and verified after approval, and the change is classified complete only when its archive has no unresolved delivery contradiction.
