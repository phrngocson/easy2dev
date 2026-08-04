# Dependency management contract

Apply this contract to every application, workspace, build image, project-owned CLI, and runtime needed to develop, test, build, or deploy the repository.

## One owner per dependency root

Use one manifest/lock pair for each dependency root. Do not mix package managers or keep competing lockfiles in the same root.

| New project type | Canonical source | Change command | Frozen synchronization |
|---|---|---|---|
| Python backend | `pyproject.toml` + `uv.lock` | `uv add`, `uv add --dev`, `uv remove` | `uv sync --locked` |
| JavaScript/TypeScript app | `package.json` + `package-lock.json` | `npm install`, `npm uninstall`, `npm install --save-dev` | `npm ci` |

For Python details and legacy `requirements.txt`, read [python-dependencies.md](python-dependencies.md).

Preserve an existing Poetry, PDM, pip, pnpm, Yarn, Bun, Cargo, or Go workflow while validating its own frozen contract. Do not introduce a second manager or migrate the existing manager without explicit approval. Multiple recognized lockfiles beside one manifest are `FAIL`, not a reason to guess.

Use these frozen commands when those existing managers are detected: `poetry install --sync`, `pdm sync --clean` or its frozen-lock equivalent, `pnpm install --frozen-lockfile`, `yarn install --immutable`, `bun install --frozen-lockfile`, Cargo with `--locked`, and `go mod download` followed by readonly build/test behavior. Keep the repository's stronger existing command when present.

## Agent dependency-change protocol

Whenever code needs a missing, new, removed, or upgraded dependency:

1. Identify the owning root, direct consumer, runtime/dev classification, manifest, lockfile, build stage, and deploy consumer.
2. Use the owning manager's change command; never satisfy the change only in a global environment, `.venv`, `node_modules`, cache, interactive shell, or old container.
3. Review both manifest and lock diff. Do not hand-edit generated lockfiles.
4. Run frozen synchronization from the lock and confirm it does not rewrite tracked dependency files.
5. Rebuild every affected image/artifact and run the smallest consumer test, then broader build/runtime gates.
6. Commit the manifest, lock, Docker/CI changes, configuration example, test, and relevant documentation in the same slice.

Repository startup, CI, Dockerfiles, and VM scripts may install from manifests; they must not contain ad hoc package-name installs. A checked-in `pip install <package>`, `uv pip install <package>`, `npm install <package>` in an environment bootstrap, or equivalent manager bypass is `FAIL` unless it is the explicit manifest-changing developer command documented outside runtime automation.

## JavaScript and frontend rules

Use npm for new Easy2Dev JavaScript/TypeScript applications. Commit `package-lock.json`, declare the package manager/version when the repository convention supports it, and run `npm ci` after clone/pull and in CI/container builds.

Use `npm install <package>` or `npm install --save-dev <package>` only to change the tracked manifest and lock. Do not use it as the daily startup install. A package root with both `package-lock.json` and `pnpm-lock.yaml`, `yarn.lock`, or Bun lock is ambiguous and must fail validation.

For npm workspaces, one root lock may own declared child workspaces. Do not create child lockfiles inside that ownership boundary.

## Toolchain and container dependencies

- Track supported Python and Node versions through repository-native version/config fields. `dev.ps1` checks compatibility and gives a copyable prerequisite instruction; it does not silently install or upgrade global runtimes.
- Pin project-owned CLIs through an existing package manager where practical. If a host-installed CLI such as Docker Desktop or Supabase CLI remains a prerequisite, declare its accepted version range and check it before startup.
- Pin Docker base/service images to a non-floating version or digest. Do not use an omitted tag or `latest` in a reproducible build/deploy path.
- Pin CI actions and reusable workflows to an reviewed stable reference according to repository policy; do not float on `main` or another moving branch.

## External services are configuration dependencies

Supabase Online, email, storage, AI providers, and other remote services are not installed packages. Declare their required variable names, execution-context URLs, versioned schemas/migrations, startup/deploy validation, readiness, and secret source. Never place secret values in manifests, lockfiles, generated diagnostics, or source control.

## Evidence

Keep these gates distinct: source ownership, lock integrity, frozen synchronization, clean install, artifact/image rebuild, tests/build, runtime smoke, and deployed verification. A populated environment or successful old image is not dependency evidence.
