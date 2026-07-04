import yaml
from pathlib import Path
from datetime import datetime

def load_database(db_path: Path) -> dict:
    if db_path.exists():
        with open(db_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {
        "projects": [{
            "project_id": "PRJ-EPB-001",
            "name": "Electric Parking Brake Control ECU",
            "target_aspice_level": "CL2",
            "safety_applicable": True,
            "cybersecurity_applicable": True,
            "current_gate_id": "GATE-G5"
        }],
        "artifacts": [],
        "issues": [],
        "trace_links": []
    }

def save_database(db_path: Path, data: dict):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with open(db_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

def _generate_id(prefix: str, existing_ids: list[str]) -> str:
    count = 1
    while True:
        candidate = f"{prefix}-{count:03d}"
        if candidate not in existing_ids:
            return candidate
        count += 1

def integrate_pipeline_results(root: Path, pipeline_result: dict, db_path: Path = None):
    if db_path is None:
        db_path = root / "data" / "project_database.yaml"
    
    db = load_database(db_path)
    
    existing_artifacts = [a.get("artifact_id") for a in db.get("artifacts", [])]
    existing_issues = [i.get("issue_id") for i in db.get("issues", [])]
    
    # 1. Update/Add Artifacts
    sdr = pipeline_result.get("sdr")
    if sdr:
        sdr_report = sdr.get("report")
        if sdr_report:
            art_id = _generate_id("ART-SDR", existing_artifacts)
            existing_artifacts.append(art_id)
            db.setdefault("artifacts", []).append({
                "artifact_id": art_id,
                "project_id": "PRJ-EPB-001",
                "artifact_type": "Unit Design Report",
                "title": Path(sdr_report).name,
                "version": "1.0",
                "status": "In Review",
                "storage_uri": str(Path(sdr_report).relative_to(root)),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
        unit_xmi = sdr.get("unit_xmi")
        if unit_xmi:
            # Check if UnitDesign.xmi already exists
            xmi_art = next((a for a in db.get("artifacts", []) if "UnitDesign.xmi" in str(a.get("storage_uri", ""))), None)
            if not xmi_art:
                art_id = _generate_id("ART-XMI", existing_artifacts)
                existing_artifacts.append(art_id)
                db.setdefault("artifacts", []).append({
                    "artifact_id": art_id,
                    "project_id": "PRJ-EPB-001",
                    "artifact_type": "Detailed Design Specification",
                    "title": "UnitDesign.xmi",
                    "version": "1.0",
                    "status": "In Review",
                    "storage_uri": str(Path(unit_xmi).relative_to(root)),
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            else:
                xmi_art["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                xmi_art["status"] = "In Review" # Code changed, needs review

    sar = pipeline_result.get("sar")
    if sar:
        sar_report = sar.get("report")
        if sar_report:
            art_id = _generate_id("ART-SAR", existing_artifacts)
            existing_artifacts.append(art_id)
            db.setdefault("artifacts", []).append({
                "artifact_id": art_id,
                "project_id": "PRJ-EPB-001",
                "artifact_type": "Architecture Review Report",
                "title": Path(sar_report).name,
                "version": "1.0",
                "status": "In Review",
                "storage_uri": str(Path(sar_report).relative_to(root)),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
        # 2. Add Issues from SAR Findings
        findings = sar.get("findings", [])
        for finding in findings:
            issue_id = _generate_id("ISS", existing_issues)
            existing_issues.append(issue_id)
            db.setdefault("issues", []).append({
                "issue_id": issue_id,
                "project_id": "PRJ-EPB-001",
                "title": "Architecture Consistency Violation",
                "description": finding,
                "severity": "High",
                "category": "Design",
                "status": "Open",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

    save_database(db_path, db)
    
    # Generate dashboard automatically
    try:
        import sys
        scripts_dir = root / "scripts"
        if str(scripts_dir) not in sys.path:
            sys.path.append(str(scripts_dir))
        from generate_dashboard import generate_dashboard
        generate_dashboard()
    except Exception as e:
        print(f"Warning: Failed to generate dashboard automatically: {e}")

    return db
