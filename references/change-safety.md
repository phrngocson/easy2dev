# Clean change contract

Apply this contract before every bug fix, behavior change, refactor, shared configuration change, or dependency change. Clean code means preserving the system's invariants while correcting the owning cause; it does not mean rewriting surrounding code for style.

## 1. Reproduce and locate ownership

Before editing:

1. Reproduce the observable symptom with the smallest reliable command, request, or test.
2. Trace the full owning flow from entrypoint through contract, domain logic, persistence, and external boundary as applicable.
3. State the root-cause hypothesis and the evidence that distinguishes it from a downstream symptom.
4. Identify the module that owns the broken invariant. Fix there unless an established boundary requires another location.

If the cause is not yet evidenced, continue diagnosis. Do not scatter defensive changes across callers to make the symptom disappear.

## 2. Build an impact map

Record the smallest useful impact map:

- owning module and invariant;
- direct callers and consumers;
- shared schemas, types, configuration, events, APIs, and database objects;
- tests and documentation that state the expected behavior;
- explicitly protected out-of-scope behavior.

Treat a public API, shared library, authentication path, migration, common configuration, or startup script as a wider blast radius even when the code diff is small.

## 3. Choose the smallest coherent fix

The smallest coherent fix is the least change that restores the invariant across every affected layer. It is not necessarily the fewest files.

- Preserve existing module ownership and dependency direction.
- Keep unrelated formatting, renames, refactors, and dependency upgrades out of the slice.
- Change a public contract only when the approved requirement requires it; map and verify every consumer in the same slice.
- Add an abstraction only when it removes demonstrated duplication or protects a real boundary.
- Update manifest and lockfile with the consuming code whenever a dependency changes.

Never use these as a shortcut:

- swallowing exceptions or replacing specific failures with unconditional success;
- disabling, deleting, skipping, or weakening a correct test;
- inventing a route, mock response, duplicated business rule, or client-side database access to bypass a missing backend contract;
- creating a second configuration or dependency source of truth;
- changing a shared default to repair one caller without checking the others;
- broad cleanup that makes the functional change hard to review.

## 4. Verify by blast radius

Run gates in increasing scope:

1. the reproducer or focused regression test;
2. owning module unit tests;
3. affected contract, persistence, migration, or integration tests;
4. mapped consumer tests and user journey when a public boundary changed;
5. wider regression gates when shared code, shared configuration, authentication, startup, or infrastructure changed.

A focused test passing proves only the focused behavior. Record wider unavailable gates as `BLOCKED` or `NOT RUN`, not `PASS`.

## 5. Audit the final diff

Before handoff:

- explain how each changed file participates in the root-cause fix;
- confirm protected behavior still has evidence;
- check that no temporary debug code, hidden dependency, stale generated artifact, or parallel source of truth remains;
- reconcile API maps, diagrams, tests, and documentation affected by the change;
- report the exact blast radius and every unverified layer.

Stop and re-plan when evidence expands the change into a new module, public contract, schema, shared infrastructure, or product decision. Do not silently absorb that expansion into the original repair.
