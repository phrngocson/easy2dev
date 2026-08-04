from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_api_mapping.py"
SPEC = importlib.util.spec_from_file_location("validate_api_mapping", SCRIPT)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


class ApiMappingValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.openapi_path = self.root / "openapi.json"
        self.manifest_path = self.root / "docs" / "api-map.json"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, relative: str, content: str = "") -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def write_json(self, relative: str, content: object) -> None:
        self.write(relative, json.dumps(content, indent=2))

    def openapi(self, include_detail: bool = False) -> dict[str, object]:
        paths: dict[str, object] = {
            "/api/projects": {"get": {"operationId": "list_projects", "responses": {"200": {"description": "ok"}}}}
        }
        if include_detail:
            paths["/api/projects/{project_id}"] = {
                "get": {"operationId": "get_project", "responses": {"200": {"description": "ok"}}}
            }
        return {"openapi": "3.1.0", "info": {"title": "Fixture", "version": "1"}, "paths": paths}

    def valid_manifest(self) -> dict[str, object]:
        return {
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
                            "entrypoints": ["frontend/app/projects/page.tsx"],
                        }
                    ],
                    "sequence_diagrams": ["docs/features/projects/SEQUENCE.md"],
                    "reason": "",
                }
            ],
        }

    def write_valid_fixture(self) -> None:
        self.write_json("openapi.json", self.openapi())
        self.write_json("docs/api-map.json", self.valid_manifest())
        self.write("frontend/lib/api/projects.ts", "export async function listProjects() { return []; }\n")
        self.write("frontend/app/projects/page.tsx", "import { listProjects } from '../../lib/api/projects';\n")
        self.write(
            "docs/API_MAPPING.md",
            "# Current API mapping\n\n| operationId | Consumer |\n|---|---|\n| `list_projects` | frontend |\n\n```mermaid\nflowchart LR\n  UI --> API\n```\n",
        )
        self.write(
            "docs/features/projects/SEQUENCE.md",
            "# Implemented flow\n\n```mermaid\nsequenceDiagram\n  UI->>API: list_projects\n  API-->>UI: 200\n```\n",
        )

    def failures(self, allow_partial: bool = False) -> list[validator.Check]:
        checks = validator.validate(self.root, self.openapi_path, self.manifest_path, allow_partial)
        return [check for check in checks if check.status == "FAIL"]

    def test_complete_mapping_with_real_consumers_and_diagrams_passes(self) -> None:
        self.write_valid_fixture()
        self.assertEqual(self.failures(), [])

    def test_unclassified_openapi_operation_fails_strict_but_is_reported_in_discovery(self) -> None:
        self.write_valid_fixture()
        self.write_json("openapi.json", self.openapi(include_detail=True))
        strict = validator.validate(self.root, self.openapi_path, self.manifest_path, False)
        strict_mapping = next(check for check in strict if check.name == "mapping_contract")
        self.assertEqual(strict_mapping.status, "FAIL")
        self.assertIn("get_project", strict_mapping.detail)

        discovery = validator.validate(self.root, self.openapi_path, self.manifest_path, True)
        discovery_mapping = next(check for check in discovery if check.name == "mapping_contract")
        self.assertEqual(discovery_mapping.status, "PASS")
        self.assertIn("partial discovery mode", discovery_mapping.detail)

    def test_manifest_cannot_invent_an_operation(self) -> None:
        self.write_valid_fixture()
        manifest = self.valid_manifest()
        manifest["operations"][0]["operation_id"] = "invented_route"  # type: ignore[index]
        self.write_json("docs/api-map.json", manifest)
        mapping = next(
            check
            for check in validator.validate(self.root, self.openapi_path, self.manifest_path)
            if check.name == "mapping_contract"
        )
        self.assertEqual(mapping.status, "FAIL")
        self.assertIn("absent from OpenAPI", mapping.detail)

    def test_missing_consumer_file_and_symbol_fail(self) -> None:
        self.write_valid_fixture()
        manifest = self.valid_manifest()
        consumer = manifest["operations"][0]["consumers"][0]  # type: ignore[index]
        consumer["client"] = "frontend/lib/api/missing.ts"
        self.write_json("docs/api-map.json", manifest)
        consumer_check = next(
            check
            for check in validator.validate(self.root, self.openapi_path, self.manifest_path)
            if check.name == "consumer_paths"
        )
        self.assertEqual(consumer_check.status, "FAIL")
        self.assertIn("does not exist", consumer_check.detail)

        consumer["client"] = "frontend/lib/api/projects.ts"
        consumer["symbol"] = "inventedClient"
        self.write_json("docs/api-map.json", manifest)
        consumer_check = next(
            check
            for check in validator.validate(self.root, self.openapi_path, self.manifest_path)
            if check.name == "consumer_paths"
        )
        self.assertEqual(consumer_check.status, "FAIL")
        self.assertIn("was not found", consumer_check.detail)

    def test_backend_only_blocked_and_deprecated_statuses_require_reason(self) -> None:
        self.write_valid_fixture()
        for status in ("INTENTIONALLY_BACKEND_ONLY", "BLOCKED", "DEPRECATED"):
            manifest = self.valid_manifest()
            operation = manifest["operations"][0]  # type: ignore[index]
            operation["status"] = status
            operation["consumers"] = []
            operation["sequence_diagrams"] = []
            operation["reason"] = ""
            self.write_json("docs/api-map.json", manifest)
            mapping = next(
                check
                for check in validator.validate(self.root, self.openapi_path, self.manifest_path)
                if check.name == "mapping_contract"
            )
            self.assertEqual(mapping.status, "FAIL")
            self.assertIn("requires a reason", mapping.detail)

    def test_sequence_must_reference_exact_operation_id_inside_mermaid(self) -> None:
        self.write_valid_fixture()
        self.write(
            "docs/features/projects/SEQUENCE.md",
            "list_projects in prose only\n\n```mermaid\nsequenceDiagram\n  UI->>API: wrong_operation\n```\n",
        )
        sequence = next(
            check
            for check in validator.validate(self.root, self.openapi_path, self.manifest_path)
            if check.name == "sequence_diagrams"
        )
        self.assertEqual(sequence.status, "FAIL")
        self.assertIn("list_projects", sequence.detail)

    def test_mandatory_mapping_document_must_exist_and_reference_each_operation(self) -> None:
        self.write_valid_fixture()
        (self.root / "docs" / "API_MAPPING.md").unlink()
        document_check = next(
            check
            for check in validator.validate(self.root, self.openapi_path, self.manifest_path)
            if check.name == "mapping_document"
        )
        self.assertEqual(document_check.status, "FAIL")
        self.assertIn("does not exist", document_check.detail)

        self.write(
            "docs/API_MAPPING.md",
            "# Current API mapping\n\n```mermaid\nflowchart LR\n  UI --> API\n```\n",
        )
        document_check = next(
            check
            for check in validator.validate(self.root, self.openapi_path, self.manifest_path)
            if check.name == "mapping_document"
        )
        self.assertEqual(document_check.status, "FAIL")
        self.assertIn("list_projects", document_check.detail)

    def test_openapi_requires_unique_operation_ids(self) -> None:
        self.write_valid_fixture()
        document = self.openapi(include_detail=True)
        document["paths"]["/api/projects/{project_id}"]["get"]["operationId"] = "list_projects"  # type: ignore[index]
        self.write_json("openapi.json", document)
        contract = next(
            check
            for check in validator.validate(self.root, self.openapi_path, self.manifest_path)
            if check.name == "openapi_contract"
        )
        self.assertEqual(contract.status, "FAIL")
        self.assertIn("duplicate operationId", contract.detail)

    def test_repository_paths_cannot_escape_root(self) -> None:
        self.write_valid_fixture()
        manifest = self.valid_manifest()
        manifest["topology_diagrams"] = ["../outside.md"]
        self.write_json("docs/api-map.json", manifest)
        topology = next(
            check
            for check in validator.validate(self.root, self.openapi_path, self.manifest_path)
            if check.name == "topology_diagrams"
        )
        self.assertEqual(topology.status, "FAIL")
        self.assertIn("escapes the repository", topology.detail)


if __name__ == "__main__":
    unittest.main()
