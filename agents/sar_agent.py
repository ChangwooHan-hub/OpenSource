from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agents.config import load_config, resolve_path
from agents.openai_client import OpenAIReviewClient
from agents.xmi_manager import ensure_architecture_seed, read_named_elements, write_review_report


DEVELOPER_PROMPT = """You are SAR_Agent.
Review architecture consistency between Architecture.xmi and UnitDesign.xmi.
Focus on missing architectural ownership, dependency direction risks, interface contract drift, and review actions.
Keep the response concise and actionable."""


def run_sar(root: Path, config_path: str = "agents/config.yaml") -> dict:
    config = load_config(root / config_path)
    paths = config["paths"]
    architecture_xmi = resolve_path(root, paths["architecture_xmi"])
    unit_xmi = resolve_path(root, paths["unit_design_xmi"])
    reports_dir = resolve_path(root, paths["reports_dir"])
    ensure_architecture_seed(architecture_xmi)

    architecture = read_named_elements(architecture_xmi, "Architecture")
    unit_design = read_named_elements(unit_xmi, "UnitDesign")
    findings = _deterministic_findings(config, architecture, unit_design)
    gpt_notes = _gpt_sar_notes(config, architecture, unit_design, findings)

    report_path = reports_dir / f"ReviewReport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    sections = [
        ("Architecture Inventory", _format_inventory(architecture)),
        ("Unit Design Inventory", _format_inventory(unit_design)),
        ("Rule Findings", "\n".join(f"- {finding}" for finding in findings) if findings else "No deterministic rule findings."),
        ("GPT SAR Notes", gpt_notes or "GPT review skipped. Set OPENAI_API_KEY and install openai to enable it."),
        ("EA Import", "Import `design/Architecture.xmi` and `design/UnitDesign.xmi` with Enterprise Architect: File > Import > Import Package from XMI."),
    ]
    write_review_report(report_path, "SAR_Agent Architecture Review", sections)
    return {"findings": findings, "report": str(report_path)}


def _deterministic_findings(config: dict, architecture: dict[str, set[str]], unit_design: dict[str, set[str]]) -> list[str]:
    findings: list[str] = []
    components = architecture.get("components", set())
    classes = unit_design.get("classes", set())
    enumerations = unit_design.get("enumerations", set())
    operations = unit_design.get("operations", set())
    unit_types = classes | enumerations
    allowed = set(config.get("architecture", {}).get("allowed_external_dependencies", []))

    if classes and not components:
        findings.append("Architecture.xmi has no uml:Component elements to own unit-level classes.")
    if operations and not classes:
        findings.append("UnitDesign.xmi contains free functions but no classes; confirm whether procedural units need component ownership.")

    for class_name in sorted(classes):
        if not _has_architecture_owner(class_name, components):
            findings.append(f"`{class_name}` is present in UnitDesign.xmi but has no matching or prefix-based architecture component.")

    for dependency in sorted(unit_design.get("dependencies", set())):
        normalized = dependency.lower()
        if any(token in normalized for token in allowed):
            continue
        if "_uses_" in dependency:
            supplier = dependency.rsplit("_uses_", 1)[-1]
            if supplier not in unit_types and not _has_architecture_owner(supplier, components):
                findings.append(f"Dependency `{dependency}` points to `{supplier}`, which is not represented in unit or architecture models.")
    return findings


def _has_architecture_owner(class_name: str, components: set[str]) -> bool:
    lowered = class_name.lower()
    for component in components:
        comp = component.lower()
        if comp in lowered or lowered.startswith(comp):
            return True
    return False


def _format_inventory(values: dict[str, set[str]]) -> str:
    serializable = {key: sorted(value) for key, value in values.items()}
    return f"```json\n{json.dumps(serializable, indent=2)}\n```"


def _gpt_sar_notes(config: dict, architecture: dict[str, set[str]], unit_design: dict[str, set[str]], findings: list[str]) -> str | None:
    openai_config = config.get("openai", {})
    client = OpenAIReviewClient(
        enabled=bool(openai_config.get("enabled", True)),
        max_output_tokens=int(openai_config.get("max_output_tokens", 4096)),
    )
    payload = {
        "architecture": {key: sorted(value) for key, value in architecture.items()},
        "unit_design": {key: sorted(value) for key, value in unit_design.items()},
        "deterministic_findings": findings,
    }
    return client.review(
        model=openai_config.get("sar_model", "gpt-5.2"),
        developer_prompt=DEVELOPER_PROMPT,
        user_prompt=json.dumps(payload, indent=2),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Review UnitDesign.xmi against Architecture.xmi.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--config", default="agents/config.yaml", help="Agent config path")
    args = parser.parse_args()
    result = run_sar(Path(args.root).resolve(), args.config)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
