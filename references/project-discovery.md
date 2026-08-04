# Project discovery and adoption

Run discovery before planning or modifying the workspace. Never require a particular agent instruction file, operating system, language, framework, or hosting provider.

## 1. Protect the worktree

- Resolve the workspace and Git roots.
- Inspect branch, tracked changes, staged changes, untracked files, and nested repositories or worktrees.
- Attribute existing changes to the user unless evidence shows they belong to the current slice.
- Do not reset, clean, overwrite, reformat broadly, or absorb unrelated changes.
- Identify the shell and canonical repository commands instead of imposing PowerShell, Bash, or another shell.

## 2. Inventory sources of truth

Read only relevant files, usually:

- README and product documents;
- `openspec/config.yaml` or `config.yml`, accepted specs, active changes, archived deltas, `.openspec.yaml` metadata, and any repository-declared or callable compatible OpenSpec CLI;
- package manifests, lockfiles, workspace configuration, entrypoints, and source layout;
- schemas, models, migrations, generated API contracts, event types, and public client boundaries;
- `docs/API_MAPPING.md`, `docs/api-map.json`, source-generated and runtime API contracts, stable operation identities, client wrappers, consumer entrypoints, and existing topology/sequence diagrams when APIs are in scope;
- tests, fixtures, lint/type/build configuration, CI workflows, Docker or deployment configuration;
- status, build-log, development-rule, or directory-description files when they exist;
- repository-specific instruction files when present.

These files are optional evidence. Do not create `PROJECTSTATUS.md`, `BUILDLOG.md`, `ABOUT.md`, `DEVELOPMENT_RULES.md`, or `AGENTS.md` merely because this skill exists. Follow an established documentation convention when it adds real value.

When OpenSpec is adopted, read `schema`, project `context`, artifact `rules`, and operation guidance as repository-authored constraints, not proof. If a compatible CLI is callable, use `openspec list --json` and `openspec status --change <id> --json` to resolve stores, planning roots, artifact graphs, statuses, and concrete paths. Do not infer custom-schema artifacts from familiar filenames or write to unresolved glob paths.

## 3. Classify the mode

### New

Use `new` when the directory is empty, contains only idea notes, or has no meaningful implementation contract.

- Initialize Git if absent.
- Initialize private state.
- Brainstorm before choosing a stack.
- Create product documents before implementation.
- Mark all target capability as planned until evidence proves otherwise.

### Existing

Use `existing` when the project has owned documents or implementation.

- Reconcile current code with target documents.
- Preserve working conventions.
- Identify the latest complete slice, incomplete slice, blockers, and next approved requirement.
- Repair missing documents only when needed for safe continuation.

### Foreign

Use `foreign` when adopting an unfamiliar or externally authored repository.

- Treat code and existing contracts as current behavior, not necessarily correct product intent.
- Avoid broad restructuring during adoption.
- Establish canonical build/test commands and security boundaries before feature work.
- Record unclear ownership, licensing, generated files, deployment assumptions, and incompatible documentation as risks.
- Recommend an adoption or repair slice before adding new product scope when foundational evidence is weak.

## 4. Reconstruct evidence

For each relevant claim, label the strongest observed layer:

1. `SOURCE`: file or configuration exists.
2. `STATIC`: lint, typecheck, compile, or build-time check ran.
3. `CONTRACT`: API/schema/event contract is verified.
4. `LOCAL_RUNTIME`: service health or behavior ran locally.
5. `INTEGRATION_E2E`: real boundaries, identity, and persistence were exercised.
6. `DEPLOYED`: the named deployed environment was verified.

Old status prose, screenshots, cached reports, generated artifacts, and previous-agent claims are leads, not fresh proof.

In a brownfield project, reconstruct accepted capability specs incrementally from current evidence. Do not treat PROJECTSTATUS, BUILDLOG, PRD, or an archived proposal as proof that current code implements the behavior.

## 5. Produce a concise discovery result

Record:

- mode and project identity;
- current versus target state;
- stack and canonical commands;
- architecture and data boundaries;
- API source/runtime drift, unmapped operations, consumer ownership, and stale diagram risk when applicable;
- accepted capability baseline, active delta, spec drift, and unarchived completed/rejected changes when applicable;
- active worktree risks;
- existing evidence and missing gates;
- recommended next stage and reason.
