from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agents.ast_parser import is_source_file
from agents.config import load_config
from agents.sar_agent import run_sar
from agents.sdr_agent import run_sdr
from agents.process_integrator import integrate_pipeline_results

def changed_files(root: Path, mode: str, explicit_files: list[str]) -> list[str]:
    if explicit_files:
        return [str(_resolve_explicit_path(root, file)) for file in explicit_files]

    if mode == "last-commit":
        command = ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]
    elif mode == "staged":
        command = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRT"]
    else:
        command = ["git", "diff", "--name-only", "--diff-filter=ACMRT"]

    try:
        output = subprocess.check_output(command, cwd=root, text=True, stderr=subprocess.DEVNULL)
    except subprocess.SubprocessError:
        return []

    git_root = _git_root(root)
    files = []
    for line in output.splitlines():
        candidate = _resolve_changed_path(root, git_root, line.strip())
        if candidate.exists() and is_source_file(candidate):
            files.append(str(candidate))
    return files


def _git_root(root: Path) -> Path:
    try:
        output = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=root, text=True, stderr=subprocess.DEVNULL)
        return Path(output.strip()).resolve()
    except subprocess.SubprocessError:
        return root


def _resolve_changed_path(root: Path, git_root: Path, value: str) -> Path:
    candidate = root / value
    if candidate.exists():
        return candidate
    candidate = git_root / value
    if candidate.exists():
        return candidate
    return root / value


def _resolve_explicit_path(root: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    root_candidate = root / candidate
    if root_candidate.exists():
        return root_candidate.resolve()
    cwd_candidate = Path.cwd() / candidate
    if cwd_candidate.exists():
        return cwd_candidate.resolve()
    return root_candidate.resolve()


def run_pipeline(root: Path, mode: str, files: list[str], config_path: str = "agents/config.yaml") -> dict:
    config = load_config(root / config_path)
    extensions = set(config.get("parser", {}).get("source_extensions", []))
    selected = [
        file for file in changed_files(root, mode, files)
        if not extensions or Path(file).suffix.lower() in extensions
    ]

    if not selected:
        sar_result = run_sar(root, config_path)
        result = {"changed_files": [], "sdr": None, "sar": sar_result}
        integrate_pipeline_results(root, result)
        return result

    sdr_result = run_sdr(selected, root, config_path)
    sar_result = run_sar(root, config_path)
    result = {"changed_files": selected, "sdr": sdr_result, "sar": sar_result}
    integrate_pipeline_results(root, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run AST -> SDR -> SAR design synchronization.")
    parser.add_argument("files", nargs="*", help="Explicit changed files")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--config", default="agents/config.yaml", help="Agent config path")
    parser.add_argument(
        "--mode",
        choices=["working-tree", "staged", "last-commit"],
        default="working-tree",
        help="How to discover changed files when no files are provided",
    )
    parser.add_argument("--changed-in-last-commit", action="store_true", help="Shortcut for --mode last-commit")
    args = parser.parse_args()

    mode = "last-commit" if args.changed_in_last_commit else args.mode
    result = run_pipeline(Path(args.root).resolve(), mode, args.files, args.config)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
