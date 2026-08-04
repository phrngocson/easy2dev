#!/usr/bin/env python3
"""Validate default OpenSpec spec-driven deltas and optional project records."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


CAPABILITY_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUIREMENT_RE = re.compile(r"^### Requirement:\s*(.+?)\s*$", re.MULTILINE)
SCENARIO_RE = re.compile(r"^#### Scenario:\s*.+$", re.MULTILINE)
DELTA_SECTION_RE = re.compile(
    r"^## (ADDED|MODIFIED|REMOVED|RENAMED) Requirements\s*$",
    re.MULTILINE,
)
TASK_RE = re.compile(r"^- \[[ xX]\]\s+\S", re.MULTILINE)
INCOMPLETE_TASK_RE = re.compile(r"^- \[ \]\s+\S", re.MULTILINE)
SCHEMA_RE = re.compile(r"^\s*schema:\s*['\"]?([^#'\"\s]+)", re.MULTILINE)
SKIP_SPECS_RE = re.compile(r"^\s*skip_specs:\s*true\s*(?:#.*)?$", re.IGNORECASE | re.MULTILINE)
RENAMED_FROM_RE = re.compile(
    r"^-\s*FROM:\s*`?### Requirement:\s*(.+?)`?\s*$",
    re.MULTILINE,
)
RENAMED_TO_RE = re.compile(
    r"^-\s*TO:\s*`?### Requirement:\s*(.+?)`?\s*$",
    re.MULTILINE,
)
BUILDLOG_HEADER_RE = re.compile(
    r"^##\s+(\d{4}-\d{2}-\d{2}(?:T[^|\r\n]+)?)\s*\|[^\r\n]*",
    re.MULTILINE,
)


@dataclass
class Check:
    name: str
    status: str
    detail: str


def read_text(path: Path) -> tuple[str, str | None]:
    try:
        return path.read_text(encoding="utf-8"), None
    except FileNotFoundError:
        return "", f"file does not exist: {path}"
    except UnicodeError as exc:
        return "", f"file is not UTF-8: {path} ({exc})"
    except OSError as exc:
        return "", f"cannot read {path}: {exc}"


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def requirement_blocks(text: str) -> list[tuple[str, str]]:
    matches = list(REQUIREMENT_RE.finditer(text))
    blocks: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append((match.group(1).strip(), text[match.end() : end]))
    return blocks


def validate_requirement_blocks(
    text: str,
    label: str,
    *,
    require_scenario: bool = True,
) -> tuple[set[str], list[str]]:
    titles: set[str] = set()
    errors: list[str] = []
    blocks = requirement_blocks(text)
    if not blocks:
        return titles, [f"{label} has no '### Requirement:' block"]
    for title, body in blocks:
        if title in titles:
            errors.append(f"{label} duplicates requirement {title!r}")
        titles.add(title)
        if require_scenario and not SCENARIO_RE.search(body):
            errors.append(f"{label} requirement {title!r} has no '#### Scenario:'")
    return titles, errors


def baseline_specs(root: Path, specs_root: Path) -> tuple[dict[str, set[str]], list[str]]:
    requirements: dict[str, set[str]] = {}
    errors: list[str] = []
    if not specs_root.is_dir():
        return requirements, ["openspec/specs does not exist"]
    files = sorted(specs_root.glob("*/spec.md"))
    unexpected = sorted(path for path in specs_root.rglob("spec.md") if path not in files)
    for path in unexpected:
        errors.append(f"baseline spec must be openspec/specs/<capability>/spec.md: {relative(path, root)}")
    for path in files:
        capability = path.parent.name
        label = relative(path, root)
        if not CAPABILITY_RE.fullmatch(capability):
            errors.append(f"{label} capability must use lowercase hyphen-case")
        text, read_error = read_text(path)
        if read_error:
            errors.append(read_error)
            continue
        if not re.search(r"^## Purpose\s*$", text, re.MULTILINE):
            errors.append(f"{label} has no '## Purpose'")
        if not re.search(r"^## Requirements\s*$", text, re.MULTILINE):
            errors.append(f"{label} has no '## Requirements'")
        titles, block_errors = validate_requirement_blocks(text, label)
        errors.extend(block_errors)
        requirements[capability] = titles
    return requirements, errors


def proposal_errors(path: Path, root: Path) -> list[str]:
    label = relative(path, root)
    text, read_error = read_text(path)
    if read_error:
        return [read_error]
    errors = []
    for heading in ("Why", "What Changes", "Impact"):
        if not re.search(rf"^## {re.escape(heading)}\s*$", text, re.MULTILINE):
            errors.append(f"{label} has no '## {heading}'")
    return errors


def tasks_errors(path: Path, root: Path) -> list[str]:
    label = relative(path, root)
    text, read_error = read_text(path)
    if read_error:
        return [read_error]
    return [] if TASK_RE.search(text) else [f"{label} has no Markdown task checkbox"]


def openspec_schema(root: Path, openspec_root: Path) -> tuple[str | None, list[str]]:
    candidates = [path for path in (openspec_root / "config.yaml", openspec_root / "config.yml") if path.is_file()]
    if not candidates:
        return None, ["openspec/config.yaml or config.yml does not exist"]
    if len(candidates) > 1:
        return None, ["both openspec/config.yaml and config.yml exist; configuration source is ambiguous"]
    text, read_error = read_text(candidates[0])
    if read_error:
        return None, [read_error]
    match = SCHEMA_RE.search(text)
    if not match:
        return None, [f"{relative(candidates[0], root)} has no top-level schema"]
    return match.group(1), []


def change_skips_specs(change: Path) -> bool:
    text, error = read_text(change / ".openspec.yaml")
    return error is None and bool(SKIP_SPECS_RE.search(text))


def delta_sections(text: str) -> list[tuple[str, str]]:
    matches = list(DELTA_SECTION_RE.finditer(text))
    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append((match.group(1), text[match.end() : end]))
    return sections


def validate_delta_file(
    path: Path,
    root: Path,
    baseline: dict[str, set[str]],
) -> tuple[int, list[str]]:
    label = relative(path, root)
    capability = path.parent.name
    text, read_error = read_text(path)
    if read_error:
        return 0, [read_error]
    sections = delta_sections(text)
    if not sections:
        return 0, [f"{label} has no ADDED/MODIFIED/REMOVED/RENAMED Requirements section"]
    errors: list[str] = []
    seen: set[str] = set()
    operation_count = 0
    accepted = baseline.get(capability, set())
    for operation, section in sections:
        if operation == "RENAMED":
            from_titles = [item.strip().rstrip("`") for item in RENAMED_FROM_RE.findall(section)]
            to_titles = [item.strip().rstrip("`") for item in RENAMED_TO_RE.findall(section)]
            if not from_titles or len(from_titles) != len(to_titles):
                errors.append(f"{label} RENAMED Requirements needs paired FROM and TO entries")
            for old_title, new_title in zip(from_titles, to_titles):
                operation_count += 1
                if old_title not in accepted:
                    errors.append(f"{label} RENAMED requirement is absent from baseline: {old_title}")
                if old_title == new_title:
                    errors.append(f"{label} RENAMED requirement keeps the same name: {old_title}")
            continue
        titles, block_errors = validate_requirement_blocks(
            section,
            f"{label} {operation}",
            require_scenario=operation == "ADDED",
        )
        errors.extend(block_errors)
        for title in titles:
            operation_count += 1
            if title in seen:
                errors.append(f"{label} repeats requirement {title!r} across delta sections")
            seen.add(title)
            if operation in {"MODIFIED", "REMOVED"} and title not in accepted:
                errors.append(f"{label} {operation} requirement is absent from baseline: {title}")
    return operation_count, errors


def active_change_checks(
    root: Path,
    changes_root: Path,
    baseline: dict[str, set[str]],
) -> tuple[list[str], list[str], int]:
    structure_errors: list[str] = []
    delta_errors: list[str] = []
    delta_operations = 0
    if not changes_root.is_dir():
        return ["openspec/changes does not exist"], delta_errors, delta_operations
    changes = sorted(
        path for path in changes_root.iterdir() if path.is_dir() and path.name != "archive"
    )
    for change in changes:
        if not CAPABILITY_RE.fullmatch(change.name):
            structure_errors.append(f"active change must use lowercase hyphen-case: {change.name}")
        metadata = change / ".openspec.yaml"
        if not metadata.is_file():
            structure_errors.append(f"{relative(change, root)} is missing .openspec.yaml")
        proposal = change / "proposal.md"
        tasks = change / "tasks.md"
        structure_errors.extend(proposal_errors(proposal, root))
        structure_errors.extend(tasks_errors(tasks, root))
        delta_root = change / "specs"
        delta_files = sorted(delta_root.glob("*/spec.md")) if delta_root.is_dir() else []
        skips_specs = change_skips_specs(change)
        if not delta_files and not skips_specs:
            structure_errors.append(f"{relative(change, root)} has no specs/<capability>/spec.md delta")
        if delta_files and skips_specs:
            structure_errors.append(f"{relative(change, root)} declares skip_specs but contains delta specs")
        for delta_file in delta_files:
            capability = delta_file.parent.name
            if not CAPABILITY_RE.fullmatch(capability):
                delta_errors.append(f"{relative(delta_file, root)} capability must use lowercase hyphen-case")
            count, errors = validate_delta_file(delta_file, root, baseline)
            delta_operations += count
            delta_errors.extend(errors)
    return structure_errors, delta_errors, delta_operations


def archive_errors(root: Path, archive_root: Path) -> list[str]:
    if not archive_root.exists():
        return []
    if not archive_root.is_dir():
        return ["openspec/changes/archive must be a directory"]
    errors = []
    for change in sorted(path for path in archive_root.iterdir() if path.is_dir()):
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*", change.name):
            errors.append(f"archived change must use YYYY-MM-DD-<change-id>: {relative(change, root)}")
        for required in ("proposal.md", "tasks.md"):
            if not (change / required).is_file():
                errors.append(f"archived change is missing {required}: {relative(change, root)}")
        if not (change / ".openspec.yaml").is_file():
            errors.append(f"archived change is missing .openspec.yaml: {relative(change, root)}")
        tasks_path = change / "tasks.md"
        if tasks_path.is_file():
            tasks_text, read_error = read_text(tasks_path)
            if read_error:
                errors.append(read_error)
            elif INCOMPLETE_TASK_RE.search(tasks_text):
                errors.append(f"archived Easy2Dev delivery has incomplete tasks: {relative(change, root)}")
    return errors


def project_status_check(root: Path, required: bool) -> Check:
    path = root / "PROJECTSTATUS.md"
    if not path.is_file():
        return Check(
            "project_status",
            "FAIL" if required else "N/A",
            "PROJECTSTATUS.md is required by the project-record profile" if required else "PROJECTSTATUS.md is not adopted",
        )
    text, read_error = read_text(path)
    if read_error:
        return Check("project_status", "FAIL", read_error)
    errors = []
    line_count = len(text.splitlines())
    if line_count > 300:
        errors.append(f"PROJECTSTATUS.md has {line_count} lines; maximum is 300")
    required_concepts = {
        "project identity": r"(?im)^#{1,3} .*\b(project|dự án)\b",
        "completed": r"(?im)^#{1,3} .*\b(completed|done|hoàn thành)\b",
        "active work": r"(?im)^#{1,3} .*\b(current|active|in progress|đang làm)\b",
        "incomplete": r"(?im)^#{1,3} .*\b(not done|incomplete|chưa làm|out of scope)\b",
        "blockers": r"(?im)^#{1,3} .*\b(blocker|blockers|risk|risks|rủi ro)\b",
        "next priorities": r"(?im)^#{1,3} .*\b(next|priority|priorities|tiếp theo|ưu tiên)\b",
    }
    for concept, pattern in required_concepts.items():
        if not re.search(pattern, text):
            errors.append(f"PROJECTSTATUS.md has no heading for {concept}")
    return Check(
        "project_status",
        "FAIL" if errors else "PASS",
        "; ".join(errors) if errors else f"concise current snapshot ({line_count} lines)",
    )


def parse_log_time(value: str) -> float | None:
    candidate = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        try:
            parsed = datetime.fromisoformat(candidate[:10])
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.timestamp()


def build_log_check(root: Path, required: bool) -> Check:
    path = root / "BUILDLOG.md"
    if not path.is_file():
        return Check(
            "build_log",
            "FAIL" if required else "N/A",
            "BUILDLOG.md is required by the project-record profile" if required else "BUILDLOG.md is not adopted",
        )
    text, read_error = read_text(path)
    if read_error:
        return Check("build_log", "FAIL", read_error)
    errors = []
    header_matches = list(BUILDLOG_HEADER_RE.finditer(text))
    headers = [match.group(1) for match in header_matches]
    if not header_matches:
        errors.append("BUILDLOG.md has no ISO-dated '## <time> | <scope>' entry")
    times = [parse_log_time(value) for value in headers]
    if any(value is None for value in times):
        errors.append("BUILDLOG.md contains an invalid entry time")
    elif any(times[index] < times[index + 1] for index in range(len(times) - 1)):  # type: ignore[operator]
        errors.append("BUILDLOG.md entries are not newest first")
    if len(headers) > 1 and "==========" not in text:
        errors.append("BUILDLOG.md entries are not separated by ==========")
    concepts = {
        "change": r"(?im)^- (Change|Việc làm):",
        "why": r"(?im)^- (Why|Lý do):",
        "how": r"(?im)^- (How|Cách làm):",
        "evidence": r"(?im)^- (Evidence|Bằng chứng):",
        "result": r"(?im)^- (Result|Kết quả):",
        "next": r"(?im)^- (Next|Bước tiếp theo):",
    }
    for index, header in enumerate(header_matches):
        end = header_matches[index + 1].start() if index + 1 < len(header_matches) else len(text)
        body = text[header.end() : end]
        for concept, pattern in concepts.items():
            if not re.search(pattern, body):
                entry_label = header.group(0).removeprefix("##").strip()
                errors.append(f"BUILDLOG.md entry {entry_label!r} has no {concept} field")
    return Check(
        "build_log",
        "FAIL" if errors else "PASS",
        "; ".join(errors) if errors else f"{len(headers)} curated entry/entries, newest first",
    )


def validate(root: Path, require_openspec: bool, require_project_records: bool) -> list[Check]:
    checks: list[Check] = []
    openspec_root = root / "openspec"
    if not openspec_root.is_dir():
        status = "FAIL" if require_openspec else "N/A"
        detail = "openspec/ is required" if require_openspec else "openspec/ is not adopted"
        checks.extend(
            [
                Check("openspec_layout", status, detail),
                Check("openspec_schema", status, detail),
                Check("baseline_specs", status, detail),
                Check("active_changes", status, detail),
                Check("delta_semantics", status, detail),
                Check("archive_layout", status, detail),
            ]
        )
    else:
        checks.append(Check("openspec_layout", "PASS", "tracked openspec/ contract exists"))
        schema, schema_errors = openspec_schema(root, openspec_root)
        checks.append(
            Check(
                "openspec_schema",
                "FAIL" if schema_errors else "PASS",
                "; ".join(schema_errors) if schema_errors else f"schema is {schema}",
            )
        )
        if not schema_errors and schema != "spec-driven":
            detail = f"custom schema {schema!r} requires compatible OpenSpec CLI validation"
            checks.extend(
                [
                    Check("baseline_specs", "BLOCKED", detail),
                    Check("active_changes", "BLOCKED", detail),
                    Check("delta_semantics", "BLOCKED", detail),
                    Check("archive_layout", "BLOCKED", detail),
                ]
            )
            checks.append(project_status_check(root, require_project_records))
            checks.append(build_log_check(root, require_project_records))
            return checks
        baseline, baseline_error_list = baseline_specs(root, openspec_root / "specs")
        checks.append(
            Check(
                "baseline_specs",
                "FAIL" if baseline_error_list else "PASS",
                "; ".join(baseline_error_list)
                if baseline_error_list
                else f"{len(baseline)} accepted capability spec(s)",
            )
        )
        structure_errors, delta_errors, delta_count = active_change_checks(
            root,
            openspec_root / "changes",
            baseline,
        )
        checks.append(
            Check(
                "active_changes",
                "FAIL" if structure_errors else "PASS",
                "; ".join(structure_errors) if structure_errors else "active change structure is valid",
            )
        )
        checks.append(
            Check(
                "delta_semantics",
                "FAIL" if delta_errors else "PASS",
                "; ".join(delta_errors) if delta_errors else f"{delta_count} delta operation(s) are structurally valid",
            )
        )
        archived_errors = archive_errors(root, openspec_root / "changes" / "archive")
        checks.append(
            Check(
                "archive_layout",
                "FAIL" if archived_errors else "PASS",
                "; ".join(archived_errors) if archived_errors else "archive naming and required records are valid",
            )
        )
    checks.append(project_status_check(root, require_project_records))
    checks.append(build_log_check(root, require_project_records))
    return checks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate default OpenSpec spec-driven deltas and project records.")
    parser.add_argument("--project-root", default=".", help="Repository root to inspect.")
    parser.add_argument("--require-openspec", action="store_true", help="Fail when the tracked openspec/ contract is absent.")
    parser.add_argument("--require-project-records", action="store_true", help="Require PROJECTSTATUS.md and BUILDLOG.md.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.project_root).expanduser().resolve()
    if not root.is_dir():
        print(f"Invalid project root: {root}", file=sys.stderr)
        return 2
    checks = validate(root, args.require_openspec, args.require_project_records)
    failures = [check for check in checks if check.status in {"FAIL", "BLOCKED"}]
    if args.json:
        print(json.dumps({"root": str(root), "checks": [asdict(check) for check in checks], "valid": not failures}, indent=2))
    else:
        for check in checks:
            print(f"{check.status:9} {check.name}: {check.detail}")
        print("SPEC_CONTRACT_VALID" if not failures else "SPEC_CONTRACT_INVALID")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
