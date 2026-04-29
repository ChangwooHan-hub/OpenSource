from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable


SOURCE_EXTENSIONS = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"}


@dataclass
class MethodInfo:
    name: str
    result_type: str = ""
    parameters: list[str] = field(default_factory=list)
    access: str = "public"


@dataclass
class ClassInfo:
    name: str
    kind: str = "class"
    methods: list[MethodInfo] = field(default_factory=list)
    members: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)


@dataclass
class FunctionInfo:
    name: str
    result_type: str = ""
    parameters: list[str] = field(default_factory=list)


@dataclass
class AstFileInfo:
    file: str
    parser: str
    includes: list[str] = field(default_factory=list)
    classes: list[ClassInfo] = field(default_factory=list)
    functions: list[FunctionInfo] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    diagnostics: list[str] = field(default_factory=list)


def is_source_file(path: str | Path, extensions: Iterable[str] = SOURCE_EXTENSIONS) -> bool:
    return Path(path).suffix.lower() in set(extensions)


def parse_files(files: Iterable[str | Path], compile_args: list[str] | None = None) -> list[dict]:
    results = []
    for file_path in files:
        path = Path(file_path)
        if path.exists() and is_source_file(path):
            results.append(asdict(parse_file(path, compile_args=compile_args or [])))
    return results


def parse_file(path: Path, compile_args: list[str] | None = None) -> AstFileInfo:
    try:
        return _parse_with_libclang(path, compile_args or [])
    except Exception as exc:
        fallback = _parse_with_regex(path)
        fallback.diagnostics.append(f"libclang unavailable or failed: {exc}")
        return fallback


def _parse_with_libclang(path: Path, compile_args: list[str]) -> AstFileInfo:
    from clang import cindex

    lib_file = os.getenv("CLANG_LIBRARY_FILE")
    if lib_file:
        cindex.Config.set_library_file(lib_file)

    index = cindex.Index.create()
    args = compile_args or ["-x", "c++", "-std=c++17"]
    translation_unit = index.parse(str(path), args=args)
    info = AstFileInfo(file=str(path), parser="libclang")
    info.diagnostics = [str(diag) for diag in translation_unit.diagnostics]
    info.includes = _read_includes(path)

    for cursor in translation_unit.cursor.get_children():
        if not _is_from_file(cursor, path):
            continue
        kind_name = str(cursor.kind)
        if kind_name.endswith("CLASS_DECL") or kind_name.endswith("STRUCT_DECL"):
            class_info = _class_from_cursor(cursor)
            if class_info.name:
                info.classes.append(class_info)
        elif kind_name.endswith("FUNCTION_DECL"):
            fn = _function_from_cursor(cursor)
            if fn.name:
                info.functions.append(fn)

    deps = set(_include_dependency_names(info.includes))
    for class_info in info.classes:
        deps.update(class_info.dependencies)
    info.dependencies = sorted(deps)
    return info


def _is_from_file(cursor: object, path: Path) -> bool:
    location = getattr(cursor, "location", None)
    file_obj = getattr(location, "file", None)
    if not file_obj:
        return False
    try:
        return Path(str(file_obj)).resolve() == path.resolve()
    except OSError:
        return False


def _class_from_cursor(cursor: object) -> ClassInfo:
    from clang import cindex

    class_info = ClassInfo(
        name=getattr(cursor, "spelling", ""),
        kind="struct" if str(cursor.kind).endswith("STRUCT_DECL") else "class",
    )
    dependencies: set[str] = set()
    for child in cursor.get_children():
        if child.kind == cindex.CursorKind.CXX_METHOD:
            class_info.methods.append(_method_from_cursor(child))
        elif child.kind == cindex.CursorKind.FIELD_DECL:
            member_type = getattr(child.type, "spelling", "")
            class_info.members.append(f"{member_type} {child.spelling}".strip())
            dependencies.update(_type_dependencies(member_type))
        elif child.kind == cindex.CursorKind.CXX_BASE_SPECIFIER:
            base_type = getattr(child.type, "spelling", "")
            dependencies.update(_type_dependencies(base_type))
    class_info.dependencies = sorted(dependencies - {class_info.name})
    return class_info


def _method_from_cursor(cursor: object) -> MethodInfo:
    result_type = getattr(getattr(cursor, "result_type", None), "spelling", "")
    params = [f"{arg.type.spelling} {arg.spelling}".strip() for arg in cursor.get_arguments()]
    access = str(getattr(cursor, "access_specifier", "public")).split(".")[-1].lower()
    return MethodInfo(name=getattr(cursor, "spelling", ""), result_type=result_type, parameters=params, access=access)


def _function_from_cursor(cursor: object) -> FunctionInfo:
    result_type = getattr(getattr(cursor, "result_type", None), "spelling", "")
    params = [f"{arg.type.spelling} {arg.spelling}".strip() for arg in cursor.get_arguments()]
    return FunctionInfo(name=getattr(cursor, "spelling", ""), result_type=result_type, parameters=params)


def _parse_with_regex(path: Path) -> AstFileInfo:
    text = path.read_text(encoding="utf-8", errors="ignore")
    info = AstFileInfo(file=str(path), parser="regex")
    info.includes = _read_includes(path, text)

    consumed_ranges: list[tuple[int, int]] = []
    for match in re.finditer(r"\btypedef\s+struct(?:\s+([A-Za-z_]\w*))?\s*\{(?P<body>.*?)\}\s*([A-Za-z_]\w*)\s*;", text, re.DOTALL):
        tag_name = match.group(1)
        alias_name = match.group(3)
        body = match.group("body")
        name = alias_name or tag_name
        if name:
            class_info = ClassInfo(name=name, kind="struct")
            class_info.members = _regex_members(body)
            class_info.dependencies = sorted(_dependencies_from_members(class_info.members) - {name})
            info.classes.append(class_info)
            consumed_ranges.append(match.span())

    for match in re.finditer(r"\btypedef\s+enum(?:\s+([A-Za-z_]\w*))?\s*\{(?P<body>.*?)\}\s*([A-Za-z_]\w*)\s*;", text, re.DOTALL):
        tag_name = match.group(1)
        alias_name = match.group(3)
        body = match.group("body")
        name = alias_name or tag_name
        if name:
            enum_info = ClassInfo(name=name, kind="enum")
            enum_info.members = _regex_enum_literals(body)
            info.classes.append(enum_info)
            consumed_ranges.append(match.span())

    for match in re.finditer(r"\b(class|struct)\s+([A-Za-z_]\w*)[^{;]*\{(?P<body>.*?)\}\s*;", text, re.DOTALL):
        if _overlaps(match.span(), consumed_ranges):
            continue
        kind, name = match.group(1), match.group(2)
        body = match.group("body")
        class_info = ClassInfo(name=name, kind=kind)
        class_info.methods = _regex_methods(body)
        class_info.members = _regex_members(body)
        class_info.dependencies = sorted(_dependencies_from_members(class_info.members) - {name})
        info.classes.append(class_info)

    stripped = _remove_ranges(text, consumed_ranges)
    stripped = re.sub(r"\b(class|struct)\s+[A-Za-z_]\w*[^{;]*\{.*?\}\s*;", "", stripped, flags=re.DOTALL)
    info.functions = _regex_functions(stripped)
    deps = set(_include_dependency_names(info.includes))
    deps.update(_collect_dependencies_from_text(text))
    info.dependencies = sorted(deps)
    return info


def _read_includes(path: Path, text: str | None = None) -> list[str]:
    source = text if text is not None else path.read_text(encoding="utf-8", errors="ignore")
    return re.findall(r"^\s*#\s*include\s+[<\"]([^>\"]+)[>\"]", source, flags=re.MULTILINE)


def _regex_methods(body: str) -> list[MethodInfo]:
    methods: list[MethodInfo] = []
    pattern = re.compile(r"(?P<ret>[A-Za-z_][\w:<>\s*&~]*?)\s+(?P<name>[A-Za-z_]\w*)\s*\((?P<params>[^;{}]*)\)\s*(?:const)?\s*[;{]")
    for match in pattern.finditer(body):
        methods.append(
            MethodInfo(
                name=match.group("name"),
                result_type=" ".join(match.group("ret").split()),
                parameters=_split_parameters(match.group("params")),
            )
        )
    return methods


def _regex_members(body: str) -> list[str]:
    members: list[str] = []
    for line in body.splitlines():
        candidate = line.strip()
        if not candidate or "(" in candidate or not candidate.endswith(";"):
            continue
        if candidate in {"public:", "private:", "protected:"}:
            continue
        members.append(candidate.rstrip(";"))
    return members


def _regex_enum_literals(body: str) -> list[str]:
    literals = []
    for part in body.split(","):
        token = part.strip().split("=", 1)[0].strip()
        if token:
            literals.append(token)
    return literals


def _dependencies_from_members(members: Iterable[str]) -> set[str]:
    dependencies: set[str] = set()
    for member in members:
        dependencies.update(_type_dependencies(_member_type_text(member)))
    return dependencies


def _member_type_text(member: str) -> str:
    tokens = member.split()
    if len(tokens) < 2:
        return member
    return " ".join(tokens[:-1])


def _regex_functions(text: str) -> list[FunctionInfo]:
    functions: list[FunctionInfo] = []
    pattern = re.compile(
        r"(?m)^\s*(?P<ret>[A-Za-z_][\w:<>\s*&]*?)\s+(?P<name>[A-Za-z_]\w*)\s*\((?P<params>[^;{}]*)\)\s*(?:;|\{)"
    )
    control_words = {"if", "for", "while", "switch", "return"}
    for match in pattern.finditer(text):
        name = match.group("name")
        if name not in control_words:
            functions.append(
                FunctionInfo(
                    name=name,
                    result_type=" ".join(match.group("ret").split()),
                    parameters=_split_parameters(match.group("params")),
                )
            )
    return functions


def _overlaps(span: tuple[int, int], ranges: list[tuple[int, int]]) -> bool:
    start, end = span
    return any(start < range_end and end > range_start for range_start, range_end in ranges)


def _remove_ranges(text: str, ranges: list[tuple[int, int]]) -> str:
    if not ranges:
        return text
    chunks = []
    last = 0
    for start, end in sorted(ranges):
        chunks.append(text[last:start])
        last = end
    chunks.append(text[last:])
    return "".join(chunks)


def _split_parameters(value: str) -> list[str]:
    value = value.strip()
    if not value or value == "void":
        return []
    return [" ".join(part.strip().split()) for part in value.split(",") if part.strip()]


def _include_dependency_names(includes: Iterable[str]) -> set[str]:
    names = set()
    for include in includes:
        stem = Path(include).stem
        if stem:
            names.add(stem)
    return names


def _type_dependencies(value: str) -> set[str]:
    primitive = {
        "void",
        "bool",
        "char",
        "short",
        "int",
        "long",
        "float",
        "double",
        "signed",
        "unsigned",
        "const",
        "volatile",
        "static",
        "std",
        "size_t",
        "uint8_t",
        "uint16_t",
        "uint32_t",
        "uint64_t",
        "int8_t",
        "int16_t",
        "int32_t",
        "int64_t",
        "if",
        "else",
        "for",
        "while",
        "switch",
        "return",
        "typedef",
        "struct",
        "enum",
        "extern",
    }
    tokens = set(re.findall(r"\b[A-Za-z_]\w*\b", value))
    return {token for token in tokens if token not in primitive and not token.isupper()}


def _collect_dependencies_from_text(text: str) -> set[str]:
    return _type_dependencies(text)


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract C/C++ design elements into JSON.")
    parser.add_argument("files", nargs="+", help="C/C++ source files")
    parser.add_argument("--compile-arg", action="append", default=[], help="Additional libclang compile argument")
    args = parser.parse_args()
    print(json.dumps(parse_files(args.files, args.compile_arg), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
