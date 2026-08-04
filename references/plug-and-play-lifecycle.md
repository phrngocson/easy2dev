# Plug-and-play development and VM lifecycle

Use this contract for Windows-first application repositories that need a one-command daily workflow. The public interface is stable across projects; the implementation behind it must be adapted to the repository's actual stack and service ownership.

## Contents

1. [Non-negotiable dependency ledger](#1-non-negotiable-dependency-ledger)
2. [Canonical local ports](#2-canonical-local-ports)
3. [Required `scripts/dev.ps1` contract](#3-required-scriptsdevps1-contract)
4. [Required `scripts/vm.ps1` contract](#4-required-scriptsvmps1-contract)
5. [CI gates that enforce the contract](#5-ci-gates-that-enforce-the-contract)

## 1. Non-negotiable dependency ledger

Every dependency must be reproducible from tracked repository files. Apply [dependency-management.md](dependency-management.md) to every root and [python-dependencies.md](python-dependencies.md) to Python. A package that exists only in a machine, virtual environment, global installation, container layer, or agent session does not exist for delivery purposes. New Python backends use `pyproject.toml + uv.lock`; new JavaScript/TypeScript apps use `package.json + package-lock.json`; `requirements.txt` is either a validated legacy source or a marked export from uv, never a second hand-written source.

When an agent needs a missing package or changes a dependency, it must complete all of these steps in the same approved slice:

1. Identify the owning application, package manager, manifest, lockfile, runtime/dev group, and container build file that consume it.
2. Add, remove, or change the package through that package manager. For uv use `uv add`, `uv add --dev`, and `uv remove`. Never use an unrecorded convenience install such as bare `pip install`, `uv pip install`, or `npm install -g` for an application dependency.
3. Update both manifest and lockfile. Examples: `uv add <package>` plus `uv.lock`; `uv add --dev <package>` for a development-only Python package; `npm install <package>` plus `package-lock.json`; `npm install --save-dev <package>` for a development-only JavaScript package.
4. Recreate or synchronize the environment strictly from the lockfile. For the default stack use `uv sync --locked` and `npm ci`; include the repository's required dependency groups or workspaces explicitly.
5. Rebuild affected containers or artifacts so an old layer cannot hide a missing declaration.
6. Run the narrow consumer test, then the dependency reproducibility and relevant build gates.
7. Keep the manifest, lockfile, build/deploy file, configuration example, tests, and documentation changes together when they describe one dependency change.

Do not hand-edit a lockfile. Do not let a startup command silently resolve newer versions or change a tracked lockfile. CI must fail if a manifest and its lockfile disagree.

Track every dependency root, not only the repository root. A backend, each frontend, worker, tool, and workspace can own a separate manifest/lockfile pair. A workspace lockfile may cover child manifests only when the package manager configuration proves that ownership.

## 2. Canonical local ports

For this Windows FastAPI/Next.js/Supabase profile, use one deterministic port map:

| Service | Host port |
|---|---:|
| Backend API | `8000` |
| First frontend | `3000` |
| Additional frontends | `3001`, `3002`, ... in a stable declared order |
| Supabase API | `54321` |
| Supabase Studio | `54323` |
| Supabase Mailpit/Inbucket | `54324` |

Keep all frontends in `3000-3999`. Record the stable frontend-to-port mapping in one tracked configuration source and use it to generate ignored local env files, Compose mappings, CORS origins, callback URLs, proxy targets, health checks, and status output. Never determine frontend order from unstable filesystem enumeration.

When Supabase CLI owns the local stack, its tracked `supabase/config.toml` must contain API `54321`, Studio `54323`, and Mailpit `54324`. Compose must consume that stack instead of creating a competing database/auth/storage stack.

The agent that introduces or changes a service must update the tracked port source and every consumer in the same slice. The daily script may repair generated or ignored runtime files; it must not silently rewrite tracked project files and leave an unexplained dirty worktree. A tracked port mismatch is an implementation defect that must be fixed and reviewed.

## 3. Required `scripts/dev.ps1` contract

On a Windows-first repository, the one daily command is:

```powershell
.\scripts\dev.ps1
```

No argument means `up`. Keep `-Action up`, `-Action down`, and `-Action status` for automation and diagnostics. The script must be idempotent after clone, pull, dependency changes, env changes, and a later work session.

Run `up` in this order:

1. Resolve the repository root from `$PSScriptRoot`; never depend on the caller's current directory.
2. Check required host tools and print copyable installation guidance for missing tools. Do not install global system tools without explicit authority.
3. Discover every supported dependency root. Fail early for a missing or stale lockfile, an ambiguous Python source, or an invalid legacy requirement, then synchronize strictly from committed locks (`uv sync --locked`, `npm ci`, or the detected equivalent). For legacy pip, recreate the isolated environment when the recursively included requirements checksum changes. Never mutate locks during daily startup.
4. Stop this project's already running resources cleanly when they must be recreated.
5. For each canonical host port, identify the exact listening PID and process. If it is not the current script or a protected Windows system PID, terminate that exact process with `Stop-Process -Id <pid> -Force`, report its name/PID/port, and verify that the port becomes free. Never kill by wildcard process name. If the listener cannot be identified or safely stopped, fail with an actionable message rather than starting on a different port.
6. Start the authoritative local platform such as Supabase and derive local endpoints/temporary local credentials from its status output.
7. Generate ignored env files atomically from the tracked variable and port contract. Report variable names and destinations, never secret values.
8. Build or recreate affected containers so changed manifests, locks, Dockerfiles, or env inputs take effect. Bind mounts must not hide installed environments.
9. Run migrations as an observable gate before application traffic.
10. Start backend and frontends on their assigned ports, wait for readiness, then run applicable health/business smoke.
11. Print a compact URL/status summary including Backend, every Frontend, Supabase API, Studio, and Mailpit.

Port reclamation is explicitly a development-machine behavior for the canonical project ports. It does not authorize killing PID `0`, PID `4`, the current PowerShell process, protected OS services, remote processes, or arbitrary production listeners. `down` stops only project-owned resources and preserves local data by default.

`status` must check dependency-lock consistency, expected listeners, service health, migration current/head, and the effective URL map without printing credentials. `down` must be safe to repeat.

## 4. Required `scripts/vm.ps1` contract

Create `scripts/vm.ps1` when the approved deployment target is a Windows-accessible VM workflow. Its public interface is one command for an authorized deployment:

```powershell
.\scripts\vm.ps1
```

The script must adapt to the real deployment topology, prefer immutable Docker/Compose artifacts, and be safe to rerun. It must not embed project-specific secrets or URLs in the script.

Before changing the VM, it must:

1. Show and confirm the target environment, source revision, and artifact identity. Running the script is deployment intent, but production migration, secret replacement, and destructive recovery still require explicit confirmation at the relevant gate.
2. Inspect the application's actual configuration schema and prompt only for missing required variable names.
3. Ask for every public frontend URL needed by CORS, redirects, cookies, OAuth callbacks, emails, and API allowlists. Validate `https://` in production and support multiple frontends in their stable order.
4. Ask for the required Supabase Online values used by this repository, commonly project URL, publishable/anon key, service-role secret, direct/pooler database URL, JWT issuer/audience, and storage settings. Do not require variables the code does not consume.
5. Read secrets with `Read-Host -AsSecureString` or an approved secret provider. Never echo them, include them in command arguments, logs, source control, or generated diagnostics.
6. Write the ignored production env atomically with restrictive permissions and preserve a recoverable previous version without displaying its contents.

Then verify locked dependencies or build the pinned image, validate configuration presence, run migration safety checks, deploy in the real service order, wait for readiness, run business smoke, and report the named deployment evidence separately. Reclaim only ports owned by this deployment definition; never apply the local-development kill policy to arbitrary VM services.

If the target VM uses Linux, keep `vm.ps1` as the developer-facing orchestrator only when PowerShell is genuinely available; otherwise provide a thin PowerShell wrapper over the repository's canonical remote/deploy mechanism. Do not pretend a Windows-only body is portable.

## 5. CI gates that enforce the contract

CI for a plug-and-play project must independently prove:

1. Every supported manifest has an owning lockfile or validated legacy pip contract, and the frozen install/sync succeeds without changing tracked files.
2. Dependency groups used by lint, tests, migrations, build, and production are all included in the relevant job or image stage.
3. The canonical port map has no duplicates and all tracked consumers agree: backend `8000`, frontends from `3000`, Supabase API `54321`, Studio `54323`, and Mailpit `54324` when applicable.
4. `scripts/dev.ps1` parses, defaults to `up`, exposes `up/down/status`, and contains exact-PID port reclamation for a Windows-first project.
5. `scripts/vm.ps1` parses and has no committed secrets when VM deployment is in scope.
6. Safe env examples cover required variable names while real env files remain ignored and untracked.
7. Migration, build, runtime, and post-deploy evidence remain separate gates.

Run the Easy2Dev validator with stricter profile flags when these contracts are required:

```powershell
python <skill-root>\scripts\validate_local_onboarding.py --project-root <repository-root> --require-default-managers --require-standard-ports --require-vm --run-tools
```

Static validation proves repository wiring, not successful startup or deployment. First-run, repeat-run, clean-checkout, runtime, and VM verification must still be recorded separately.
