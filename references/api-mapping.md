# API mapping and Mermaid sequence contract

Apply this contract whenever a slice creates, changes, consumes, deprecates, or diagnoses an HTTP API, WebSocket message, event, webhook, or other public transport contract. The examples use OpenAPI because it is the standard FastAPI source; adapt the same identity-and-consumer rules to other transports.

## 1. Establish the real contract

An API map is not a route list. It connects the backend contract to every real consumer and the user or system flow that depends on it.

For OpenAPI-backed services:

1. Generate or inspect OpenAPI from the current source revision.
2. Fetch `/openapi.json` from the named running environment when runtime evidence is required.
3. Compare source and runtime operations. Treat a mismatch as `DRIFT`; identify stale process, image, configuration, migration, or source before mapping consumers.
4. Use `operationId` as the stable mapping identity and derive method plus exact path from OpenAPI.

A checked-in OpenAPI file is a contract registry. It is not proof that a running environment serves the same contract. An operation without a unique `operationId` is not ready for deterministic mapping.

## 2. Maintain the mandatory mapping artifacts

Every API-bearing project must keep both files:

- `docs/API_MAPPING.md`: the mandatory human-facing map that every Agent reads before API work;
- `docs/api-map.json`: the machine-checkable ledger used to prevent the Markdown map from silently drifting.

Create or reconstruct both before the first authorized API change when they are missing. A read-only invocation must report their absence as a mapping gate instead of modifying the repository.

`docs/API_MAPPING.md` must contain:

- document status and named contract/runtime evidence;
- a table or equally clear index of every `operationId`, method/path derived from OpenAPI, owner, strongest status, client wrapper, and application entrypoint;
- the current Mermaid API topology;
- links to the relevant feature sequence diagrams;
- explicit backend-only, blocked, deprecated, and removed behavior.

Keep both directions recoverable:

- backend operation -> client wrapper -> application entrypoints;
- application entrypoint -> client wrapper -> backend operation.

Recommended ledger version 2 shape:

```json
{
  "schema_version": 2,
  "mapping_document": "docs/API_MAPPING.md",
  "topology_diagrams": ["docs/API_MAPPING.md"],
  "operations": [
    {
      "operation_id": "list_projects",
      "owner": "backend.modules.projects",
      "status": "UI_INTEGRATED",
      "consumers": [
        {
          "app": "frontend",
          "client": "frontend/lib/api/projects.ts",
          "symbol": "listProjects",
          "entrypoints": ["frontend/app/projects/page.tsx"]
        }
      ],
      "sequence_diagrams": ["docs/features/projects/SEQUENCE.md"],
      "reason": ""
    }
  ]
}
```

Do not duplicate method and path in the JSON ledger; derive them from the authoritative contract to avoid drift. Use repository-relative paths and real symbols. The Markdown view may display method/path for readers, but its operation identities must match the JSON ledger and OpenAPI.

Classify every operation with one of:

- `BACKEND_CONTRACT`: backend contract exists; no consumer mapping is claimed yet;
- `CLIENT_MAPPED`: a real shared client wrapper is mapped;
- `UI_INTEGRATED`: at least one real application entrypoint uses the wrapper;
- `RUNTIME_VERIFIED`: the named runtime served the expected contract and behavior;
- `E2E_VERIFIED`: a real consumer journey was verified end to end;
- `INTENTIONALLY_BACKEND_ONLY`: no application consumer is intended; record why;
- `BLOCKED`: mapping or verification cannot proceed reliably; record why;
- `DEPRECATED`: operation remains visible during a compatibility window; record replacement or removal plan.

Statuses describe the strongest evidenced layer, not future intent. An endpoint returning `200` does not establish `UI_INTEGRATED` or `E2E_VERIFIED`.

## 3. Map consumers without inventing behavior

- Use one shared client boundary per application where repository conventions allow it.
- Trace real imports or calls to entrypoints; a similarly named file is not evidence.
- Do not invent routes, request fields, response fields, or success behavior.
- Do not scatter raw requests when an owning client boundary exists.
- Do not move identity, authorization, state transition, or other server-owned business rules into a consumer.
- Do not bypass a missing API with direct application access to backend tables or Supabase unless Architecture explicitly defines that boundary.
- Mark unused, internal, deprecated, or blocked operations explicitly rather than hiding them from coverage.

Open `docs/API_MAPPING.md` before adding, changing, removing, deprecating, consuming, or troubleshooting an API. In the same coherent slice, update the implementation, OpenAPI registry, consumer wrapper, entrypoints, tests, `docs/api-map.json`, `docs/API_MAPPING.md`, and affected diagrams. Removing an API also requires proving that no mapped consumer still calls it.

## 4. Draw the mapped system

After mapping, maintain both Mermaid views:

1. At least one API topology diagram using `flowchart` or `graph` for applications, shared clients, backend modules, data stores, and external services that actually exist.
2. A `sequenceDiagram` for each mapped consumer/business flow. One sequence may cover several operations when they form one coherent flow.

Each sequence diagram must:

- name the exact `operationId` inside the Mermaid block;
- show only evidenced participants and the real call direction;
- distinguish important success and failure branches with `alt`/`else` when relevant;
- show authentication, validation, conflict, not-found, retry, timeout, transaction, or rollback behavior when those affect the flow;
- use `loop`, `opt`, or `par` only when the runtime behavior actually has that shape.

Label the surrounding document `current`, `planned`, `implemented`, `verified`, or `stale` so readers cannot confuse design with runtime proof. A diagram explains a contract; it never proves that the runtime works.

For repositories using feature documentation, keep the mandatory global `docs/API_MAPPING.md` plus feature-local `API.md`, `SEQUENCE.md`, and `TEST_CHECKLIST.md`. Follow the repository's established hierarchy and update the nearest `ABOUT.md` when its directory description becomes stale.

## 5. Validate and gate

Run the deterministic structural validator after changing OpenAPI, a client wrapper, an entrypoint, the API map, or its diagrams:

```powershell
python scripts/validate_api_mapping.py --project-root . --openapi openapi.json --manifest docs/api-map.json
```

Use `--allow-partial` only during discovery of an adopted repository. Do not use it for slice completion or CI.

The structural gate requires:

- unique OpenAPI `operationId` values and complete operation classification;
- the exact mandatory `docs/API_MAPPING.md` file and a reference to every mapped `operationId` inside it;
- no manifest operation absent from OpenAPI;
- real consumer and entrypoint paths, plus declared client symbols;
- a reason for backend-only, blocked, and deprecated classifications;
- at least one Mermaid topology block;
- a Mermaid sequence block referencing each consumer-mapped `operationId`.

Also render Mermaid with the repository's existing documentation tool when available. Structural validation, rendering, source/runtime OpenAPI parity, API behavior tests, and authenticated consumer E2E are separate evidence gates.
