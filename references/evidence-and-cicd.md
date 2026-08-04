# Evidence, CI/CD, migration, and release safety

Read the sections relevant to the current stage. CI/CD readiness and deployment are separate authorities.

## Evidence model

Record each gate independently:

- `PASS`: the gate ran against the named source/environment and met its condition.
- `FAIL`: the gate ran and found an in-scope defect.
- `BLOCKED`: the gate cannot run reliably because of environment, permission, credential, service, or dependency limitations.
- `NOT RUN`: the gate has not run.
- `N/A`: the gate is not applicable, with a reason.

Typical layers:

1. dependency/lockfile reproducibility;
2. tracked spec baseline and delta validation when applicable;
3. format, lint, typecheck, and compile;
4. API mapping and Mermaid structural validation when applicable;
5. unit tests;
6. integration/API/WebSocket/contract tests;
7. production build or artifact verification;
8. migration/schema safety;
9. container/service health;
10. runtime smoke or E2E on a named environment;
11. post-deploy health, logs, and monitoring.

Dependency evidence requires every application/workspace manifest to have one owning manager and lockfile or a validated legacy pip contract, plus a frozen install or sync that leaves tracked files unchanged. Apply [dependency-management.md](dependency-management.md); for Python also apply [python-dependencies.md](python-dependencies.md), including uv lock freshness, source ownership, legacy pins/includes, and generated export drift. A successful run from a pre-populated virtual environment, global package, cache, or old container layer is not reproducibility evidence. When the plug-and-play profile is adopted, read [plug-and-play-lifecycle.md](plug-and-play-lifecycle.md) and validate its port, `dev.ps1`, and `vm.ps1` contracts explicitly.

Never infer a higher-layer pass from a lower layer. A healthy process does not prove business behavior; local E2E does not prove production.

For API-backed work, apply [api-mapping.md](api-mapping.md). A valid map proves that mandatory `docs/API_MAPPING.md` and `docs/api-map.json` agree structurally with declared OpenAPI operations, consumer files, client symbols, and Mermaid blocks. It does not prove source/runtime parity, correct API behavior, rendered diagram syntax, authentication, or an end-to-end journey; record those as separate gates.

## Failure diagnosis

1. Identify the exact command, workflow, job, step, source revision, and environment.
2. Preserve the first meaningful failure and distinguish root cause from cascading failures.
3. Compare runtime, dependency, configuration, data, and service boundaries.
4. Locate an already installed runtime with read-only tools when the default alias is broken. For a dependency-free project, do not create a virtual environment, package-manager cache, or dependency installation merely to discover an executable.
5. Reproduce with the smallest canonical command when safe.
6. Fix the root cause inside approved scope.
7. Rerun the narrow failing gate, then related wider gates.
8. Report unavailable verification as `BLOCKED`, never conditional `PASS`.

## Minimal CI design

After explicit CI/CD approval, inspect existing workflow and canonical repository commands. Add only gates justified by real stack and risk, ordered for fast feedback:

| Gate | Minimum proof |
|---|---|
| Dependency | Locked, reproducible installation without unintended lockfile changes |
| Spec delta | Schema/config resolved, required artifact graph complete, accepted baseline, coherent delta or explicit skip, verified sync, and correct archive state |
| API map | Complete operation classification, real consumer paths, and mapped Mermaid topology/sequences |
| Static | Clear exit codes for format/lint/typecheck/compile as applicable |
| Unit | Actual test count and report |
| Integration | Named database/API/service boundaries |
| Build | Reproducible artifact tied to source identity |
| Security | Agreed secret, dependency, or image checks |
| Runtime | Health/smoke/E2E on a named environment |

Do not add a version matrix, browser suite, load test, or new tool unless product requirements or risk justify the cost. Never weaken a gate to hide a failure.

When the repository owns an API map, CI should run `scripts/validate_api_mapping.py` without `--allow-partial`. Compare source-generated and runtime OpenAPI in the appropriate runtime gate; do not let the structural validator substitute for that comparison.

When the repository adopts tracked capability specs, CI should run its pinned compatible OpenSpec validation and `scripts/validate_spec_contract.py --require-openspec` for the default `spec-driven` Easy2Dev profile. Add `--require-project-records` only for repositories that intentionally adopt PROJECTSTATUS and BUILDLOG. A custom schema without its compatible CLI is `BLOCKED`; never download an unpinned CLI inside CI to repair or reinterpret specs.

For a multi-application repository, run the dependency gate for each owning root or prove that a declared workspace lock covers it. CI should use frozen commands such as `uv lock --check`/`uv sync --locked` and `npm ci`, then fail if tracked manifests or locks changed. When a platform requires a pip artifact, regenerate it from uv into a temporary file and compare rather than rewriting it in CI. For legacy pip, install recursively pinned requirements into a clean environment. Do not use daily startup or CI to repair dependency declarations automatically; the implementing agent must commit the manifest and lock change together.

## Migration safety gate

Before creating, running, approving, or releasing a migration, verify:

- database and environment identity;
- framework, source head, and current database revision;
- graph integrity and scoped diff;
- destructive operations, type narrowing, implicit rename, new constraints, large rewrites, and lock risk;
- old/new application compatibility;
- idempotent, bounded, restartable, observable backfill behavior;
- backup, roll-forward, application rollback, or restore path.

Run local/test migrations only when the target is verified. Production migration always requires explicit authority. Do not assume schema downgrade is safe.

## Pre-release gate

Before calling a release ready, require the applicable evidence on the exact source identity:

- required CI gates pass;
- production artifact is reproducible and traceable;
- required configuration exists without exposing secret values;
- capacity and dependencies meet the minimum envelope;
- migration order and recovery plan are defined;
- readiness, smoke, monitoring, and rollback ownership exist.

Conclude:

- `GO` only when every required gate for the named milestone passes;
- `NO-GO` when an in-scope required gate fails;
- `BLOCKED` when a required gate cannot run reliably.

## Deploy and rollback authority

Do not commit, push, tag, publish, change secrets, migrate production, deploy, or roll back merely because release readiness is `GO`. Obtain explicit authorization for the exact action and target.

When deployment is authorized:

1. pin target and immutable artifact identity;
2. record baseline health and metrics;
3. verify config, secret presence, capacity, and dependencies;
4. run an approved compatible migration if required;
5. deploy using the actual topology's strategy;
6. verify readiness, then business smoke;
7. observe agreed metrics and logs;
8. complete rollout or trigger predetermined rollback criteria;
9. verify health and data again after rollback.

Never promise zero downtime without topology, capacity, readiness, and schema-compatibility evidence.
