from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_spec_contract.py"
SPEC = importlib.util.spec_from_file_location("validate_spec_contract", SCRIPT)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


class SpecContractValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, relative: str, content: str = "") -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def baseline(self) -> str:
        return (
            "# Authentication Specification\n\n"
            "## Purpose\n\nDefine account access.\n\n"
            "## Requirements\n\n"
            "### Requirement: FR-AUTH-001 Register account\n\n"
            "The system SHALL create one valid account.\n\n"
            "#### Scenario: Valid registration\n\n"
            "- **WHEN** valid data is submitted\n"
            "- **THEN** one account is created\n"
        )

    def proposal(self) -> str:
        return (
            "# Change: Strengthen authentication\n\n"
            "## Why\n\nRegistration needs an explicit duplicate rule.\n\n"
            "## What Changes\n\nModify registration and add logout.\n\n"
            "## Impact\n\nAuthentication API and tests.\n"
        )

    def config(self, schema: str = "spec-driven") -> str:
        return f"schema: {schema}\n"

    def delta(self) -> str:
        return (
            "# Authentication Delta\n\n"
            "## MODIFIED Requirements\n\n"
            "### Requirement: FR-AUTH-001 Register account\n\n"
            "The system SHALL reject duplicate identity.\n\n"
            "#### Scenario: Duplicate registration\n\n"
            "- **WHEN** an existing identity is submitted\n"
            "- **THEN** registration is rejected\n\n"
            "## ADDED Requirements\n\n"
            "### Requirement: FR-AUTH-002 Logout account\n\n"
            "The system SHALL end the active session.\n\n"
            "#### Scenario: Valid logout\n\n"
            "- **WHEN** an authenticated user logs out\n"
            "- **THEN** the session is revoked\n"
        )

    def project_status(self) -> str:
        return (
            "# Project\n\nPortfolio API.\n\n"
            "## Completed\n\n- Baseline.\n\n"
            "## Current work\n\n- Authentication.\n\n"
            "## Not done\n\n- Deployment.\n\n"
            "## Blockers and risks\n\n- None.\n\n"
            "## Next priorities\n\n1. Verify runtime.\n"
        )

    def build_log(self, timestamp: str = "2026-08-04T10:00:00+07:00") -> str:
        return (
            f"## {timestamp} | strengthen-authentication\n\n"
            "- Change: Updated registration behavior.\n"
            "- Why: Match FR-AUTH-001.\n"
            "- How: Changed the owning service.\n"
            "- Evidence: Unit tests PASS.\n"
            "- Result: Technical verification PASS.\n"
            "- Next: Manual acceptance.\n"
        )

    def write_valid_fixture(self) -> None:
        self.write("openspec/config.yaml", self.config())
        self.write("openspec/specs/authentication/spec.md", self.baseline())
        self.write("openspec/changes/strengthen-authentication/.openspec.yaml", "schema: spec-driven\n")
        self.write("openspec/changes/strengthen-authentication/proposal.md", self.proposal())
        self.write("openspec/changes/strengthen-authentication/tasks.md", "# Tasks\n\n- [ ] Update service and tests\n")
        self.write("openspec/changes/strengthen-authentication/specs/authentication/spec.md", self.delta())
        self.write("PROJECTSTATUS.md", self.project_status())
        self.write("BUILDLOG.md", self.build_log())

    def checks(
        self,
        require_openspec: bool = True,
        require_records: bool = True,
        spec_language: str | None = None,
    ) -> list[validator.Check]:
        return validator.validate(
            self.root,
            require_openspec,
            require_records,
            spec_language,
        )

    def check(
        self,
        name: str,
        require_openspec: bool = True,
        require_records: bool = True,
        spec_language: str | None = None,
    ) -> validator.Check:
        return next(
            item
            for item in self.checks(require_openspec, require_records, spec_language)
            if item.name == name
        )

    def test_valid_brownfield_delta_and_project_records_pass(self) -> None:
        self.write_valid_fixture()
        failures = [item for item in self.checks() if item.status == "FAIL"]
        self.assertEqual(failures, [])
        self.assertIn("2 delta operation", self.check("delta_semantics").detail)

    def test_missing_openspec_is_optional_unless_required(self) -> None:
        optional = self.check("openspec_layout", False, False)
        required = self.check("openspec_layout", True, False)
        self.assertEqual(optional.status, "N/A")
        self.assertEqual(required.status, "FAIL")

    def test_fresh_openspec_init_layout_passes_without_baseline_or_changes(self) -> None:
        self.write("openspec/config.yaml", self.config())
        self.write("openspec/specs/.gitkeep")
        self.write("openspec/changes/archive/.gitkeep")
        failures = [item for item in self.checks(True, False) if item.status in {"FAIL", "BLOCKED"}]
        self.assertEqual(failures, [])

    def test_baseline_requirement_needs_scenario(self) -> None:
        self.write_valid_fixture()
        self.write(
            "openspec/specs/authentication/spec.md",
            "# Auth\n\n## Purpose\n\nAuth.\n\n## Requirements\n\n### Requirement: FR-AUTH-001 Register account\n\nRule.\n",
        )
        result = self.check("baseline_specs")
        self.assertEqual(result.status, "FAIL")
        self.assertIn("has no '#### Scenario:'", result.detail)

    def test_active_change_requires_proposal_tasks_and_delta(self) -> None:
        self.write("openspec/config.yaml", self.config())
        self.write("openspec/specs/authentication/spec.md", self.baseline())
        self.write("openspec/changes/empty-change/placeholder.md")
        result = self.check("active_changes", True, False)
        self.assertEqual(result.status, "FAIL")
        self.assertIn("proposal.md", result.detail)
        self.assertIn("tasks.md", result.detail)
        self.assertIn("delta", result.detail)
        self.assertIn(".openspec.yaml", result.detail)

    def test_delta_accepts_added_existing_but_rejects_modified_missing_requirement(self) -> None:
        self.write_valid_fixture()
        invalid = self.delta().replace(
            "FR-AUTH-001 Register account",
            "FR-AUTH-999 Missing account",
            1,
        ).replace(
            "FR-AUTH-002 Logout account",
            "FR-AUTH-001 Register account",
            1,
        )
        self.write("openspec/changes/strengthen-authentication/specs/authentication/spec.md", invalid)
        result = self.check("delta_semantics")
        self.assertEqual(result.status, "FAIL")
        self.assertIn("MODIFIED requirement is absent", result.detail)
        self.assertNotIn("ADDED requirement already exists", result.detail)

    def test_partial_modified_removed_and_renamed_delta_matches_openspec(self) -> None:
        self.write_valid_fixture()
        extended_baseline = self.baseline() + (
            "\n### Requirement: FR-AUTH-002 Logout account\n\n"
            "The system SHALL end the active session.\n\n"
            "#### Scenario: Valid logout\n\n"
            "- **WHEN** an authenticated user logs out\n"
            "- **THEN** the session is revoked\n\n"
            "### Requirement: FR-AUTH-003 Old account label\n\n"
            "The system SHALL expose the account label.\n\n"
            "#### Scenario: Read label\n\n"
            "- **WHEN** the account is viewed\n"
            "- **THEN** its label is returned\n"
        )
        self.write("openspec/specs/authentication/spec.md", extended_baseline)
        delta = (
            "## MODIFIED Requirements\n\n"
            "### Requirement: FR-AUTH-001 Register account\n\n"
            "The system SHALL also audit duplicate attempts.\n\n"
            "## REMOVED Requirements\n\n"
            "### Requirement: FR-AUTH-002 Logout account\n\n"
            "## RENAMED Requirements\n\n"
            "- FROM: `### Requirement: FR-AUTH-003 Old account label`\n"
            "- TO: `### Requirement: FR-AUTH-003 Account label`\n"
        )
        self.write("openspec/changes/strengthen-authentication/specs/authentication/spec.md", delta)
        result = self.check("delta_semantics")
        self.assertEqual(result.status, "PASS")
        self.assertNotIn("has no '#### Scenario:'", result.detail)

    def test_change_can_explicitly_skip_specs(self) -> None:
        self.write_valid_fixture()
        delta_path = self.root / "openspec/changes/strengthen-authentication/specs/authentication/spec.md"
        delta_path.unlink()
        self.write(
            "openspec/changes/strengthen-authentication/.openspec.yaml",
            "schema: spec-driven\nskip_specs: true\n",
        )
        result = self.check("active_changes")
        self.assertEqual(result.status, "PASS")

    def test_custom_schema_requires_compatible_cli(self) -> None:
        self.write("openspec/config.yaml", self.config("research-first"))
        self.write("openspec/specs/.gitkeep")
        self.write("openspec/changes/archive/.gitkeep")
        result = self.check("active_changes", True, False)
        self.assertEqual(result.status, "BLOCKED")
        self.assertIn("compatible OpenSpec CLI", result.detail)

    def test_delta_requires_exact_operation_heading(self) -> None:
        self.write_valid_fixture()
        self.write(
            "openspec/changes/strengthen-authentication/specs/authentication/spec.md",
            self.delta().replace("## ADDED Requirements", "## New requirements").replace("## MODIFIED Requirements", "## Changed requirements"),
        )
        result = self.check("delta_semantics")
        self.assertEqual(result.status, "FAIL")
        self.assertIn("no ADDED/MODIFIED/REMOVED", result.detail)

    def test_vietnamese_spec_language_contract_passes(self) -> None:
        self.write_valid_fixture()
        marker = "<!-- easy2dev-spec-language: vi -->\n\n"
        baseline = (
            marker
            + self.baseline()
            .replace("Authentication Specification", "Đặc tả xác thực")
            .replace("Define account access.", "Xác định hành vi truy cập tài khoản.")
            .replace("Register account", "Đăng ký tài khoản")
            .replace("The system SHALL create one valid account.", "Hệ thống PHẢI tạo đúng một tài khoản hợp lệ.")
            .replace("Valid registration", "Đăng ký hợp lệ")
            .replace("valid data is submitted", "khách gửi dữ liệu hợp lệ")
            .replace("one account is created", "một tài khoản được tạo")
        )
        delta = (
            marker
            + self.delta()
            .replace("Authentication Delta", "Thay đổi đặc tả xác thực")
            .replace("Register account", "Đăng ký tài khoản")
            .replace("The system SHALL reject duplicate identity.", "Hệ thống PHẢI từ chối danh tính trùng lặp.")
            .replace("Duplicate registration", "Đăng ký trùng lặp")
            .replace("an existing identity is submitted", "người dùng gửi danh tính đã tồn tại")
            .replace("registration is rejected", "yêu cầu đăng ký bị từ chối")
            .replace("Logout account", "Đăng xuất tài khoản")
            .replace("The system SHALL end the active session.", "Hệ thống PHẢI kết thúc phiên đang hoạt động.")
            .replace("Valid logout", "Đăng xuất hợp lệ")
            .replace("an authenticated user logs out", "người dùng đã xác thực đăng xuất")
            .replace("the session is revoked", "phiên bị thu hồi")
        )
        self.write("openspec/specs/authentication/spec.md", baseline)
        self.write(
            "openspec/changes/strengthen-authentication/specs/authentication/spec.md",
            delta,
        )
        result = self.check("spec_language", spec_language="vi")
        self.assertEqual(result.status, "PASS")
        self.assertIn("2 current spec file", result.detail)

    def test_spec_language_contract_rejects_missing_or_wrong_marker(self) -> None:
        self.write_valid_fixture()
        missing = self.check("spec_language", spec_language="vi")
        self.assertEqual(missing.status, "FAIL")
        self.assertIn("has no", missing.detail)

        marker = "<!-- easy2dev-spec-language: en -->\n\n"
        self.write("openspec/specs/authentication/spec.md", marker + self.baseline())
        self.write(
            "openspec/changes/strengthen-authentication/specs/authentication/spec.md",
            marker + self.delta(),
        )
        wrong = self.check("spec_language", spec_language="vi")
        self.assertEqual(wrong.status, "FAIL")
        self.assertIn("expected 'vi'", wrong.detail)

    def test_spec_language_contract_rejects_english_prose_marked_as_vietnamese(self) -> None:
        self.write_valid_fixture()
        marker = "<!-- easy2dev-spec-language: vi -->\n\n"
        self.write("openspec/specs/authentication/spec.md", marker + self.baseline())
        self.write(
            "openspec/changes/strengthen-authentication/specs/authentication/spec.md",
            marker + self.delta(),
        )
        result = self.check("spec_language", spec_language="vi")
        self.assertEqual(result.status, "FAIL")
        self.assertIn("no Vietnamese-language prose evidence", result.detail)

    def test_project_status_must_be_concise_and_complete(self) -> None:
        self.write_valid_fixture()
        self.write("PROJECTSTATUS.md", "# Project\n" + "line\n" * 301)
        result = self.check("project_status")
        self.assertEqual(result.status, "FAIL")
        self.assertIn("maximum is 300", result.detail)
        self.assertIn("no heading", result.detail)

    def test_build_log_must_be_newest_first(self) -> None:
        self.write_valid_fixture()
        older = self.build_log("2026-08-03T10:00:00+07:00")
        newer = self.build_log("2026-08-04T10:00:00+07:00")
        self.write("BUILDLOG.md", older + "\n==========\n\n" + newer)
        result = self.check("build_log")
        self.assertEqual(result.status, "FAIL")
        self.assertIn("not newest first", result.detail)

    def test_each_build_log_entry_requires_all_fields(self) -> None:
        self.write_valid_fixture()
        incomplete = "## 2026-08-03T10:00:00+07:00 | incomplete\n\n- Change: Partial entry.\n"
        self.write("BUILDLOG.md", self.build_log() + "\n==========\n\n" + incomplete)
        result = self.check("build_log")
        self.assertEqual(result.status, "FAIL")
        self.assertIn("incomplete", result.detail)
        self.assertIn("has no why field", result.detail)

    def test_archive_requires_dated_name_and_records(self) -> None:
        self.write_valid_fixture()
        self.write("openspec/changes/archive/bad-name/placeholder.md")
        result = self.check("archive_layout")
        self.assertEqual(result.status, "FAIL")
        self.assertIn("YYYY-MM-DD", result.detail)
        self.assertIn("proposal.md", result.detail)

    def test_archived_easy2dev_delivery_cannot_have_incomplete_tasks(self) -> None:
        self.write("openspec/config.yaml", self.config())
        self.write("openspec/specs/.gitkeep")
        archive = "openspec/changes/archive/2026-08-04-finished-change"
        self.write(f"{archive}/.openspec.yaml", "schema: spec-driven\n")
        self.write(f"{archive}/proposal.md", self.proposal())
        self.write(f"{archive}/tasks.md", "# Tasks\n\n- [ ] Not actually complete\n")
        result = self.check("archive_layout", True, False)
        self.assertEqual(result.status, "FAIL")
        self.assertIn("incomplete tasks", result.detail)


if __name__ == "__main__":
    unittest.main()
