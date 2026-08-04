#!/usr/bin/env python3
"""Validate an Easy2Dev OpenAPI-to-consumer map and Mermaid coverage."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}
REQUIRED_MAPPING_DOCUMENT = "docs/API_MAPPING.md"
STATUSES = {
    "BACKEND_CONTRACT",
    "CLIENT_MAPPED",
    "UI_INTEGRATED",
    "RUNTIME_VERIFIED",
    "E2E_VERIFIED",
    "INTENTIONALLY_BACKEND_ONLY",
    "BLOCKED",
    "DEPRECATED",
}
CONSUMER_STATUSES = {"CLIENT_MAPPED", "UI_INTEGRATED", "RUNTIME_VERIFIED", "E2E_VERIFIED"}
ENTRYPOINT_STATUSES = {"UI_INTEGRATED", "RUNTIME_VERIFIED", "E2E_VERIFIED"}
REASON_STATUSES = {"INTENTIONALLY_BACKEND_ONLY", "BLOCKED", "DEPRECATED"}
MERMAID_RE = re.compile(r"```mermaid[^\n]*\n(.*?)```", re.IGNORECASE | re.DOTALL)


@dataclass
class Check:
    name: str
    status: str
    detail: str


def read_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, f"file does not exist: {path}"
    except UnicodeError as exc:
        return None, f"file is not UTF-8: {path} ({exc})"
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON in {path}: line {exc.lineno}, column {exc.colno}"
    except OSError as exc:
        return None, f"cannot read {path}: {exc}"


def repository_file(root: Path, raw: Any, label: str) -> tuple[Path | None, str | None]:
    if not isinstance(raw, str) or not raw.strip():
        return None, f"{label} must be a non-empty repository-relative path"
    relative = Path(raw)
    if relative.is_absolute():
        return None, f"{label} must be repository-relative: {raw}"
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None, f"{label} escapes the repository: {raw}"
    if not candidate.is_file():
        return None, f"{label} does not exist: {raw}"
    return candidate, None


def extract_openapi_operations(document: Any) -> tuple[dict[str, tuple[str, str]], list[str]]:
    operations: dict[str, tuple[str, str]] = {}
    errors: list[str] = []
    if not isinstance(document, dict):
        return operations, ["OpenAPI root must be an object"]
    paths = document.get("paths")
    if not isinstance(paths, dict):
        return operations, ["OpenAPI paths must be an object"]

    for path, path_item in paths.items():
        if not isinstance(path, str) or not isinstance(path_item, dict):
            errors.append(f"invalid OpenAPI path item: {path!r}")
            continue
        for method, operation in path_item.items():
            normalized_method = str(method).lower()
            if normalized_method not in HTTP_METHODS:
                continue
            location = f"{normalized_method.upper()} {path}"
            if not isinstance(operation, dict):
                errors.append(f"{location} operation must be an object")
                continue
            operation_id = operation.get("operationId")
            if not isinstance(operation_id, str) or not operation_id.strip():
                errors.append(f"{location} has no operationId")
                continue
            operation_id = operation_id.strip()
            if operation_id in operations:
                previous_method, previous_path = operations[operation_id]
                errors.append(
                    f"duplicate operationId {operation_id!r}: "
                    f"{previous_method.upper()} {previous_path} and {location}"
                )
                continue
            operations[operation_id] = (normalized_method, path)
    return operations, errors


def mermaid_blocks(path: Path) -> tuple[list[str], str | None]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [], f"cannot read diagram {path}: {exc}"
    return MERMAID_RE.findall(text), None


def contains_symbol(path: Path, symbol: str) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return False
    return re.search(rf"(?<![\w$]){re.escape(symbol)}(?![\w$])", text) is not None


def validate(
    root: Path,
    openapi_path: Path,
    manifest_path: Path,
    allow_partial: bool = False,
) -> list[Check]:
    checks: list[Check] = []
    openapi_document, openapi_read_error = read_json(openapi_path)
    if openapi_read_error:
        return [Check("openapi_contract", "FAIL", openapi_read_error)]

    operations, openapi_errors = extract_openapi_operations(openapi_document)
    checks.append(
        Check(
            "openapi_contract",
            "FAIL" if openapi_errors else "PASS",
            "; ".join(openapi_errors) if openapi_errors else f"{len(operations)} uniquely identified operation(s)",
        )
    )

    manifest, manifest_read_error = read_json(manifest_path)
    if manifest_read_error:
        checks.append(Check("manifest_schema", "FAIL", manifest_read_error))
        return checks
    if not isinstance(manifest, dict):
        checks.append(Check("manifest_schema", "FAIL", "manifest root must be an object"))
        return checks

    schema_errors: list[str] = []
    if manifest.get("schema_version") != 2:
        schema_errors.append("schema_version must be 2")
    mapping_document_value = manifest.get("mapping_document")
    if mapping_document_value != REQUIRED_MAPPING_DOCUMENT:
        schema_errors.append(f"mapping_document must be {REQUIRED_MAPPING_DOCUMENT!r}")
    entries = manifest.get("operations")
    if not isinstance(entries, list):
        schema_errors.append("operations must be an array")
        entries = []
    topology_values = manifest.get("topology_diagrams")
    if not isinstance(topology_values, list) or not topology_values:
        schema_errors.append("topology_diagrams must be a non-empty array")
        topology_values = []
    elif REQUIRED_MAPPING_DOCUMENT not in topology_values:
        schema_errors.append(f"topology_diagrams must include {REQUIRED_MAPPING_DOCUMENT!r}")
    checks.append(
        Check(
            "manifest_schema",
            "FAIL" if schema_errors else "PASS",
            "; ".join(schema_errors) if schema_errors else "schema version 2 with mandatory mapping document",
        )
    )

    mapping_errors: list[str] = []
    consumer_errors: list[str] = []
    sequence_errors: list[str] = []
    mapped_ids: set[str] = set()
    consumer_sequences: dict[str, list[Path]] = {}

    for index, raw_entry in enumerate(entries):
        label = f"operations[{index}]"
        if not isinstance(raw_entry, dict):
            mapping_errors.append(f"{label} must be an object")
            continue
        operation_id = raw_entry.get("operation_id")
        if not isinstance(operation_id, str) or not operation_id.strip():
            mapping_errors.append(f"{label}.operation_id must be non-empty")
            continue
        operation_id = operation_id.strip()
        if operation_id in mapped_ids:
            mapping_errors.append(f"duplicate manifest operation_id: {operation_id}")
            continue
        mapped_ids.add(operation_id)
        if operation_id not in operations:
            mapping_errors.append(f"manifest operation is absent from OpenAPI: {operation_id}")

        owner = raw_entry.get("owner")
        if not isinstance(owner, str) or not owner.strip():
            mapping_errors.append(f"{operation_id}: owner must be non-empty")
        status = raw_entry.get("status")
        if status not in STATUSES:
            mapping_errors.append(f"{operation_id}: invalid status {status!r}")
            status = None
        reason = raw_entry.get("reason", "")
        if status in REASON_STATUSES and (not isinstance(reason, str) or not reason.strip()):
            mapping_errors.append(f"{operation_id}: {status} requires a reason")

        consumers = raw_entry.get("consumers", [])
        if not isinstance(consumers, list):
            consumer_errors.append(f"{operation_id}: consumers must be an array")
            consumers = []
        if status in CONSUMER_STATUSES and not consumers:
            consumer_errors.append(f"{operation_id}: {status} requires at least one consumer")

        for consumer_index, consumer in enumerate(consumers):
            consumer_label = f"{operation_id}.consumers[{consumer_index}]"
            if not isinstance(consumer, dict):
                consumer_errors.append(f"{consumer_label} must be an object")
                continue
            app = consumer.get("app")
            if not isinstance(app, str) or not app.strip():
                consumer_errors.append(f"{consumer_label}.app must be non-empty")
            client, client_error = repository_file(root, consumer.get("client"), f"{consumer_label}.client")
            if client_error:
                consumer_errors.append(client_error)
            symbol = consumer.get("symbol")
            if not isinstance(symbol, str) or not symbol.strip():
                consumer_errors.append(f"{consumer_label}.symbol must be non-empty")
            elif client is not None and not contains_symbol(client, symbol.strip()):
                consumer_errors.append(f"{consumer_label}.symbol {symbol!r} was not found in {consumer.get('client')}")

            entrypoints = consumer.get("entrypoints", [])
            if not isinstance(entrypoints, list):
                consumer_errors.append(f"{consumer_label}.entrypoints must be an array")
                entrypoints = []
            if status in ENTRYPOINT_STATUSES and not entrypoints:
                consumer_errors.append(f"{consumer_label}: {status} requires at least one entrypoint")
            for entrypoint_index, entrypoint in enumerate(entrypoints):
                _, entrypoint_error = repository_file(
                    root,
                    entrypoint,
                    f"{consumer_label}.entrypoints[{entrypoint_index}]",
                )
                if entrypoint_error:
                    consumer_errors.append(entrypoint_error)

        sequence_values = raw_entry.get("sequence_diagrams", [])
        if not isinstance(sequence_values, list):
            sequence_errors.append(f"{operation_id}: sequence_diagrams must be an array")
            sequence_values = []
        if status in CONSUMER_STATUSES and not sequence_values:
            sequence_errors.append(f"{operation_id}: {status} requires a sequence diagram")
        resolved_sequences: list[Path] = []
        for sequence_index, sequence_value in enumerate(sequence_values):
            sequence, sequence_error = repository_file(
                root,
                sequence_value,
                f"{operation_id}.sequence_diagrams[{sequence_index}]",
            )
            if sequence_error:
                sequence_errors.append(sequence_error)
            elif sequence is not None:
                resolved_sequences.append(sequence)
        if status in CONSUMER_STATUSES:
            consumer_sequences[operation_id] = resolved_sequences

    if not allow_partial:
        missing = sorted(set(operations) - mapped_ids)
        if missing:
            mapping_errors.append(f"OpenAPI operations missing from manifest: {', '.join(missing)}")
    elif set(operations) - mapped_ids:
        mapping_errors.append(
            "partial discovery mode: "
            f"{len(set(operations) - mapped_ids)} OpenAPI operation(s) are not classified"
        )

    mapping_status = "FAIL" if mapping_errors and not allow_partial else "PASS"
    if allow_partial and any("partial discovery mode" not in error for error in mapping_errors):
        mapping_status = "FAIL"
    checks.append(
        Check(
            "mapping_contract",
            mapping_status,
            "; ".join(mapping_errors) if mapping_errors else f"{len(mapped_ids)} operation(s) classified",
        )
    )

    mapping_document_errors: list[str] = []
    mapping_document, mapping_document_error = repository_file(
        root,
        mapping_document_value,
        "mapping_document",
    )
    if mapping_document_error:
        mapping_document_errors.append(mapping_document_error)
    elif mapping_document is not None:
        try:
            mapping_text = mapping_document.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            mapping_document_errors.append(f"cannot read mapping_document: {exc}")
        else:
            missing_references = sorted(operation_id for operation_id in mapped_ids if operation_id not in mapping_text)
            if missing_references:
                mapping_document_errors.append(
                    "mapping_document does not reference operationId(s): " + ", ".join(missing_references)
                )
    checks.append(
        Check(
            "mapping_document",
            "FAIL" if mapping_document_errors else "PASS",
            "; ".join(mapping_document_errors)
            if mapping_document_errors
            else f"{REQUIRED_MAPPING_DOCUMENT} references all {len(mapped_ids)} mapped operation(s)",
        )
    )
    checks.append(
        Check(
            "consumer_paths",
            "FAIL" if consumer_errors else "PASS",
            "; ".join(consumer_errors) if consumer_errors else "all declared consumers, symbols, and entrypoints exist",
        )
    )

    topology_errors: list[str] = []
    topology_count = 0
    for index, topology_value in enumerate(topology_values):
        topology, topology_error = repository_file(root, topology_value, f"topology_diagrams[{index}]")
        if topology_error:
            topology_errors.append(topology_error)
            continue
        assert topology is not None
        blocks, block_error = mermaid_blocks(topology)
        if block_error:
            topology_errors.append(block_error)
            continue
        matching = [block for block in blocks if re.search(r"^\s*(?:flowchart|graph)\b", block, re.IGNORECASE)]
        if not matching:
            topology_errors.append(f"{topology_value} has no Mermaid flowchart/graph block")
            continue
        if not any(re.search(r"--?>|==>", block) for block in matching):
            topology_errors.append(f"{topology_value} topology has no relationship arrow")
            continue
        topology_count += 1
    checks.append(
        Check(
            "topology_diagrams",
            "FAIL" if topology_errors or not topology_count else "PASS",
            "; ".join(topology_errors) if topology_errors else f"{topology_count} Mermaid topology diagram(s)",
        )
    )

    for operation_id, paths in consumer_sequences.items():
        matched = False
        for path in paths:
            blocks, block_error = mermaid_blocks(path)
            if block_error:
                sequence_errors.append(block_error)
                continue
            sequence_blocks = [block for block in blocks if re.search(r"^\s*sequenceDiagram\b", block, re.IGNORECASE)]
            for block in sequence_blocks:
                if operation_id in block and re.search(r"(?:->>|-->>|->|-->)", block):
                    matched = True
                    break
            if matched:
                break
        if paths and not matched:
            sequence_errors.append(
                f"{operation_id}: no declared Mermaid sequenceDiagram references the operationId and a message arrow"
            )
    checks.append(
        Check(
            "sequence_diagrams",
            "FAIL" if sequence_errors else "PASS",
            "; ".join(sequence_errors) if sequence_errors else f"{len(consumer_sequences)} consumer-mapped operation(s) have Mermaid sequences",
        )
    )
    return checks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate OpenAPI mapping, real consumers, and Mermaid coverage.")
    parser.add_argument("--project-root", default=".", help="Repository root to inspect.")
    parser.add_argument("--openapi", required=True, help="OpenAPI JSON path, relative to the repository root unless absolute.")
    parser.add_argument("--manifest", required=True, help="API mapping JSON path, relative to the repository root unless absolute.")
    parser.add_argument("--allow-partial", action="store_true", help="Allow unclassified OpenAPI operations during adopted-project discovery only.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def resolve_input(root: Path, value: str) -> Path:
    candidate = Path(value).expanduser()
    return candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()


def main() -> int:
    args = parse_args()
    root = Path(args.project_root).expanduser().resolve()
    if not root.is_dir():
        print(f"Invalid project root: {root}", file=sys.stderr)
        return 2
    openapi_path = resolve_input(root, args.openapi)
    manifest_path = resolve_input(root, args.manifest)
    checks = validate(root, openapi_path, manifest_path, args.allow_partial)
    failures = [check for check in checks if check.status == "FAIL"]
    if args.json:
        print(
            json.dumps(
                {
                    "root": str(root),
                    "openapi": str(openapi_path),
                    "manifest": str(manifest_path),
                    "checks": [asdict(check) for check in checks],
                    "valid": not failures,
                },
                indent=2,
            )
        )
    else:
        for check in checks:
            print(f"{check.status:9} {check.name}: {check.detail}")
        print("API_MAPPING_VALID" if not failures else "API_MAPPING_INVALID")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
