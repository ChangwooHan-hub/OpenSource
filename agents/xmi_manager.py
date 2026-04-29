from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path
from xml.dom import minidom
from xml.etree import ElementTree as ET


XMI_NS = "http://www.omg.org/XMI"
UML_NS = "http://www.eclipse.org/uml2/5.0.0/UML"
XMI = f"{{{XMI_NS}}}"

ET.register_namespace("xmi", XMI_NS)
ET.register_namespace("uml", UML_NS)


def stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha1("::".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def ensure_xmi(path: Path, package_name: str) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    root = ET.Element(
        f"{{{UML_NS}}}Model",
        {
            f"{XMI}version": "2.1",
            "name": "SystemModel",
        },
    )
    ET.SubElement(
        root,
        "packagedElement",
        {
            f"{XMI}type": "uml:Package",
            f"{XMI}id": stable_id("pkg", package_name),
            "name": package_name,
        },
    )
    write_xml(path, root)


def read_root(path: Path, package_name: str) -> ET.Element:
    ensure_xmi(path, package_name)
    return ET.parse(path).getroot()


def write_xml(path: Path, root: ET.Element) -> None:
    rough = ET.tostring(root, encoding="utf-8")
    parsed = minidom.parseString(rough)
    pretty = parsed.toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")
    cleaned = "\n".join(line for line in pretty.splitlines() if line.strip())
    path.write_text(cleaned + "\n", encoding="utf-8")


def find_or_create_package(root: ET.Element, name: str) -> ET.Element:
    for child in root.findall("packagedElement"):
        if child.attrib.get("name") == name and child.attrib.get(f"{XMI}type") == "uml:Package":
            return child
    return ET.SubElement(
        root,
        "packagedElement",
        {
            f"{XMI}type": "uml:Package",
            f"{XMI}id": stable_id("pkg", name),
            "name": name,
        },
    )


def update_unit_design(path: Path, ast_files: list[dict], source_commit: str | None = None) -> dict:
    root = read_root(path, "UnitDesign")
    package = find_or_create_package(root, "UnitDesign")

    _remove_generated_elements(package)

    summary = {"classes": 0, "functions": 0, "dependencies": 0}
    package.append(ET.Comment(f"Updated by SDR_Agent {datetime.now().isoformat(timespec='seconds')}"))
    if source_commit:
        package.append(ET.Comment(f"Source commit {source_commit}"))

    known_names: dict[str, str] = {}
    emitted_functions: set[tuple[str, tuple[str, ...]]] = set()
    for file_info in ast_files:
        for class_info in file_info.get("classes", []):
            known_names[class_info.get("name", "")] = _type_element_id(file_info, class_info)
            package.append(_class_element(file_info, class_info))
            summary["classes"] += 1
        for function_info in file_info.get("functions", []):
            signature = (function_info.get("name", ""), tuple(function_info.get("parameters", [])))
            if signature in emitted_functions:
                continue
            emitted_functions.add(signature)
            package.append(_function_element(file_info, function_info))
            summary["functions"] += 1

    for file_info in ast_files:
        for class_info in file_info.get("classes", []):
            for dependency in class_info.get("dependencies", []):
                if dependency and dependency != class_info.get("name"):
                    package.append(_dependency_element(class_info.get("name", ""), dependency, known_names))
                    summary["dependencies"] += 1

    write_xml(path, root)
    return summary


def _remove_generated_elements(package: ET.Element) -> None:
    removable_prefixes = ("cls_", "struct_", "enum_", "fn_", "dep_")
    for child in list(package):
        child_id = child.attrib.get(f"{XMI}id", "")
        if child_id.startswith(removable_prefixes):
            package.remove(child)


def _class_element(file_info: dict, class_info: dict) -> ET.Element:
    kind = class_info.get("kind", "class")
    if kind == "enum":
        return _enum_element(file_info, class_info)
    prefix = "struct" if kind == "struct" else "cls"
    name = class_info.get("name", "Unnamed")
    element = ET.Element(
        "packagedElement",
        {
            f"{XMI}type": "uml:Class",
            f"{XMI}id": _type_element_id(file_info, class_info),
            "name": name,
        },
    )
    element.append(ET.Comment(f"source: {file_info.get('file', '')}"))
    for member in class_info.get("members", []):
        member_name = _member_name(member)
        ET.SubElement(
            element,
            "ownedAttribute",
            {
                f"{XMI}id": stable_id("attr", file_info.get("file", ""), name, member),
                "name": member_name,
                "type": _member_type(member),
            },
        )
    for method in class_info.get("methods", []):
        operation = ET.SubElement(
            element,
            "ownedOperation",
            {
                f"{XMI}id": stable_id("op", file_info.get("file", ""), name, method.get("name", "")),
                "name": method.get("name", ""),
                "visibility": method.get("access", "public"),
            },
        )
        if method.get("result_type"):
            ET.SubElement(
                operation,
                "ownedParameter",
                {
                    f"{XMI}id": stable_id("ret", file_info.get("file", ""), name, method.get("name", "")),
                    "name": "return",
                    "direction": "return",
                    "type": method.get("result_type", ""),
                },
            )
        for index, parameter in enumerate(method.get("parameters", []), start=1):
            ET.SubElement(
                operation,
                "ownedParameter",
                {
                    f"{XMI}id": stable_id("param", file_info.get("file", ""), name, method.get("name", ""), str(index)),
                    "name": _parameter_name(parameter, index),
                    "direction": "in",
                    "type": _parameter_type(parameter),
                },
            )
    return element


def _enum_element(file_info: dict, class_info: dict) -> ET.Element:
    name = class_info.get("name", "UnnamedEnum")
    element = ET.Element(
        "packagedElement",
        {
            f"{XMI}type": "uml:Enumeration",
            f"{XMI}id": _type_element_id(file_info, class_info),
            "name": name,
        },
    )
    element.append(ET.Comment(f"source: {file_info.get('file', '')}"))
    for literal in class_info.get("members", []):
        ET.SubElement(
            element,
            "ownedLiteral",
            {
                f"{XMI}id": stable_id("lit", file_info.get("file", ""), name, literal),
                "name": literal,
            },
        )
    return element


def _function_element(file_info: dict, function_info: dict) -> ET.Element:
    name = function_info.get("name", "unnamed_function")
    element = ET.Element(
        "packagedElement",
        {
            f"{XMI}type": "uml:Operation",
            f"{XMI}id": stable_id("fn", file_info.get("file", ""), name),
            "name": name,
        },
    )
    element.append(ET.Comment(f"source: {file_info.get('file', '')}"))
    if function_info.get("result_type"):
        ET.SubElement(
            element,
            "ownedParameter",
            {
                f"{XMI}id": stable_id("fnret", file_info.get("file", ""), name),
                "name": "return",
                "direction": "return",
                "type": function_info.get("result_type", ""),
            },
        )
    for index, parameter in enumerate(function_info.get("parameters", []), start=1):
        ET.SubElement(
            element,
            "ownedParameter",
            {
                f"{XMI}id": stable_id("fnparam", file_info.get("file", ""), name, str(index)),
                "name": _parameter_name(parameter, index),
                "direction": "in",
                "type": _parameter_type(parameter),
            },
        )
    return element


def _type_element_id(file_info: dict, class_info: dict) -> str:
    kind = class_info.get("kind", "class")
    if kind == "enum":
        prefix = "enum"
    elif kind == "struct":
        prefix = "struct"
    else:
        prefix = "cls"
    return stable_id(prefix, file_info.get("file", ""), class_info.get("name", ""))


def _dependency_element(source: str, target: str, known_names: dict[str, str]) -> ET.Element:
    attributes = {
        f"{XMI}type": "uml:Dependency",
        f"{XMI}id": stable_id("dep", source, target),
        "name": f"{source}_uses_{target}",
        "client": known_names.get(source, source),
        "supplier": known_names.get(target, target),
    }
    return ET.Element("packagedElement", attributes)


def read_named_elements(path: Path, package_name: str) -> dict[str, set[str]]:
    root = read_root(path, package_name)
    result = {"packages": set(), "components": set(), "classes": set(), "enumerations": set(), "operations": set(), "dependencies": set()}
    for element in root.iter():
        uml_type = element.attrib.get(f"{XMI}type", "")
        name = element.attrib.get("name")
        if not name:
            continue
        if uml_type == "uml:Package":
            result["packages"].add(name)
        elif uml_type == "uml:Component":
            result["components"].add(name)
        elif uml_type == "uml:Class":
            result["classes"].add(name)
        elif uml_type == "uml:Enumeration":
            result["enumerations"].add(name)
        elif uml_type == "uml:Operation":
            result["operations"].add(name)
        elif uml_type == "uml:Dependency":
            result["dependencies"].add(name)
    return result


def ensure_architecture_seed(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    root = ET.Element(
        f"{{{UML_NS}}}Model",
        {
            f"{XMI}version": "2.1",
            "name": "SystemModel",
        },
    )
    arch = ET.SubElement(
        root,
        "packagedElement",
        {
            f"{XMI}type": "uml:Package",
            f"{XMI}id": stable_id("pkg", "Architecture"),
            "name": "Architecture",
        },
    )
    ET.SubElement(
        arch,
        "packagedElement",
        {
            f"{XMI}type": "uml:Component",
            f"{XMI}id": stable_id("comp", "Application"),
            "name": "Application",
        },
    )
    ET.SubElement(
        arch,
        "packagedElement",
        {
            f"{XMI}type": "uml:Component",
            f"{XMI}id": stable_id("comp", "Platform"),
            "name": "Platform",
        },
    )
    write_xml(path, root)


def write_review_report(path: Path, title: str, sections: list[tuple[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}", "", f"Generated: {datetime.now().isoformat(timespec='seconds')}", ""]
    for heading, body in sections:
        lines.extend([f"## {heading}", "", body.strip() or "No findings.", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def _member_name(member: str) -> str:
    tokens = member.replace("*", " ").replace("&", " ").split()
    return tokens[-1].strip(";") if tokens else member


def _member_type(member: str) -> str:
    tokens = member.split()
    return " ".join(tokens[:-1]) if len(tokens) > 1 else ""


def _parameter_name(parameter: str, index: int) -> str:
    tokens = parameter.replace("*", " ").replace("&", " ").split()
    if len(tokens) < 2:
        return f"arg{index}"
    return tokens[-1]


def _parameter_type(parameter: str) -> str:
    tokens = parameter.split()
    if len(tokens) < 2:
        return parameter
    return " ".join(tokens[:-1])
