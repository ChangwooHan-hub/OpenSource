import yaml
import xml.etree.ElementTree as ET
from pathlib import Path

def generate_dashboard():
    base_dir = Path(__file__).resolve().parent.parent
    db_path = base_dir / "data" / "project_database.yaml"
    xmi_path = base_dir / "design" / "UnitDesign.xmi"
    output_path = base_dir / "dashboard.html"

    # 1. Load Data
    artifacts = []
    issues = []
    if db_path.exists():
        with open(db_path, "r", encoding="utf-8") as f:
            db = yaml.safe_load(f) or {}
            artifacts = db.get("artifacts", [])
            issues = db.get("issues", [])

    # 2. Parse XMI
    reqs = []
    classes = []
    if xmi_path.exists():
        tree = ET.parse(xmi_path)
        root = tree.getroot()
        namespaces = {'uml': 'http://schema.omg.org/spec/UML/2.1', 'xmi': 'http://schema.omg.org/spec/XMI/2.1'}
        
        for req in root.findall(".//packagedElement[@xmi:type='uml:Package'][@name='Requirements']/packagedElement", namespaces):
            req_name = req.attrib.get("name", "Unknown")
            reqs.append(req_name)
            
        for cls in root.findall(".//packagedElement[@xmi:type='uml:Class']", namespaces):
            cls_name = cls.attrib.get("name", "")
            if "VF-R-" not in cls_name and "Decision Table" not in cls_name:
                classes.append(cls_name)

    # 3. Build Mermaid Graph
    mermaid_lines = ["graph LR"]
    
    mermaid_lines.append("  subgraph Requirements")
    for i, req in enumerate(reqs):
        safe_req = req.replace('"', '')
        mermaid_lines.append(f"    R{i}[\"{safe_req}\"]")
    mermaid_lines.append("  end")

    mermaid_lines.append("  subgraph UnitDesign")
    for i, cls in enumerate(classes):
        mermaid_lines.append(f"    C{i}[\"Class: {cls}\"]")
        for j in range(len(reqs)):
            mermaid_lines.append(f"    R{j} --> C{i}")
    mermaid_lines.append("  end")

    mermaid_lines.append("  subgraph Artifacts")
    for i, art in enumerate(artifacts):
        title = art.get('title', 'Unknown')
        mermaid_lines.append(f"    A{i}[\"Artifact: {title}\"]")
        for j in range(len(classes)):
            mermaid_lines.append(f"    C{j} -.->|Documented by| A{i}")
    mermaid_lines.append("  end")

    if issues:
        mermaid_lines.append("  subgraph Issues")
        for i, iss in enumerate(issues):
            iss_id = iss.get('issue_id', 'ISS')
            sev = iss.get('severity', '')
            mermaid_lines.append(f"    I{i}((\"{iss_id}\\nSeverity: {sev}\"))")
            mermaid_lines.append(f"    style I{i} fill:#f9d0c4,stroke:#d9534f,stroke-width:2px")
            for j in range(len(artifacts)):
                if "SAR" in artifacts[j].get("artifact_id", ""):
                    mermaid_lines.append(f"    A{j} -.->|Found| I{i}")
        mermaid_lines.append("  end")

    mermaid_graph = "\\n".join(mermaid_lines)

    # 4. Generate HTML
    html = [
        "<!DOCTYPE html>",
        "<html lang='ko'>",
        "<head>",
        "    <meta charset='UTF-8'>",
        "    <title>프로세스 추적성 대시보드</title>",
        "    <script src='https://cdn.jsdelivr.net/npm/mermaid@10.8.0/dist/mermaid.min.js'></script>",
        "    <style>",
        "        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background-color: #f4f7f6; }",
        "        h1 { color: #333; text-align: center; }",
        "        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; overflow-x: auto; }",
        "        .mermaid { text-align: center; }",
        "        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }",
        "        th, td { padding: 12px; border: 1px solid #eee; text-align: left; }",
        "        th { background-color: #fafafa; color: #555; }",
        "        .badge { padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; }",
        "        .badge-high { background-color: #fbebeb; color: #d9534f; }",
        "        .badge-review { background-color: #e8f4f8; color: #0275d8; }",
        "    </style>",
        "</head>",
        "<body>",
        "    <h1>📊 프로젝트 단위설계 & 산출물 추적성 대시보드</h1>",
        "    <div class='card'>",
        "        <h2>🔗 요구사항-설계-산출물 추적 맵 (Traceability Map)</h2>",
        "        <div class='mermaid'>" + mermaid_graph + "</div>",
        "    </div>",
        "    <div class='card'>",
        "        <h2>📄 자동 생성 산출물 (Artifacts)</h2>",
        "        <table>",
        "            <tr><th>Artifact ID</th><th>유형</th><th>제목</th><th>상태</th><th>생성일시</th></tr>"
    ]
    
    for art in artifacts:
        status_html = f"<span class='badge badge-review'>{art.get('status')}</span>"
        html.append(f"            <tr><td>{art.get('artifact_id')}</td><td>{art.get('artifact_type')}</td><td>{art.get('title')}</td><td>{status_html}</td><td>{art.get('created_at')}</td></tr>")

    html.append("        </table>")
    html.append("    </div>")
    html.append("    <div class='card'>")
    html.append("        <h2>⚠️ 아키텍처/검증 이슈 (Issues)</h2>")
    html.append("        <table>")
    html.append("            <tr><th>Issue ID</th><th>심각도</th><th>카테고리</th><th>설명</th><th>상태</th></tr>")

    for iss in issues:
        sev = iss.get('severity', '')
        sev_html = f"<span class='badge badge-high'>{sev}</span>" if sev == "High" else sev
        html.append(f"            <tr><td>{iss.get('issue_id')}</td><td>{sev_html}</td><td>{iss.get('category')}</td><td>{iss.get('description')}</td><td>{iss.get('status')}</td></tr>")

    html.append("        </table>")
    html.append("    </div>")
    html.append("    <script>")
    html.append("        mermaid.initialize({startOnLoad:true, theme: 'default'});")
    html.append("    </script>")
    html.append("</body>")
    html.append("</html>")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html))
    
    print(f"Success: Dashboard successfully generated at: {output_path}")

if __name__ == "__main__":
    generate_dashboard()
