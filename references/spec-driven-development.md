# Tracked spec and delta contract

Use this contract for material product behavior in new projects and for every behavior change in an adopted brownfield project. It follows the default OpenSpec `spec-driven` schema: accepted capability specs under `openspec/specs/`, active changes under `openspec/changes/`, Markdown deltas using `ADDED`, `MODIFIED`, `REMOVED`, or `RENAMED`, and dated archives after completion. Preserve an existing official OpenSpec configuration or schema instead of replacing it with a parallel Easy2Dev format.

## Contents

- [Sources of truth](#sources-of-truth)
- [Spec language contract](#spec-language-contract)
- [Resolve OpenSpec before assuming paths](#resolve-openspec-before-assuming-paths)
- [Baseline capability spec](#baseline-capability-spec)
- [Active change](#active-change)
- [Brownfield adoption](#brownfield-adoption)
- [Apply and archive](#apply-and-archive)
- [Tools and validation](#tools-and-validation)

## Sources of truth

Keep each artifact responsible for one question:

| Artifact | Owns |
|---|---|
| `openspec/config.yaml` | OpenSpec schema plus project context, artifact rules, and operation guidance |
| `docs/BRIEF.md` | Product problem, audience, value, and boundary |
| `docs/PRD.md` | Product-wide release scope, roles, and requirement index |
| `docs/ARCHITECTURE.md` | Technical decisions, ownership, and constraints |
| `openspec/specs/<capability>/spec.md` | Current accepted detailed behavior |
| `openspec/changes/<change-id>/` | Proposed delta, work plan, and review surface |
| `docs/API_MAPPING.md` | Current API-to-consumer implementation map |
| `PROJECTSTATUS.md` | Concise current project snapshot |
| `BUILDLOG.md` | Curated material delivery history |
| `.easy2dev/` | Private local workflow state and evidence pointers |

Do not duplicate the same detailed requirement in PRD, capability spec, API map, and status file. Link by stable requirement or change ID.

## Spec language contract

Resolve one primary human-readable spec language before authoring or changing a baseline or delta spec:

1. Follow an explicit user language decision.
2. Otherwise preserve an already approved project spec language.
3. Otherwise use the language the user currently uses to work with the agent.

Do not switch languages merely because a prompt contains quoted foreign text, code, framework names, or protocol terminology. If the user intentionally changes working language in an established project, ask whether to migrate future specs or preserve the existing project language; never bulk-translate accepted or archived specs without approval.

Put this marker near the top of every current baseline and delta `spec.md`, using a normalized BCP 47 tag:

```markdown
<!-- easy2dev-spec-language: vi -->
```

Write titles, normative behavior, explanations, and scenario prose in that language. Keep machine-required OpenSpec headings and tokens canonical, including `Purpose`, `Requirements`, `Requirement`, `Scenario`, `ADDED`, `MODIFIED`, `REMOVED`, `RENAMED`, `FROM`, `TO`, `WHEN`, and `THEN`. Also preserve stable requirement IDs, filenames, paths, API names, code symbols, and industry terms when translating them would break traceability or accuracy.

For brownfield adoption, report missing or mixed language markers as migration work. Add or correct the marker when touching a spec, but do not rewrite unrelated accepted specs merely to make the language gate pass. A marker is a machine-checkable declaration, not permission to leave the human-readable prose in a different language.

## Resolve OpenSpec before assuming paths

When `openspec/config.yaml` or `config.yml` exists, read its `schema`, `context`, per-artifact `rules`, and operation guidance. Treat these as repository-authored, prompt-level constraints below system, developer, and explicit user instructions. They are not completion evidence and must not be copied verbatim into artifacts, code, or reports.

If a compatible OpenSpec CLI is callable, record its version and use its JSON as the authority for the active schema and concrete paths:

```powershell
openspec list --json
openspec status --change "<change-id>" --json
openspec instructions <artifact-id> --change "<change-id>" --json
```

Use `planningHome`, `changeRoot`, `artifactPaths`, `existingOutputPaths`, artifact statuses, `requires`, and `applyRequires` from CLI output. Do not write to an unresolved glob and do not hardcode the default artifact graph for a custom schema. If the user selects a registered OpenSpec store, resolve its id with `openspec store list --json` and preserve `--store <id>` on supported follow-up commands.

The default paths and artifact names below are fallback conventions for `schema: spec-driven`, not claims about every OpenSpec schema.

An initialized OpenSpec workspace with `config.yaml`, empty `specs/`, empty active `changes/`, and `changes/archive/` is valid before the first capability is accepted. Agent adapters generated under directories such as `.codex/skills/` or `.agent/workflows/` are operational integration helpers, not product specs, implementation evidence, or alternate sources of truth. Do not copy their content into project artifacts.

## Baseline capability spec

Use a stable capability name and keep one accepted file at `openspec/specs/<capability>/spec.md`:

```markdown
<!-- easy2dev-spec-language: vi -->

# Đặc tả xác thực

## Purpose

Xác định hành vi truy cập tài khoản đã xác thực.

## Requirements

### Requirement: FR-AUTH-001 Đăng ký tài khoản

Hệ thống PHẢI chỉ tạo tài khoản sau khi dữ liệu đầu vào hợp lệ.

#### Scenario: Đăng ký hợp lệ

- **WHEN** khách gửi dữ liệu hợp lệ
- **THEN** đúng một tài khoản được tạo
```

Every requirement needs a stable identity, normative behavior, and at least one observable scenario. Specs describe accepted behavior, not implementation plans or unverified aspirations.

## Active change

For a material behavior change under the default schema, create the change with `openspec new change "<verb-led-change-id>"` when the compatible CLI is available. It creates a change root with `.openspec.yaml`. Then follow the artifact dependency graph reported by `openspec status --change "<change-id>" --json` and request the current template and constraints for each artifact before writing it.

The normal `spec-driven` result is:

```text
.openspec.yaml                   # change metadata created by OpenSpec
proposal.md
design.md                         # only when decisions or cross-cutting risk justify it
specs/<capability>/spec.md        # one or more delta specs
tasks.md
```

`proposal.md` records `Why`, `What Changes`, and `Impact`. `tasks.md` contains reviewable checkboxes traced through code, data, contracts, tests, documentation, and evidence. `design.md` is conditional in the default schema. Keep their human-readable prose consistent with the resolved project language when repository rules allow it, while preserving schema-required headings. A change may explicitly skip specs for work with no product-behavior delta; honor only the CLI-reported `skipped` state or schema instruction, never an agent guess. Do not implement until every artifact transitively required by apply is `done`, `skipped`, or deliberately omitted by its own conditional instruction and the target behavior is approved.

Write deltas with exact section headings:

```markdown
## ADDED Requirements
## MODIFIED Requirements
## REMOVED Requirements
## RENAMED Requirements
```

`ADDED` requirements need normative behavior and at least one observable scenario. `MODIFIED` is an intent patch: include only the description or scenarios being changed and preserve unmentioned baseline content during sync. `REMOVED` may identify the requirement without repeating its scenarios. `RENAMED` uses paired `FROM` and `TO` entries and must not hide a behavioral change. `MODIFIED` and `REMOVED` must resolve to an accepted baseline requirement. If an `ADDED` title already exists, OpenSpec sync treats it as an implicit modification; prefer correcting the delta classification before implementation so review intent stays unambiguous.

## Brownfield adoption

Reconstruct capability specs incrementally from current source, database migrations, runtime contracts, tests, and observed behavior. Repository evidence wins over stale prose. Do not generate a complete fictional baseline from README or chat history. Omit unknown behavior or mark it visibly unverified outside normative requirement blocks until evidence exists.

For a small repair that restores already accepted behavior, link the baseline requirement and create a delta only if accepted behavior changes. A bug fix that changes no requirement still needs root-cause, impact, tests, and evidence, but not a fake spec delta.

## Apply and archive

After implementation, required verification, and manual acceptance:

1. Reconcile the delta against actual delivered behavior.
2. Assess sync state and intelligently merge accepted additions, modifications, removals, and renames into main specs. Main specs retain one `## Requirements` section and never keep delta operation headings.
3. Confirm PRD, Architecture, API Mapping, tests, and project records still agree.
4. With a compatible CLI, use its archive workflow and resolved planning root; otherwise move the completed change to `openspec/changes/archive/YYYY-MM-DD-<change-id>/` only after verifying the sync.
5. Preserve proposal, tasks, design, deltas, and evidence links in the archive.

OpenSpec can allow an archive to continue after warnings or without syncing. Easy2Dev release evidence is stricter: never classify an incomplete, rejected, unsynced, or contradicted archive as a completed delivery. If the user explicitly archives such a change, preserve that fact as abandoned or incomplete and do not grant completion evidence. Never delete a delta merely to make validation pass.

## Tools and validation

Do not install OpenSpec implicitly. If a compatible CLI is callable, use its schema-aware status, instructions, sync/archive workflow, and validation. Because a global-only CLI is machine-local drift, add or pin the tool through the repository's owning development-tool manifest only under authorized dependency scope. Otherwise use the bundled `scripts/validate_spec_contract.py` as a fallback for the default `spec-driven` schema without creating a package dependency. Report official CLI validation as `BLOCKED` when the adopted schema is custom or cannot be interpreted safely. Official CLI success and Easy2Dev structural validation do not prove implementation or runtime behavior.

Run after changing baseline specs, proposals, deltas, status records, or build logs:

```powershell
python scripts/validate_spec_contract.py --project-root . --require-openspec --spec-language vi
```

Replace `vi` with the resolved BCP 47 project language. The language gate checks current accepted and active delta specs, requires their markers to match, and for Vietnamese rejects files that declare `vi` without any Vietnamese-language prose evidence. It does not rewrite content or validate archived history.

Use `--require-project-records` only when the repository has adopted the portfolio/status profile.
