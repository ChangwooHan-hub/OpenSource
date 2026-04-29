from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agents.ast_parser import parse_files
from agents.config import load_config, resolve_path
from agents.openai_client import OpenAIReviewClient
from agents.xmi_manager import ensure_architecture_seed, update_unit_design, write_review_report


DEVELOPER_PROMPT = """You are SDR_Agent.
Review C/C++ AST JSON and summarize unit design changes for UML class/function documentation.
Do not emit XMI. Report only concise design implications, renamed/added/removed elements, and risks."""


def run_sdr(files: list[str], root: Path, config_path: str = "agents/config.yaml") -> dict:
    config = load_config(root / config_path)
    paths = config["paths"]
    unit_xmi = resolve_path(root, paths["unit_design_xmi"])
    architecture_xmi = resolve_path(root, paths["architecture_xmi"])
    reports_dir = resolve_path(root, paths["reports_dir"])
    ensure_architecture_seed(architecture_xmi)

    ast_files = parse_files(files, config["parser"].get("compile_args", []))
    commit = _git_commit(root)
    summary = update_unit_design(unit_xmi, ast_files, source_commit=commit)

    gpt_notes = _gpt_sdr_notes(config, ast_files)
    report_path = reports_dir / f"SDRReport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    sections = [
        ("Inputs", "\n".join(f"- `{file}`" for file in files) or "No C/C++ files."),
        ("AST Summary", f"```json\n{json.dumps(summary, indent=2)}\n```"),
        ("GPT SDR Notes", gpt_notes or "GPT review skipped. Set OPENAI_API_KEY and install openai to enable it."),
        ("Output", f"Updated `{unit_xmi}`."),
    ]
    write_review_report(report_path, "SDR_Agent Unit Design Update", sections)
    return {"ast_files": ast_files, "summary": summary, "unit_xmi": str(unit_xmi), "report": str(report_path)}


def _gpt_sdr_notes(config: dict, ast_files: list[dict]) -> str | None:
    openai_config = config.get("openai", {})
    client = OpenAIReviewClient(
        enabled=bool(openai_config.get("enabled", True)),
        max_output_tokens=int(openai_config.get("max_output_tokens", 4096)),
    )
    if not ast_files:
        return None
    return client.review(
        model=openai_config.get("sdr_model", "gpt-5.2"),
        developer_prompt=DEVELOPER_PROMPT,
        user_prompt=json.dumps(ast_files, indent=2),
    )


def _git_commit(root: Path) -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
    except subprocess.SubprocessError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Update UnitDesign.xmi from changed C/C++ files.")
    parser.add_argument("files", nargs="*", help="Changed C/C++ files")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--config", default="agents/config.yaml", help="Agent config path")
    args = parser.parse_args()
    result = run_sdr(args.files, Path(args.root).resolve(), args.config)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
