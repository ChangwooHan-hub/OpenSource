from __future__ import annotations

from pathlib import Path
from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
    "paths": {
        "architecture_xmi": "design/Architecture.xmi",
        "unit_design_xmi": "design/UnitDesign.xmi",
        "reports_dir": "design/reports",
    },
    "openai": {
        "enabled": True,
        "sdr_model": "gpt-5.2",
        "sar_model": "gpt-5.2",
        "max_output_tokens": 4096,
    },
    "parser": {
        "compile_args": ["-x", "c++", "-std=c++17"],
        "source_extensions": [".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"],
    },
    "architecture": {
        "allowed_external_dependencies": ["std", "stdint", "stddef", "stdbool"],
    },
}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(path: str | Path = "agents/config.yaml") -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.exists():
        return DEFAULT_CONFIG

    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required to read agents/config.yaml. Install requirements.txt.") from exc

    loaded = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return deep_merge(DEFAULT_CONFIG, loaded)


def resolve_path(root: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    return root / candidate
