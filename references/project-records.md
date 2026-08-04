# Project status and build log contract

`PROJECTSTATUS.md` and `BUILDLOG.md` are useful, professional supplemental records when they stay concise, factual, and distinct from Git, specs, and release evidence. Preserve them when a project has adopted them; do not force them on every library or external repository.

## PROJECTSTATUS.md

Treat it as a current snapshot, not history and not proof. Keep it below 301 lines and answer:

- what the project is and its current milestone;
- verified completed capabilities;
- active work;
- incomplete or explicitly out-of-scope work;
- blockers and risks;
- strongest evidence with dates or source identities;
- the next one to three priorities;
- last updated time.

Use `PASS`, `FAIL`, `BLOCKED`, `NOT RUN`, or `N/A` for evidence. Remove stale claims instead of accumulating a timeline. Link capability specs and active change IDs. Never mark planned work complete because a proposal, diagram, file, or old log exists.

## BUILDLOG.md

Treat it as a curated engineering journal of material transitions. Put the newest entry first and separate entries with `==========`:

```markdown
## 2026-08-04T10:00:00+07:00 | add-retry-policy

- Change: Added bounded retry for transient provider failures.
- Why: FR-AGENT-RETRY-001 required recoverable execution.
- How: Updated the owning service and preserved idempotency fencing.
- Evidence: 12 unit tests PASS; local integration PASS; E2E NOT RUN.
- Result: Technical gate PASS; manual acceptance pending.
- Next: Run the documented manual recovery scenario.

==========
```

Record only material requirements, architecture decisions, migrations, fixes, measurements, releases, and gate results. Do not paste terminal transcripts, hidden reasoning, prompts, routine file edits, dependency download noise, or every Agent action. Never expose secrets, tokens, private URLs, personal data, or production payloads.

## Portfolio and hiring use

These files do not harm a portfolio by existing. They become harmful when they are enormous, stale, promotional, obviously machine-generated, or contradict code and tests.

- Keep README as the recruiter-facing entrypoint.
- Keep Git commits and pull requests as the canonical code history.
- Keep `openspec/changes/archive/` as the behavioral change history.
- Keep Architecture/ADR records as the reason behind durable decisions.
- Use PROJECTSTATUS only for the current snapshot.
- Use BUILDLOG only as a selective evidence-backed narrative.

Do not require a recruiter to read BUILDLOG to understand the project. Link only the most valuable entries from README or an engineering-notes section. Prefer five meaningful entries over hundreds of daily notes.

## Update timing

Update PROJECTSTATUS after a material verified transition or when current truth changes. Add a BUILDLOG entry after a coherent slice reaches a real gate. Do not update either before evidence merely to announce intent. If the repository uses both public records and `.easy2dev/`, public records state shareable project truth while `.easy2dev/` retains private resumability details.
