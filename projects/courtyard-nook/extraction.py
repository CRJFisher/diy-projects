from __future__ import annotations

import ast
import math
import re
from pathlib import Path
from typing import Any

ASSIGNMENT_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$", re.DOTALL)
INCLUDE_RE = re.compile(r"^\s*include\s*<([^>]+)>")
BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)

# OpenSCAD's trig works in degrees, Python's in radians.
FUNCTIONS = {
    "sin": lambda x: math.sin(math.radians(x)),
    "cos": lambda x: math.cos(math.radians(x)),
    "tan": lambda x: math.tan(math.radians(x)),
    "asin": lambda x: math.degrees(math.asin(x)),
    "acos": lambda x: math.degrees(math.acos(x)),
    "atan": lambda x: math.degrees(math.atan(x)),
    "atan2": lambda y, x: math.degrees(math.atan2(y, x)),
    "sqrt": math.sqrt,
    "abs": abs,
    "sign": lambda x: (x > 0) - (x < 0),
    "floor": math.floor,
    "ceil": math.ceil,
    "round": round,
    "pow": pow,
    "exp": math.exp,
    "ln": math.log,
    "log": math.log10,
    "min": min,
    "max": max,
}


def parse_parameters(path: Path) -> dict[str, Any]:
    """Evaluate `model/parameters.scad` and everything it includes.

    `parameters.scad` holds the shed's build dimensions and includes
    `site.scad`, which holds the measured site constraints it derives from.
    Both are needed before any assignment resolves.
    """
    assignments = _collect_assignments(Path(path), seen=set())

    values: dict[str, Any] = {}
    pending = assignments
    while pending:
        next_pending: list[tuple[str, str]] = []
        progressed = False
        for name, expr in pending:
            try:
                values[name] = _eval_expression(expr, values)
            except (KeyError, ValueError, TypeError, SyntaxError, ZeroDivisionError):
                next_pending.append((name, expr))
            else:
                progressed = True
        if not progressed:
            unresolved = ", ".join(f"{name}={expr}" for name, expr in next_pending)
            raise ValueError(f"Unable to evaluate OpenSCAD parameters: {unresolved}")
        pending = next_pending
    return values


def _collect_assignments(path: Path, seen: set[Path]) -> list[tuple[str, str]]:
    """Depth-first walk of `include <...>`, included files first.

    Statements are gathered by splitting on `;`, not by line, so an assignment
    whose expression wraps across several lines is read whole. Splitting on
    lines instead would silently assign the first line's fragment.
    """
    resolved = path.resolve()
    if resolved in seen:
        return []
    seen.add(resolved)

    assignments: list[tuple[str, str]] = []
    buffer: list[str] = []

    def flush() -> None:
        for statement in "".join(buffer).split(";"):
            statement = statement.strip()
            if not statement:
                continue
            match = ASSIGNMENT_RE.match(statement)
            if match:
                name, expr = match.groups()
                assignments.append((name, " ".join(expr.split())))
        buffer.clear()

    text = BLOCK_COMMENT_RE.sub(" ", resolved.read_text())
    for raw_line in text.splitlines():
        include = INCLUDE_RE.match(raw_line)
        if include:
            # Included assignments must land before anything already buffered
            # can reference them, so close off the buffer first.
            flush()
            assignments.extend(
                _collect_assignments(resolved.parent / include.group(1), seen)
            )
            continue
        buffer.append(raw_line.split("//", 1)[0] + " ")
    flush()
    return assignments


def _eval_expression(expr: str, values: dict[str, Any]) -> Any:
    expr = expr.replace("true", "True").replace("false", "False")
    tree = ast.parse(expr, mode="eval")
    return _eval_node(tree.body, values)


def _eval_node(node: ast.AST, values: dict[str, Any]) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return values[node.id]
    if isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand, values)
        if isinstance(node.op, ast.USub):
            return -operand
        if isinstance(node.op, ast.UAdd):
            return operand
    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left, values)
        right = _eval_node(node.right, values)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Mod):
            return left % right
        if isinstance(node.op, ast.Pow):
            return left**right
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in FUNCTIONS:
            raise ValueError(f"Unsupported function: {ast.dump(node)}")
        return FUNCTIONS[node.func.id](
            *(_eval_node(arg, values) for arg in node.args)
        )
    if isinstance(node, ast.Tuple):
        return tuple(_eval_node(element, values) for element in node.elts)
    if isinstance(node, ast.List):
        return [_eval_node(element, values) for element in node.elts]
    raise ValueError(f"Unsupported expression: {ast.dump(node)}")


def build_cut_list_rows(parameters: dict[str, Any]) -> list[dict[str, Any]]:
    """No rows yet — the shed itself is not designed.

    Once `model/parameters.scad` carries the frame / roof / cladding / floor
    sections listed in its TODO block, emit a row per cut here (see
    `projects/bin-store/extraction.py` for the shape and `add_row` helper).
    """
    del parameters
    return []
