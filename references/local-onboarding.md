# Reproducible local onboarding

Use this lane only when a team, new contributor, multiple machines, or measured environment drift justifies it. The outcome is identical code, dependency versions, configuration contract, schema revision, service ownership, and startup order—not shared local data.

## 1. Discover the real environment

- Inspect Git state, repository instructions, manifests, lockfiles, container files, environment examples, runtime settings, migrations, health checks, startup scripts, and onboarding docs.
- Preserve unrelated changes and remove duplicated configuration only after reference/import checks.
- Identify which tool owns each local service. Do not let Compose silently create a second database when a local platform CLI already owns database/auth/storage.
- Never read, print, copy, or commit secret values. Inspect variable names, sources, and presence only.

Map every URL by caller:

| Caller | Address form |
|---|---|
| Browser or host process | Public host address such as `localhost` or `127.0.0.1` |
| Container calling a host service | Platform-supported host bridge such as `host.docker.internal` |
| Container calling another Compose service | Compose service name and internal port |

Do not reuse one URL across incompatible execution contexts.

## 2. Build one canonical lifecycle

Create or reconcile one root entrypoint with `up`, `down`, and `status`. Use the repository's primary shell or task runner:

- Windows-first repository: a PowerShell script is reasonable.
- POSIX-first repository: a shell script, Makefile, Justfile, or Taskfile may be better.
- Cross-platform repository: prefer an existing cross-platform task runner or provide thin equivalent wrappers over one canonical implementation.

Requirements:

- `up` is idempotent and safe after clone or pull.
- On Windows-first application projects, no-argument `scripts/dev.ps1` means `up`; the same entrypoint must reconcile a later session after dependency or env changes.
- `down` stops only project-owned resources and does not delete data by default.
- `status` reports actionable service and URL state without exposing secrets.
- Dependency installation honors committed lockfiles and never runs an unlocked resolver at container startup.
- The startup path discovers all dependency roots, rejects missing/stale lockfiles, and performs frozen synchronization before services start. A package present only on one machine is never accepted as project state.
- For Python, apply [python-dependencies.md](python-dependencies.md): use uv for new backends, reject a hand-written `requirements.txt` beside uv, and preserve a validated legacy pip workflow until migration is explicitly approved.
- Bind mounts do not hide installed dependencies or virtual environments.
- Container/check-out names do not collide unintentionally across developers or worktrees.

For the adopted Windows FastAPI/Next.js/Supabase profile, read [plug-and-play-lifecycle.md](plug-and-play-lifecycle.md) and enforce backend `8000`, frontends from `3000`, Supabase API `54321`, Studio `54323`, Mailpit `54324`, and exact-PID development port reclamation. Keep the port map in a tracked source and generate ignored runtime configuration from it.

## 3. Generate safe local configuration

- Keep real local env files ignored.
- Commit only safe examples containing variable names, descriptions, and non-secret placeholders.
- Derive local endpoints and temporary local credentials from an authoritative local stack status command when available; never require manual dashboard copying.
- Generate separate host-run and container-run configuration when their addresses differ.
- Validate required variables early and report missing names without values.
- Add line-ending rules only when the team actually crosses operating systems or executable scripts require them.

## 4. Make startup ordering deterministic

- Run schema migration as an explicit, observable gate before the application accepts traffic.
- Use readiness/health conditions for required downstream dependencies; process existence alone is insufficient.
- Distinguish liveness, readiness, and business smoke.
- Use one source of truth for migrations and verify current/head after startup.
- Do not add Docker or Compose if the project has a simpler, already reproducible native workflow.

## 5. Write the contributor path

Create `docs/DEV2_ONBOARDING.md` unless the repository has a clear equivalent. Address the new contributor directly and keep the first-run path linear:

1. One-time prerequisites with copyable commands for the detected shell.
2. Clone/pull and enter the repository.
3. Run exactly one startup command.
4. Verify concrete URLs or expected outputs.
5. Follow the daily pull/start routine. The normal routine is the same one command after clone, pull, env changes, dependency changes, or a new work session.
6. Stop services safely.
7. Avoid committing env files, direct production changes, dashboard-only schema edits, dependency drift, and destructive cleanup.
8. Collect a minimal secret-safe diagnostic bundle.

Link the guide from README. Keep deep troubleshooting separate from the first-run path.

## 6. Validate in layers

Run the bundled static validator first:

```text
python <skill-root>/scripts/validate_local_onboarding.py --project-root <repository-root>
```

Add `--require-default-managers` for new Easy2Dev uv/npm projects, `--require-standard-ports` for the canonical Windows web stack, and `--require-vm` when VM deployment is an approved project capability. Do not apply the default-manager flag to an adopted legacy manager before migration is approved.

Use an already available Python interpreter; otherwise perform the same checks manually. Then verify applicable runtime layers separately:

- configuration/Compose parses from a checkout without pre-existing local env files;
- first `up` succeeds and a second `up` is idempotent;
- schema reaches the expected revision;
- backend tests, frontend static checks, and production builds pass as applicable;
- health and business smoke pass;
- authenticated API and browser redirect smoke pass when Auth/UI exist;
- `down` stops only project resources and preserves data.

Report each layer as `PASS`, `FAIL`, `BLOCKED`, `NOT RUN`, or `N/A`. Do not infer application or auth success from a successful container build.

## 7. Handoff

Lead with the exact first-run, daily-start, status, and shutdown commands. Record generated files, ignored runtime state, verified URLs, migration revision, evidence by layer, unresolved blockers, and the next safe action in `.easy2dev/`.
