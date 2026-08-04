#!/usr/bin/env python3
"""Initialize private, Git-local Easy2Dev state without external dependencies."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


EXCLUDE_MARKER = "# Easy2Dev private workflow state"
EXCLUDE_PATTERN = "/.easy2dev/"


def run_git(args: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        check=check,
        text=True,
        capture_output=True,
    )


def find_git_root(project_root: Path) -> Path | None:
    if shutil.which("git") is None:
        return None
    result = run_git(["rev-parse", "--show-toplevel"], project_root, check=False)
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip()).resolve()


def ensure_git_root(project_root: Path, init_git: bool) -> Path:
    git_root = find_git_root(project_root)
    if git_root is not None and (not init_git or git_root == project_root):
        return git_root
    if not init_git:
        raise RuntimeError("No Git repository found. Re-run with --init-git for a new project.")
    if shutil.which("git") is None:
        raise RuntimeError("Git is required to keep Easy2Dev state locally excluded.")
    # A new project directory may sit inside another repository. An explicit
    # --init-git means this directory owns its own project state, so initialize
    # a nested repository instead of writing to the parent's local exclude.
    run_git(["init", "--quiet"], project_root)
    git_root = find_git_root(project_root)
    if git_root is None:
        raise RuntimeError("Git initialization completed but the repository root was not found.")
    return git_root


def git_exclude_path(git_root: Path) -> Path:
    result = run_git(["rev-parse", "--git-path", "info/exclude"], git_root)
    raw = Path(result.stdout.strip())
    return raw.resolve() if raw.is_absolute() else (git_root / raw).resolve()


def ensure_local_exclude(git_root: Path) -> Path:
    exclude_path = git_exclude_path(git_root)
    exclude_path.parent.mkdir(parents=True, exist_ok=True)
    existing = exclude_path.read_text(encoding="utf-8") if exclude_path.exists() else ""
    lines = existing.splitlines()
    if EXCLUDE_PATTERN not in lines:
        prefix = "" if not existing or existing.endswith("\n") else "\n"
        addition = f"{prefix}{EXCLUDE_MARKER}\n{EXCLUDE_PATTERN}\n"
        exclude_path.write_text(existing + addition, encoding="utf-8", newline="\n")
    return exclude_path


def initial_state(mode: str) -> str:
    return f"""schema_version: 2
mode: {mode}
stage: DISCOVERY
status: ACTIVE
active_feature: null
active_change: null
approvals:
  product_docs:
    status: pending
    scope: null
    recorded_at: null
  manual_acceptance:
    status: pending
    scope: null
    recorded_at: null
  cicd:
    status: pending
    scope: null
    recorded_at: null
evidence_summary:
  local_onboarding: NOT_RUN
  spec_contract: NOT_RUN
  static: NOT_RUN
  unit: NOT_RUN
  integration: NOT_RUN
  build: NOT_RUN
  runtime: NOT_RUN
  migration: N_A
next_action: inspect repository and establish current truth
updated_at: null
"""


def ensure_private_state(git_root: Path, mode: str) -> tuple[Path, list[str]]:
    state_root = git_root / ".easy2dev"
    created: list[str] = []
    state_root.mkdir(exist_ok=True)
    for name in ("decisions", "features", "evidence"):
        directory = state_root / name
        if not directory.exists():
            directory.mkdir()
            created.append(str(directory.relative_to(git_root)))

    state_file = state_root / "state.yaml"
    if not state_file.exists():
        state_file.write_text(initial_state(mode), encoding="utf-8", newline="\n")
        created.append(str(state_file.relative_to(git_root)))

    journal_file = state_root / "journal.md"
    if not journal_file.exists():
        journal_file.write_text(
            "# Easy2Dev journal\n\n"
            "Newest factual transition goes first. Do not store secrets, prompts, or hidden reasoning.\n",
            encoding="utf-8",
            newline="\n",
        )
        created.append(str(journal_file.relative_to(git_root)))

    return state_root, created


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize project-local Easy2Dev workflow state and Git-local exclusion."
    )
    parser.add_argument("--project-root", default=".", help="Workspace or repository directory.")
    parser.add_argument(
        "--mode",
        choices=("new", "existing", "foreign"),
        default="existing",
        help="Initial discovery mode recorded only when state.yaml is first created.",
    )
    parser.add_argument(
        "--init-git",
        action="store_true",
        help="Initialize Git when the project is not already inside a repository.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    if not project_root.exists() or not project_root.is_dir():
        print(json.dumps({"ok": False, "error": "project root must be an existing directory"}))
        return 2

    try:
        git_root = ensure_git_root(project_root, args.init_git)
        exclude_path = ensure_local_exclude(git_root)
        state_root, created = ensure_private_state(git_root, args.mode)
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1

    result = {
        "ok": True,
        "git_root": str(git_root),
        "state_root": str(state_root),
        "exclude_file": str(exclude_path),
        "exclude_pattern": EXCLUDE_PATTERN,
        "created": created,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
