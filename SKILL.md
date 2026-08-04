---
name: easy2dev
description: Operate an evidence-driven software delivery workflow from idea and architecture through tracked OpenSpec-style capability specs and ADDED/MODIFIED/REMOVED brownfield deltas, root-cause implementation, frontend capability and design resolution, reproducible onboarding, real API mapping, regression-safe verification, CI/CD, deployment readiness, and resumable handoff. Use when the user invokes $easy2dev; starts, adopts, or resumes a project; asks to brainstorm, specify, implement, repair, design a frontend, map APIs, test, optimize, ship, or continue a feature; needs spec-driven development, PROJECTSTATUS/BUILDLOG governance, locked dependencies, one-command dev.ps1, canonical ports, vm.ps1, Dev 2 handoff, or protection from environment drift; says "continue" or "làm tiếp"; or adopts an unfamiliar repository without relying on conversation memory or AGENTS.md.
---

# Easy2Dev

Turn an idea or repository into verified delivery slices while keeping the user at product, architecture, manual-acceptance, CI/CD, and release decision gates. Work from repository evidence and private project state, not agent memory.

## Start every invocation

1. Respond in the user's language and match their demonstrated technical level. Use that language as the default human-readable spec language unless the user explicitly selects another language or the repository already has an approved project language. Keep machine-required OpenSpec tokens, stable IDs, paths, code symbols, and protocol names canonical rather than translating them.
2. Read [operating-principles.md](references/operating-principles.md) and [workflow-state-machine.md](references/workflow-state-machine.md) completely.
3. Inspect before changing anything. Read [project-discovery.md](references/project-discovery.md) and follow it for new, existing, and unfamiliar repositories. Reconcile `openspec/config.yaml`, tracked baselines, active changes, and compatible CLI-reported schema/path state before treating product prose as current behavior.
4. Treat repository instruction files as optional constraints. Discover and obey them when present, but never require `AGENTS.md` or any agent-specific file for this skill to work.
5. Locate `.easy2dev/state.yaml`. If it is absent and the workspace is writable, initialize private state with `scripts/init_project_state.py`. For an empty project, allow the script to initialize Git. If no usable Python interpreter is already available, reproduce the documented state layout and Git-local exclusion with native repository tools; do not install a runtime or dependency merely to bootstrap state.
6. Reconcile private state against current repository evidence before choosing the next stage. Repository evidence wins for current implementation; approved product documents win for target behavior.
7. State the reconstructed stage, active scope, strongest evidence, and next action in a short update. Then act without asking for information that can be discovered locally.

## Apply stage-scoped authority

Interpret an explicit `$easy2dev` invocation as authorization to run the workflow, not as unlimited repository or infrastructure authority.

- **Bootstrap authority:** An invocation with an idea authorizes discovery, brainstorming, Git initialization for an empty folder, creation of `.easy2dev/`, and creation or reconciliation of README, Brief, PRD, Architecture, and initial tracked capability specs after their behavior is approved.
- **Local onboarding authority:** An explicit onboarding request, or approval of an Architecture that requires a reproducible team environment, authorizes scoped development scripts, local configuration contracts, ignored local env generation, dependency synchronization, local containers, local migrations, onboarding docs, and local verification. It never authorizes deleting local data/volumes or changing cloud and production resources.
- **Implementation authority:** Approval of the product documents and Architecture authorizes implementation, dependency changes, versioned migrations, tests, and local verification inside the approved slice.
- **Continuation authority:** "Continue", "làm tiếp", or an equivalent instruction authorizes the next non-destructive action in the already approved stage and scope.
- **CI/CD authority:** Manual acceptance does not authorize pipeline changes. Ask whether to prepare CI/CD. Approval authorizes relevant pipeline, build, migration-safety, and release-readiness work, but not publishing or production mutation.
- **External and destructive authority:** Require explicit authorization for commit, push, merge, tag, release, deploy, production migration, secret changes, destructive data operations, or rollback that changes an environment.

Do not fall back to asking approval for every file or command once a stage is authorized. Stop only for a genuine decision gate, expanded scope, destructive action, external side effect, missing authority, or blocker that cannot be resolved safely.

## Run the workflow

### 1. Discover or adopt

Determine whether the workspace is:

- `new`: empty or idea-only;
- `existing`: an owned project with implementation or documents;
- `foreign`: an unfamiliar project whose conventions must be preserved.

For `existing` and `foreign`, reconstruct current behavior, target intent, worktree state, canonical commands, contracts, migrations, OpenSpec config/schema, accepted specs, active changes, project records, and verification evidence. When a compatible OpenSpec CLI is callable, use its JSON-reported planning root, artifact graph, statuses, and concrete paths instead of assuming the default schema. Do not overwrite good existing documents merely to fit a template. For brownfield adoption, reconstruct capability specs incrementally from evidence rather than generating a fictional complete baseline.

When an API-backed flow exists, open `docs/API_MAPPING.md` and `docs/api-map.json`, then reconstruct source-versus-runtime contract parity, stable operation identities, real client wrappers, consumer entrypoints, and current diagram status. If the files are missing, create or reconstruct them before authorized API work; on a read-only invocation, report the missing gate instead. Do not trust a stale checked-in route list as runtime evidence.

When a frontend exists or is in scope, inspect its routes, component boundaries, design system, tokens, responsive behavior, accessibility conventions, user-visible states, and available frontend skills before proposing a visual direction. Preserve a coherent existing visual language unless an approved redesign changes it.

### 2. Frame the product

For a new or materially under-specified project:

1. Brainstorm from the user's idea.
2. Separate known facts, assumptions, open decisions, risks, and recommended defaults.
3. Ask only the smallest set of product choices that materially changes scope, users, data, trust boundaries, cost, or architecture.
4. Create or reconcile:
   - `README.md`;
   - `docs/BRIEF.md`;
   - `docs/PRD.md`;
   - `docs/ARCHITECTURE.md`.
5. Read [product-docs.md](references/product-docs.md) before drafting these artifacts.
6. Cross-check terminology, scope, current-versus-target status, requirements, architecture, and local links.
7. Keep PRD as the product-wide requirement index and release boundary; place accepted detailed capability behavior in tracked specs without duplicating it.
8. Present the decisions and unresolved trade-offs, then ask whether the user approves the documents and wants implementation to begin.

Do not claim planned capabilities are implemented. Do not let the Architecture add product behavior that the PRD has not approved.

### 3. Make local onboarding reproducible when needed

Enter `LOCAL_ONBOARDING` only when the user requests it, approved Architecture requires a multi-developer environment, a new contributor needs a supported first-run path, or environment drift blocks reliable development. Read [local-onboarding.md](references/local-onboarding.md) completely.

Then autonomously:

1. Map host, container-to-host, and service-to-service execution contexts.
2. Establish one canonical, idempotent `up`, `down`, and `status` entrypoint using repository-native tooling.
3. Generate ignored local configuration from authoritative local services where possible; never require copying secret values by hand.
4. Make lockfiles, service ownership, startup order, migrations, and health checks deterministic.
5. Enforce the dependency ledger and canonical port/script contract in [plug-and-play-lifecycle.md](references/plug-and-play-lifecycle.md) for Windows FastAPI/Next.js/Supabase projects or any project whose user adopts this profile.
6. Create or reconcile a direct contributor onboarding guide and link it from the README.
7. Run `scripts/validate_local_onboarding.py`, using strict profile flags when applicable, then verify first startup, repeated startup, migration state, tests/builds, health, and applicable auth/browser paths in separate evidence layers.

Skip this stage for a solo or library project whose existing local workflow is already reproducible. Local onboarding readiness does not imply CI/CD or production readiness.

### 4. Plan one delivery slice

After document approval, select the smallest coherent feature or repair that can be implemented and verified end to end. Read [feature-delivery.md](references/feature-delivery.md).

For each slice:

1. Trace it to approved requirement IDs or record the newly approved requirement.
2. Confirm actors, permissions, states, failure behavior, data ownership, public contracts, and acceptance scenarios.
3. Map the change to existing module boundaries and dependency direction.
4. Design schema and migration changes only when required.
5. Apply [change-safety.md](references/change-safety.md): reproduce the problem, state the owning invariant and root-cause evidence, map the blast radius, and protect out-of-scope behavior.
6. Apply [spec-driven-development.md](references/spec-driven-development.md). For a material behavior change, complete and approve every artifact transitively required for apply by the active OpenSpec schema. Under default `spec-driven`, this normally includes proposal, delta specs, conditional design, and tasks. Write baseline and delta spec prose in the resolved user/project language, declare it with the Easy2Dev spec-language marker, and preserve OpenSpec's machine-required structural tokens. A repair that restores accepted behavior links the baseline requirement without inventing a delta; honor spec skipping only when the schema or CLI explicitly reports it.
7. For an API-backed slice, open and reconcile `docs/API_MAPPING.md` plus `docs/api-map.json`, then apply [api-mapping.md](references/api-mapping.md): map authoritative operations to real consumers and prepare the topology plus sequence diagrams before integration.
8. For a frontend slice, read [frontend-delivery.md](references/frontend-delivery.md), resolve the frontend capability path, and record the applicable design intent and UI acceptance states before implementation.
9. Write a short executable plan and begin unless a product, spec, architecture, or material design decision remains unresolved.

### 5. Implement and verify

Implement within the approved slice and preserve unrelated work. Follow the approved capability baseline and active delta, repository conventions, and canonical tools instead of assuming a framework. Fix the owning cause, not only the visible symptom. The smallest coherent fix may cross several affected layers, but every changed file must be traceable to the invariant being restored. Never hide a failure by swallowing errors, weakening a correct test, creating a parallel source of truth, or broadly refactoring unrelated code.

Treat dependency declaration as part of implementation, not as a later setup task. Read [dependency-management.md](references/dependency-management.md); for Python also read [python-dependencies.md](references/python-dependencies.md). Use uv for new Python backends and npm for new JavaScript/TypeScript applications; preserve an existing manager long enough to validate it and request migration approval. Whenever a package is added, removed, upgraded, or found missing, update its owning manifest and lock in the same slice, synchronize from the lock, rebuild affected artifacts, and verify the consumer. A dependency installed only in the agent's current environment is an incomplete change.

When a database-backed API is involved, normally progress through:

`Requirement -> data design -> model -> migration -> persistence -> domain logic -> API contract -> API map -> Mermaid topology/sequence -> runtime verification -> consumer integration`

Adapt or skip steps that do not apply. Stabilize contracts before downstream integration unless an explicitly approved prototype requires otherwise. Use source and runtime OpenAPI as distinct evidence, map each operation by unique `operationId`, and never invent a consumer route. Treat `docs/API_MAPPING.md` as the mandatory human-facing map and `docs/api-map.json` as its machine-checkable ledger. Read and update both in the same slice whenever an API is added, changed, removed, deprecated, or connected to or disconnected from a frontend or other consumer. Run `scripts/validate_api_mapping.py` after any such change; use partial mode only during discovery.

For frontend work, apply the capability resolution and delivery contract in [frontend-delivery.md](references/frontend-delivery.md). Use the selected installed frontend skill when one is applicable. Make loading, empty, error, success, validation, permission, and recovery states intentional; verify responsive and accessibility behavior rather than treating a successful production build as frontend acceptance. Never replace a missing backend capability with a mock or frontend-owned business rule unless an approved prototype explicitly requires that boundary.

Create tests alongside behavior. Run the smallest relevant gate first, fix the root cause, then expand verification. Read [evidence-and-cicd.md](references/evidence-and-cicd.md) for evidence states and gate design.

Keep active change tasks synchronized with delivered work. When a compatible OpenSpec CLI is available, re-read `status --json` and `instructions apply --json`, use only its reported context files and paths, and run its schema-aware validation. Also run `scripts/validate_spec_contract.py --spec-language <resolved-bcp47-tag>` for the default `spec-driven` Easy2Dev gate whenever capability specs, proposals, deltas, PROJECTSTATUS, or BUILDLOG change. Do not install OpenSpec implicitly or treat project context/rules as completion evidence.

Use the repository's existing runtime and canonical commands. Do not initialize a package-manager environment or leave a cache merely to discover an interpreter or executable; locate an already installed runtime with read-only tools or mark the gate `BLOCKED`.

### 6. Hand off for manual acceptance

When automated technical gates for the slice are complete:

1. Reconcile README, status text, contracts, and other public documentation that the implementation made stale.
2. Summarize the user-visible behavior and exact scope.
3. Give a short manual test path and expected observations.
4. Identify edge cases worth exploring without constraining the user's own exploratory testing.
5. For API-backed work, report mapped operations, consumer entrypoints, diagram locations, source/runtime parity, and the strongest evidenced status of each flow.
6. For frontend work, report the applied design intent, responsive/accessibility evidence, covered UI states, and browser/manual visual acceptance separately from static checks and builds.
7. Report the active change ID, delta sections, baseline reconciliation status, and any spec drift.
8. Report every unverified layer honestly.
9. Wait for acceptance, rejection, or refinement.

If the user finds a problem, return to the smallest affected stage, update requirements when behavior changes, implement the fix, and rerun impacted gates.

After acceptance, assess and verify delta sync into the accepted main specs, reconcile PRD/Architecture/API Mapping, then archive through the compatible OpenSpec workflow or its resolved fallback path. Never claim completion for an incomplete or unsynced archive merely because the CLI allowed it. Update adopted project records only after evidence exists; read [project-records.md](references/project-records.md).

### 7. Prepare CI/CD only after approval

After manual acceptance, ask whether to prepare or improve CI/CD for the slice. If approved:

1. Inspect existing workflows and repository commands.
2. Add the smallest pipeline that represents real stack and risk.
3. Keep static, unit, integration, build, migration, runtime, and deployment evidence separate.
4. Verify reproducibility, artifact identity, secret handling, migration order, health checks, and rollback readiness where applicable.
5. For the adopted plug-and-play profile, enforce frozen dependency installation, the canonical port map, `scripts/dev.ps1`, and the authorized `scripts/vm.ps1` deployment contract from [plug-and-play-lifecycle.md](references/plug-and-play-lifecycle.md).
6. For API-backed applications, gate complete operation classification, real consumer paths, Mermaid mapping structure, and source/runtime contract parity separately from API behavior and E2E evidence.
7. Gate tracked spec structure and delta semantics with the schema-aware official OpenSpec validation when callable and with `scripts/validate_spec_contract.py` for the default `spec-driven` Easy2Dev profile. Treat a custom schema without its compatible CLI as `BLOCKED`, not `PASS`.
8. Conclude `GO`, `NO-GO`, or `BLOCKED` for the exact milestone, never for untested higher layers.

Do not deploy merely because CI/CD is ready.

### 8. Reach commit-ready state

Update private state and hand off:

- approved scope and requirement traceability;
- changed files;
- gates run with `PASS`, `FAIL`, `BLOCKED`, `NOT RUN`, or `N/A`;
- manual acceptance status;
- CI/CD status;
- known risks and next feature.

If `PROJECTSTATUS.md` and `BUILDLOG.md` are adopted, keep the former as a concise current snapshot and the latter as a curated newest-first material history. Neither file proves implementation or replaces Git, specs, tests, or runtime evidence.

Keep the user as the default commit author. If they expect to run only `git commit`, stage only the exact approved files when doing so cannot disturb unrelated staged work; otherwise provide the exact safe staging command and explain the conflict. Never commit or push without explicit authorization.

## Resume without conversation memory

When invoked again, or when the user says "continue":

1. Inspect Git, documents, source, migrations, tests, workflows, and runtime evidence.
2. Read `.easy2dev/state.yaml`, the newest journal entry, the active feature file, and evidence pointers.
3. Detect stale or contradicted private state and repair it rather than trusting it blindly.
4. Reconstruct the last completed gate and the next valid transition.
5. Continue automatically if the next transition is already authorized.
6. Ask only when the next transition crosses a decision or authority gate.

Never use chat history as the sole evidence that work was completed, tested, approved, committed, or deployed.

## Maintain private project state

Read [private-state.md](references/private-state.md) before initializing, repairing, or writing `.easy2dev/`.

- Keep `.easy2dev/` out of tracked files through `.git/info/exclude`, not a public `.gitignore` entry.
- Store concise facts, decisions, stage transitions, and pointers to evidence.
- Never store secrets, credentials, tokens, personal profiles, raw private prompts, hidden reasoning, or full command logs.
- Update state after material transitions and before pausing.
- If local private state is unavailable, reconstruct from the repository and create it when writable.

## Ask useful questions

- Inspect first; never ask for facts available in files, Git, contracts, or runtime output.
- Ask one to three related questions at a time.
- Offer a recommended default and the consequence of alternatives.
- Use plain question-and-answer language, not an unexplained technical questionnaire.
- Do not ask the user to decide library or folder details unless they change product constraints, public contracts, security, cost, or operability.

## Load references progressively

- Always read `operating-principles.md` and `workflow-state-machine.md`.
- Read `project-discovery.md` on every fresh invocation or resume.
- Read `private-state.md` when state is created, repaired, or updated.
- Read `product-docs.md` during brainstorming or documentation work.
- Read `local-onboarding.md` when a user asks for multi-developer setup, a one-command local workflow, Dev 2 onboarding, or when environment drift blocks reliable work.
- Read `plug-and-play-lifecycle.md` when dependency drift, canonical development ports, `dev.ps1`, VM onboarding/deployment, or a "plug and play" workflow is in scope.
- Read `dependency-management.md` whenever any application, workspace, CLI, runtime, container image, CI action, or external-service dependency is added, changed, installed, validated, built, or deployed.
- Read `python-dependencies.md` whenever Python dependencies, `pyproject.toml`, `uv.lock`, `requirements.txt`, pip, uv, Python containers, or Python dependency deployment is in scope.
- Read `feature-delivery.md` before planning or implementing a slice.
- Read `spec-driven-development.md` whenever accepted behavior is created, changed, removed, renamed, reconstructed, applied, or archived, especially in brownfield projects.
- Read `change-safety.md` before any bug fix, behavior change, refactor, shared configuration change, or dependency change.
- Read `api-mapping.md` whenever an HTTP API, WebSocket message, event, webhook, client wrapper, or consumer integration is created, changed, mapped, deprecated, or diagnosed.
- Read `frontend-delivery.md` whenever frontend, web UI, mobile UI, visual design, component, page, responsive, accessibility, or browser acceptance work is in scope.
- Read `project-records.md` whenever PROJECTSTATUS.md, BUILDLOG.md, portfolio documentation, project handoff, or public status claims are created, read, or updated.
- Read `evidence-and-cicd.md` before technical acceptance, CI/CD, migration, release, deploy, or rollback work.
- Read `portability.md` when installing, packaging, or adapting this skill for another agent or machine.
