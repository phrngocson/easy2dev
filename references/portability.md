# Portability

Keep Easy2Dev usable across projects, machines, accounts, and coding agents.

## Canonical package

The portable package is the `easy2dev/` folder containing:

- `SKILL.md` as the canonical workflow;
- `references/` for progressively loaded guidance;
- `scripts/` for deterministic local automation;
- `agents/openai.yaml` as an optional OpenAI UI adapter.

Do not make canonical behavior depend on `agents/openai.yaml`, a global prompt, an `AGENTS.md` file, conversation history, an MCP server, a particular account, or an absolute filesystem path.

## Agent Skills CLI package

Easy2Dev is compatible with the open Agent Skills CLI when the published Git repository either contains this package at its root or under a standard `skills/easy2dev/` container. Keep `name: easy2dev` in `SKILL.md`; the repository name does not define the installed skill name.

Verify discovery before publication:

```powershell
npx skills add . --list
```

After publication, consumers can install only Easy2Dev with:

```powershell
npx skills add https://github.com/<owner>/<repository> --skill easy2dev
```

Use `-g --agent codex -y` only when the caller explicitly wants a non-interactive global Codex installation. Do not publish local fixtures, caches, private state, credentials, or nested generated sample skills. A sample containing its own `SKILL.md` files belongs outside the release package or in an ignored path.

## Cross-agent behavior

- Agent Skills-compatible tools may discover and invoke the folder natively.
- Other coding agents can use the same package by loading `SKILL.md` as their workflow entrypoint.
- Product-specific adapters may be added outside canonical instructions, but must not change authority gates or source-of-truth rules.
- Use relative paths with `/` inside the package.
- Use standard Markdown and YAML; keep scripts on the Python standard library unless a dependency is essential.

## Cross-project behavior

- Detect the repository's stack, shell, package manager, architecture, and conventions.
- Do not carry schema, migrations, providers, deployment targets, or product claims from another project. Do not carry arbitrary project ports; apply the canonical port profile only when the repository matches the documented Windows FastAPI/Next.js/Supabase profile or the user explicitly adopts it.
- Never embed usernames, home directories, drive letters, organization names, credentials, or personal learning preferences.
- Treat repository instruction and status files as optional evidence, not prerequisites.

## Moving or publishing the skill

Copy the entire canonical `easy2dev/` directory while applying the release exclusions above. Preserve relative structure. After installation, validate the package with the target agent's skill validator when available and run the bundled unit tests with an existing Python interpreter. The private `.easy2dev/` directory inside each project is runtime state and is not part of the portable skill package.
