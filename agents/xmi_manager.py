from __future__ import annotations

from datetime import datetime
import hashlib
from pathlib import Path
from xml.dom import minidom
from xml.etree import ElementTree as ET


XMI_NS = "http://schema.omg.org/spec/XMI/2.1"
UML_NS = "http://schema.omg.org/spec/UML/2.1"
XMI = f"{{{XMI_NS}}}"
LEGACY_XMI_TYPE_ATTRS = (
    f"{{{XMI_NS}}}type",
    "{http://www.omg.org/XMI}type",
    "xmi:type",
)

ET.register_namespace("xmi", XMI_NS)
ET.register_namespace("uml", UML_NS)


def stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha1("::".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def _safe_id(value: str) -> str:
    cleaned = []
    for char in value.lower():
        if char.isalnum():
            cleaned.append(char)
        elif cleaned and cleaned[-1] != "_":
            cleaned.append("_")
    return "".join(cleaned).strip("_") or "element"


def _xmi_type(element: ET.Element) -> str:
    for attr in LEGACY_XMI_TYPE_ATTRS:
        if attr in element.attrib:
            return element.attrib[attr]
    return ""


SEMANTIC_IDS = {
    "VoltageFail_OutputSignalType": "enum_output_signal",
    "VoltageFail_ParamsType": "dt_params",
    "VoltageFail_InputType": "dt_input",
    "VoltageFail_StateType": "dt_state",
    "VoltageFail_OutputType": "dt_output",
    "VoltageFail": "class_voltage_fail",
    "VoltageFail Component": "cmp_voltage_fail",
    "Requirements": "pkg_requirements",
    "VoltageFail_Update Activity": "act_voltage_fail_update",
    "Voltage Fail Latch State Machine": "sm_fail_latch",
    "Output_INT_VoltageFail Decision Table": "class_output_decision_table",
}

ATTRIBUTE_IDS = {
    "Par_HighVoltageDetection": "attr_param_high_det",
    "Par_HighVoltageFailFiltering": "attr_param_high_filter",
    "Par_LowVoltageDetection": "attr_param_low_det",
    "Par_LowVoltageFailFiltering": "attr_param_low_filter",
    "Par_HighVoltageReturn": "attr_param_high_return",
    "Par_LowVoltageReturn": "attr_param_low_return",
    "Par_ExhibitionLowVoltageReturn": "attr_param_exhibition_low_return",
    "Input_H_VBAT": "attr_input_vbat",
    "Input_H_IGN1": "attr_input_ign1",
    "Input_C_FactoryMode": "attr_input_factory",
    "Output_INT_VoltageFail": "attr_output_voltage_fail",
    "highVbatFilterTimeMs": "attr_state_high_vbat_time",
    "highIgn1FilterTimeMs": "attr_state_high_ign1_time",
    "lowVbatFilterTimeMs": "attr_state_low_vbat_time",
    "lowIgn1FilterTimeMs": "attr_state_low_ign1_time",
}

ENUM_LITERAL_IDS = {
    "VOLTAGE_FAIL_OUTPUT_OFF": "enum_lit_off",
    "VOLTAGE_FAIL_OUTPUT_LOW_VOLTAGE": "enum_lit_low",
    "VOLTAGE_FAIL_OUTPUT_OVER_VOLTAGE": "enum_lit_over",
    "VOLTAGE_FAIL_OUTPUT_INVALID_CONFIG": "enum_lit_invalid",
}

OPERATION_IDS = {
    "VoltageFail_Init": "op_init",
    "VoltageFail_Update": "op_update",
    "VoltageFail_AddSaturated": "op_add_saturated",
    "VoltageFail_UpdateFilter": "op_update_filter",
    "VoltageFail_GetOutput": "op_get_output",
}

REQUIREMENTS = [
    ("req_vf_001", "VF-R-001 High VBAT Fail Detection", "comment_req_vf_001", "If Input_H_VBAT >= Par_HighVoltageDetection is maintained for Par_HighVoltageFailFiltering or longer, m_VoltageHighFail shall be stored as On."),
    ("req_vf_002", "VF-R-002 High IGN1 Fail Detection", "comment_req_vf_002", "If Input_H_IGN1 >= Par_HighVoltageDetection is maintained for Par_HighVoltageFailFiltering or longer, m_VoltageHighFail_IGN1 shall be stored as On."),
    ("req_vf_003", "VF-R-003 Low VBAT Fail Detection", "comment_req_vf_003", "If Input_H_VBAT <= Par_LowVoltageDetection is maintained for Par_LowVoltageFailFiltering or longer, m_VoltageLowFail shall be stored as On."),
    ("req_vf_004", "VF-R-004 Low IGN1 Fail Detection", "comment_req_vf_004", "If Input_H_IGN1 <= Par_LowVoltageDetection is maintained for Par_LowVoltageFailFiltering or longer, m_VoltageLowFail_IGN1 shall be stored as On."),
    ("req_vf_005", "VF-R-005 High VBAT Fail Return", "comment_req_vf_005", "If m_VoltageHighFail is On and Input_H_VBAT <= Par_HighVoltageReturn, m_VoltageHighFail shall be stored as Off."),
    ("req_vf_006", "VF-R-006 High IGN1 Fail Return", "comment_req_vf_006", "If m_VoltageHighFail_IGN1 is On and Input_H_IGN1 <= Par_HighVoltageReturn, m_VoltageHighFail_IGN1 shall be stored as Off."),
    ("req_vf_007", "VF-R-007 Low VBAT Fail Return", "comment_req_vf_007", "If m_VoltageLowFail is On, return threshold is Par_LowVoltageReturn in Custom Mode and Par_ExhibitionLowVoltageReturn otherwise. If Input_H_VBAT >= selected threshold, m_VoltageLowFail shall be stored as Off."),
    ("req_vf_008", "VF-R-008 Low IGN1 Fail Return", "comment_req_vf_008", "If m_VoltageLowFail_IGN1 is On, return threshold is Par_LowVoltageReturn in Custom Mode and Par_ExhibitionLowVoltageReturn otherwise. If Input_H_IGN1 >= selected threshold, m_VoltageLowFail_IGN1 shall be stored as Off."),
    ("req_vf_009", "VF-R-009 Integrated Voltage Fail Output", "comment_req_vf_009", "Output_INT_VoltageFail shall be Off, LowVoltage, OverVoltage, or InvalidConfig according to m_VoltageHighFail, m_VoltageHighFail_IGN1, m_VoltageLowFail, and m_VoltageLowFail_IGN1."),
]


def ensure_xmi(path: Path, package_name: str) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    root = _new_ea_root()
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
    for child in root.iter("packagedElement"):
        if child.attrib.get("name") == name and _xmi_type(child) == "uml:Package":
            return child
    return ET.SubElement(
        root,
        "packagedElement",
        {
            f"{XMI}type": "uml:Package",
            f"{XMI}id": SEMANTIC_IDS.get(name, f"pkg_{_safe_id(name)}"),
            "name": name,
        },
    )


def update_unit_design(path: Path, ast_files: list[dict], source_commit: str | None = None) -> dict:
    root = build_ea_unit_design(ast_files)
    summary = _ea_summary(root)
    write_xml(path, root)
    return summary


def build_ea_unit_design(ast_files: list[dict]) -> ET.Element:
    model, package = _new_ea_model_and_package()
    package.append(_comment("comment_pkg_voltage_fail", "Voltage Fail SW design generated from src/voltage_fail.c and inc/voltage_fail.h."))

    classes = _class_map(ast_files)
    functions = _function_map(ast_files)

    _append_enum(package, classes)
    _append_datatype(package, classes, "VoltageFail_ParamsType")
    _append_datatype(package, classes, "VoltageFail_InputType")
    _append_datatype(package, classes, "VoltageFail_StateType")
    _append_datatype(package, classes, "VoltageFail_OutputType")
    _append_component(package)
    _append_voltage_fail_class(package, functions)
    _append_requirements(package)
    _append_activity(package)
    _append_state_machine(package)
    _append_decision_table(package)

    root = ET.Element(f"{{{XMI_NS}}}XMI", {f"{XMI}version": "2.1"})
    root.append(model)
    return root


def _remove_generated_elements(package: ET.Element) -> None:
    removable_prefixes = ("cls_", "struct_", "enum_", "fn_", "dep_")
    for child in list(package):
        child_id = child.attrib.get(f"{XMI}id", "")
        if child_id.startswith(removable_prefixes):
            package.remove(child)


def _new_ea_root() -> ET.Element:
    model, _package = _new_ea_model_and_package()
    root = ET.Element(f"{{{XMI_NS}}}XMI", {f"{XMI}version": "2.1"})
    root.append(model)
    return root


def _new_ea_model_and_package() -> tuple[ET.Element, ET.Element]:
    model = ET.Element(
        f"{{{UML_NS}}}Model",
        {
            f"{XMI}id": "model_voltage_fail",
            "name": "VoltageFail_SW_Design",
        },
    )
    package = ET.SubElement(
        model,
        "packagedElement",
        {
            f"{XMI}type": "uml:Package",
            f"{XMI}id": "pkg_voltage_fail",
            "name": "VoltageFail",
        },
    )
    return model, package


def _class_map(ast_files: list[dict]) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for file_info in ast_files:
        for class_info in file_info.get("classes", []):
            result[class_info.get("name", "")] = class_info
    return result


def _function_map(ast_files: list[dict]) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for file_info in ast_files:
        for function_info in file_info.get("functions", []):
            result.setdefault(function_info.get("name", ""), function_info)
    return result


def _append_enum(package: ET.Element, classes: dict[str, dict]) -> None:
    enum_info = classes.get("VoltageFail_OutputSignalType", {})
    literals = enum_info.get("members", []) or list(ENUM_LITERAL_IDS)
    element = ET.SubElement(
        package,
        "packagedElement",
        {
            f"{XMI}type": "uml:Enumeration",
            f"{XMI}id": "enum_output_signal",
            "name": "VoltageFail_OutputSignalType",
        },
    )
    for literal in literals:
        ET.SubElement(
            element,
            "ownedLiteral",
            {
                f"{XMI}id": ENUM_LITERAL_IDS.get(literal, f"enum_lit_{_safe_id(literal)}"),
                "name": literal,
            },
        )


def _append_datatype(package: ET.Element, classes: dict[str, dict], name: str) -> None:
    element = ET.SubElement(
        package,
        "packagedElement",
        {
            f"{XMI}type": "uml:DataType",
            f"{XMI}id": SEMANTIC_IDS[name],
            "name": name,
        },
    )
    for member in classes.get(name, {}).get("members", []):
        member_name = _member_name(member)
        ET.SubElement(
            element,
            "ownedAttribute",
            {
                f"{XMI}id": _attribute_id(name, member_name),
                "name": member_name,
            },
        )


def _append_component(package: ET.Element) -> None:
    component = ET.SubElement(
        package,
        "packagedElement",
        {
            f"{XMI}type": "uml:Component",
            f"{XMI}id": "cmp_voltage_fail",
            "name": "VoltageFail Component",
        },
    )
    component.append(_comment("comment_cmp_voltage_fail", "Embedded C component that detects VBAT/IGN1 high voltage and low voltage failure states with filtering and hysteresis return thresholds."))


def _append_voltage_fail_class(package: ET.Element, functions: dict[str, dict]) -> None:
    voltage_class = ET.SubElement(
        package,
        "packagedElement",
        {
            f"{XMI}type": "uml:Class",
            f"{XMI}id": "class_voltage_fail",
            "name": "VoltageFail",
        },
    )
    operation_order = [
        "VoltageFail_Init",
        "VoltageFail_Update",
        "VoltageFail_AddSaturated",
        "VoltageFail_UpdateFilter",
        "VoltageFail_GetOutput",
    ]
    for name in operation_order:
        _append_operation(voltage_class, name, functions.get(name, {}))


def _append_operation(parent: ET.Element, name: str, function_info: dict) -> None:
    attrs = {
        f"{XMI}id": OPERATION_IDS[name],
        "name": name,
    }
    if name in {"VoltageFail_AddSaturated", "VoltageFail_UpdateFilter", "VoltageFail_GetOutput"}:
        attrs["visibility"] = "private"
    operation = ET.SubElement(parent, "ownedOperation", attrs)
    comments = {
        "VoltageFail_Init": ("comment_op_init", "Initializes fail latch states and filter timers to Off/0."),
        "VoltageFail_Update": ("comment_op_update", "Updates high/low voltage fail latches and Output_INT_VoltageFail from input, parameters, and elapsed time."),
        "VoltageFail_AddSaturated": ("comment_op_add_saturated", "Performs uint32 saturated addition for filter timer accumulation."),
        "VoltageFail_UpdateFilter": ("comment_op_update_filter", "Accumulates hold time while condition is true and latches fail flag when filter time is reached."),
        "VoltageFail_GetOutput": ("comment_op_get_output", "Maps high/low fail latch combination to Output_INT_VoltageFail."),
    }
    comment_id, body = comments[name]
    operation.append(_comment(comment_id, body))
    for param_name, direction in _operation_parameters(name, function_info):
        ET.SubElement(
            operation,
            "ownedParameter",
            {
                f"{XMI}id": _parameter_id(name, param_name),
                "name": param_name,
                "direction": direction,
            },
        )


def _operation_parameters(name: str, function_info: dict) -> list[tuple[str, str]]:
    if name == "VoltageFail_Init":
        return [("state", "inout")]
    if name == "VoltageFail_Update":
        return [
            ("state", "inout"),
            ("params", "in"),
            ("input", "in"),
            ("elapsedMs", "in"),
            ("output", "out"),
        ]
    return []


def _operation_short_name(name: str) -> str:
    return {
        "VoltageFail_Init": "init",
        "VoltageFail_Update": "update",
    }.get(name, _safe_id(name))


def _parameter_id(operation_name: str, param_name: str) -> str:
    explicit = {
        ("VoltageFail_Init", "state"): "param_init_state",
        ("VoltageFail_Update", "state"): "param_update_state",
        ("VoltageFail_Update", "params"): "param_update_params",
        ("VoltageFail_Update", "input"): "param_update_input",
        ("VoltageFail_Update", "elapsedMs"): "param_update_elapsed",
        ("VoltageFail_Update", "output"): "param_update_output",
    }
    return explicit.get((operation_name, param_name), f"param_{_operation_short_name(operation_name)}_{_safe_id(param_name)}")


def _append_requirements(package: ET.Element) -> None:
    requirements = ET.SubElement(
        package,
        "packagedElement",
        {
            f"{XMI}type": "uml:Package",
            f"{XMI}id": "pkg_requirements",
            "name": "Requirements",
        },
    )
    for req_id, name, comment_id, body in REQUIREMENTS:
        requirement = ET.SubElement(
            requirements,
            "packagedElement",
            {
                f"{XMI}type": "uml:Class",
                f"{XMI}id": req_id,
                "name": name,
            },
        )
        requirement.append(_comment(comment_id, body))


def _append_activity(package: ET.Element) -> None:
    activity = ET.SubElement(
        package,
        "packagedElement",
        {
            f"{XMI}type": "uml:Activity",
            f"{XMI}id": "act_voltage_fail_update",
            "name": "VoltageFail_Update Activity",
        },
    )
    activity.append(_comment("comment_act_voltage_fail_update", "Flow: validate pointers, update high/low filters, apply high return hysteresis, select low return threshold by Factory Mode, apply low return hysteresis, copy latch states to output, calculate Output_INT_VoltageFail."))


def _append_state_machine(package: ET.Element) -> None:
    state_machine = ET.SubElement(
        package,
        "packagedElement",
        {
            f"{XMI}type": "uml:StateMachine",
            f"{XMI}id": "sm_fail_latch",
            "name": "Voltage Fail Latch State Machine",
        },
    )
    state_machine.append(_comment("comment_sm_fail_latch", "Each individual fail latch has two logical states: Off and On. Detection filter transition sets Off to On. Return threshold transition resets On to Off."))
    region = ET.SubElement(state_machine, "region", {f"{XMI}id": "sm_fail_latch_region", "name": "FailLatchRegion"})
    ET.SubElement(region, "subvertex", {f"{XMI}type": "uml:State", f"{XMI}id": "state_fail_off", "name": "Off"})
    ET.SubElement(region, "subvertex", {f"{XMI}type": "uml:State", f"{XMI}id": "state_fail_on", "name": "On"})
    ET.SubElement(region, "transition", {f"{XMI}id": "trans_detect_fail", "name": "DetectionFilterReached", "source": "state_fail_off", "target": "state_fail_on"})
    ET.SubElement(region, "transition", {f"{XMI}id": "trans_return_fail", "name": "ReturnThresholdReached", "source": "state_fail_on", "target": "state_fail_off"})


def _append_decision_table(package: ET.Element) -> None:
    decision_table = ET.SubElement(
        package,
        "packagedElement",
        {
            f"{XMI}type": "uml:Class",
            f"{XMI}id": "class_output_decision_table",
            "name": "Output_INT_VoltageFail Decision Table",
        },
    )
    decision_table.append(_comment("comment_output_decision_table", "Priority 1: same channel High and Low both On => INVALID_CONFIG. Priority 2: any High Fail On => OVER_VOLTAGE. Priority 3: VBAT Low and IGN1 Low both On => LOW_VOLTAGE. Priority 4: otherwise => OFF."))


def _comment(comment_id: str, body: str) -> ET.Element:
    comment = ET.Element("ownedComment", {f"{XMI}id": comment_id})
    body_element = ET.SubElement(comment, "body")
    body_element.text = body
    return comment


def _attribute_id(owner: str, member_name: str) -> str:
    if owner in {"VoltageFail_StateType", "VoltageFail_OutputType"} and member_name in {
        "m_VoltageHighFail",
        "m_VoltageHighFail_IGN1",
        "m_VoltageLowFail",
        "m_VoltageLowFail_IGN1",
    }:
        owner_prefix = "state" if owner == "VoltageFail_StateType" else "output"
        suffix = {
            "m_VoltageHighFail": "high_vbat",
            "m_VoltageHighFail_IGN1": "high_ign1",
            "m_VoltageLowFail": "low_vbat",
            "m_VoltageLowFail_IGN1": "low_ign1",
        }[member_name]
        return f"attr_{owner_prefix}_{suffix}"
    return ATTRIBUTE_IDS.get(member_name, f"attr_{_safe_id(member_name)}")


def _ea_summary(root: ET.Element) -> dict:
    summary = {"datatypes": 0, "classes": 0, "enumerations": 0, "operations": 0, "requirements": 0}
    for element in root.iter():
        uml_type = _xmi_type(element)
        if uml_type == "uml:DataType":
            summary["datatypes"] += 1
        elif uml_type == "uml:Class":
            summary["classes"] += 1
            if (element.attrib.get("name") or "").startswith("VF-R-"):
                summary["requirements"] += 1
        elif uml_type == "uml:Enumeration":
            summary["enumerations"] += 1
        if element.tag.split("}", 1)[-1] == "ownedOperation":
            summary["operations"] += 1
    return summary


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
        uml_type = _xmi_type(element)
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
        elif element.tag.split("}", 1)[-1] == "ownedOperation":
            result["operations"].add(name)
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
