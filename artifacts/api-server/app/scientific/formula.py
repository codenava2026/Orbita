import ast
from dataclasses import dataclass

import sympy as sp

from app.core.exceptions import InvalidFormula

ALLOWED_FUNCTIONS = {
    "sqrt": sp.sqrt,
    "exp": sp.exp,
    "log": sp.log,
    "sin": sp.sin,
    "cos": sp.cos,
}
ALLOWED_BINARY_OPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod)


def _convert(node: ast.AST, symbols: dict[str, sp.Symbol]) -> sp.Expr:
    if isinstance(node, ast.Expression):
        return _convert(node.body, symbols)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return sp.Float(node.value) if isinstance(node.value, float) else sp.Integer(node.value)
    if isinstance(node, ast.Name):
        if node.id not in symbols:
            symbols[node.id] = sp.Symbol(node.id)
        return symbols[node.id]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _convert(node.operand, symbols)
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ALLOWED_BINARY_OPS):
        left, right = _convert(node.left, symbols), _convert(node.right, symbols)
        operations = {
            ast.Add: lambda: left + right,
            ast.Sub: lambda: left - right,
            ast.Mult: lambda: left * right,
            ast.Div: lambda: left / right,
            ast.Pow: lambda: left**right,
            ast.Mod: lambda: sp.Mod(left, right),
        }
        return operations[type(node.op)]()
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ALLOWED_FUNCTIONS:
        if node.keywords or len(node.args) != 1:
            raise InvalidFormula("Formula functions accept exactly one positional argument")
        return ALLOWED_FUNCTIONS[node.func.id](_convert(node.args[0], symbols))
    raise InvalidFormula(f"Unsupported formula syntax: {ast.dump(node, include_attributes=False)}")


@dataclass(frozen=True)
class ParsedFormula:
    human_expression: str
    expression: sp.Expr
    variables: tuple[str, ...]

    @property
    def symbolic_expression(self) -> str:
        return str(self.expression)

    @property
    def canonical_expression(self) -> str:
        return sp.srepr(self.expression)


def parse_formula(expression: str) -> ParsedFormula:
    if not expression.strip():
        raise InvalidFormula("Formula cannot be empty")
    try:
        tree = ast.parse(expression, mode="eval")
        symbols: dict[str, sp.Symbol] = {}
        parsed = sp.simplify(_convert(tree, symbols))
    except (SyntaxError, ValueError, TypeError, InvalidFormula) as exc:
        if isinstance(exc, InvalidFormula):
            raise
        raise InvalidFormula("Formula could not be parsed safely") from exc
    return ParsedFormula(expression, parsed, tuple(sorted(symbols)))


class FormulaEvaluator:
    """Evaluates previously parsed symbolic expressions with explicit substitutions."""

    @staticmethod
    def evaluate(parsed: ParsedFormula, values: dict[str, float]) -> float:
        unknown = set(values) - set(parsed.variables)
        missing = set(parsed.variables) - set(values)
        if unknown or missing:
            raise InvalidFormula(f"Variable mismatch; unknown={sorted(unknown)}, missing={sorted(missing)}")
        return float(parsed.expression.evalf(subs=values))