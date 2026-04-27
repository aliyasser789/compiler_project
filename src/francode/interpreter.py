"""
interpreter.py — Francode tree-walk interpreter (Phase 3, Steps 3.1–3.6).

Execution model:
  - Plain Python int / float are the only runtime value types.
  - Division always produces float; float-to-int truncates toward zero via int().
  - Conditions must evaluate to exactly 0 or 1; anything else is a runtime error.
  - ReturnSignal (a Python exception) unwinds the call stack on raga3.
  - Recursion depth is capped at _MAX_CALL_DEPTH to catch infinite recursion.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass

from francode.ast_nodes import (
    Assign,
    BinaryOp,
    Block,
    CallExpr,
    Expr,
    FloatLiteral,
    FuncDef,
    IfStmt,
    IntLiteral,
    PrintStmt,
    Program,
    ReturnStmt,
    Stmt,
    VarDecl,
    VarRef,
    VarType,
    WhileStmt,
)

# Runtime value: plain Python int or float — no wrapper classes.
Value = int | float

# Maximum call depth before raising a stack-overflow runtime error.
_MAX_CALL_DEPTH: int = 500


# ---------------------------------------------------------------------------
# Step 3.6 — Runtime error
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class FrancodeRuntimeError(Exception):
    """Raised when a recoverable runtime rule is violated."""

    message: str
    line: int
    col: int

    def __str__(self) -> str:
        return f"RuntimeError at line {self.line} col {self.col}: {self.message}"


# ---------------------------------------------------------------------------
# Internal signal — NOT a user-visible error
# ---------------------------------------------------------------------------

class ReturnSignal(Exception):
    """Raised by ReturnStmt to unwind the call stack back to the call site."""

    __slots__ = ("value",)

    def __init__(self, value: Value) -> None:
        self.value = value


# ---------------------------------------------------------------------------
# Step 3.1 — Environment (variable store with parent chaining)
# ---------------------------------------------------------------------------

class Environment:
    """Lexically scoped variable store.

    Each scope holds its own name→value mapping.  Lookups and mutations
    walk the parent chain from innermost to outermost scope.
    """

    __slots__ = ("_store", "_parent")

    def __init__(self, parent: Environment | None = None) -> None:
        self._store: dict[str, Value] = {}
        self._parent = parent

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def define(self, name: str, value: Value) -> None:
        """Bind *name* to *value* in the current scope.

        Raises FrancodeRuntimeError if *name* is already defined HERE
        (shadowing a parent binding is fine).
        """
        if name in self._store:
            raise FrancodeRuntimeError(
                f"Variable '{name}' is already declared in this scope", 0, 0
            )
        self._store[name] = value

    def get(self, name: str, line: int = 0, col: int = 0) -> Value:
        """Return the value bound to *name* in the nearest enclosing scope."""
        if name in self._store:
            return self._store[name]
        if self._parent is not None:
            return self._parent.get(name, line, col)
        raise FrancodeRuntimeError(
            f"Undefined variable '{name}'", line, col
        )

    def set(self, name: str, value: Value, line: int = 0, col: int = 0) -> None:
        """Update the binding of *name* in the nearest enclosing scope that owns it."""
        if name in self._store:
            self._store[name] = value
            return
        if self._parent is not None:
            self._parent.set(name, value, line, col)
            return
        raise FrancodeRuntimeError(
            f"Assignment to undeclared variable '{name}'", line, col
        )


# ---------------------------------------------------------------------------
# Step 3.2 — Type conversion helpers
# ---------------------------------------------------------------------------

def _to_int(v: Value) -> int:
    """Truncate a float toward zero; leave int unchanged."""
    return int(v)  # int(float) truncates toward zero in Python


def _coerce(v: Value, target: VarType) -> Value:
    """Apply the declared variable type to a runtime value."""
    if target == VarType.RAKM:
        return _to_int(v)
    # KASR — promote int to float
    return float(v)


# ---------------------------------------------------------------------------
# Step 3.3 + 3.4 + 3.5 — The interpreter
# ---------------------------------------------------------------------------

class Interpreter:
    """Executes a Francode Program AST produced by the parser + semantic analyzer."""

    def __init__(self) -> None:
        # Global environment holds function definitions and top-level variables.
        self._globals: Environment = Environment()
        # Current call depth — used to detect infinite recursion.
        self._call_depth: int = 0

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def execute(self, program: Program) -> None:
        """Run a fully analysed Program AST."""
        # First pass: register all FuncDef nodes in the global env so that
        # forward calls work (functions defined after the call site).
        for item in program.items:
            if isinstance(item, FuncDef):
                self._exec_funcdef(item, self._globals)

        # Second pass: execute top-level statements in order.
        for item in program.items:
            if not isinstance(item, FuncDef):
                self._exec_stmt(item, self._globals)

    # ------------------------------------------------------------------
    # Step 3.4 — Statement executor
    # ------------------------------------------------------------------

    def _exec_stmt(self, stmt: Stmt, env: Environment) -> None:
        """Dispatch a statement node to the appropriate executor."""

        if isinstance(stmt, VarDecl):
            # Evaluate the initializer, apply declared type, bind in current scope.
            raw = self._eval_expr(stmt.initializer, env)
            value = _coerce(raw, stmt.var_type)
            env.define(stmt.name, value)
            return

        if isinstance(stmt, Assign):
            # Evaluate the new value and update the binding in the owning scope.
            raw = self._eval_expr(stmt.value, env)
            # Look up current type to apply the correct coercion.
            existing = env.get(stmt.name, stmt.line, stmt.col)
            target_type = VarType.KASR if isinstance(existing, float) else VarType.RAKM
            value = _coerce(raw, target_type)
            env.set(stmt.name, value, stmt.line, stmt.col)
            return

        if isinstance(stmt, PrintStmt):
            value = self._eval_expr(stmt.value, env)
            # Print int without decimal point, float with full precision.
            if isinstance(value, int):
                print(value)
            else:
                # Use Python's default float repr (e.g. 3.5, not 3.500000).
                print(value)
            return

        if isinstance(stmt, ReturnStmt):
            if stmt.value is None:
                # Semantic analyzer guarantees this never happens in v0.1.
                raise ReturnSignal(0)
            value = self._eval_expr(stmt.value, env)
            raise ReturnSignal(value)

        if isinstance(stmt, Block):
            self._exec_block(stmt, env)
            return

        if isinstance(stmt, IfStmt):
            self._exec_if(stmt, env)
            return

        if isinstance(stmt, WhileStmt):
            self._exec_while(stmt, env)
            return

        if isinstance(stmt, FuncDef):
            # A FuncDef appearing at a non-global level (unusual but possible).
            self._exec_funcdef(stmt, env)
            return

        raise FrancodeRuntimeError(
            f"Unsupported statement node: {type(stmt).__name__}",
            getattr(stmt, "line", 0),
            getattr(stmt, "col", 0),
        )

    def _exec_block(self, block: Block, parent_env: Environment) -> None:
        """Execute a block in a new child scope."""
        env = Environment(parent=parent_env)
        for stmt in block.statements:
            self._exec_stmt(stmt, env)

    def _exec_if(self, stmt: IfStmt, env: Environment) -> None:
        """Evaluate condition and execute the matching branch."""
        cond_val = self._eval_condition(stmt.condition, env)
        if cond_val == 1:
            self._exec_block(stmt.then_block, env)
            return

        for elif_cond, elif_block in stmt.elif_parts:
            if self._eval_condition(elif_cond, env) == 1:
                self._exec_block(elif_block, env)
                return

        if stmt.else_block is not None:
            self._exec_block(stmt.else_block, env)

    def _exec_while(self, stmt: WhileStmt, env: Environment) -> None:
        """Loop while the condition evaluates to 1; stop when it evaluates to 0."""
        while True:
            cond_val = self._eval_condition(stmt.condition, env)
            if cond_val == 0:
                break
            self._exec_block(stmt.body, env)

    def _exec_funcdef(self, func: FuncDef, env: Environment) -> None:
        """Store the FuncDef AST node in the environment as a callable value."""
        # We store the node itself; _call_function retrieves it on call.
        # Environment.define expects a Value (int | float) — store as a
        # special sentinel by abusing the dict directly to avoid the type constraint.
        env._store[func.name] = func  # type: ignore[assignment]

    # ------------------------------------------------------------------
    # Step 3.5 — Function calls
    # ------------------------------------------------------------------

    def _call_function(self, func: FuncDef, args: list[Value], line: int, col: int) -> Value:
        """Create a child environment, bind params, run body, return value."""
        # Step 3.6 — guard against infinite recursion.
        self._call_depth += 1
        if self._call_depth > _MAX_CALL_DEPTH:
            self._call_depth -= 1
            raise FrancodeRuntimeError(
                f"Stack overflow: maximum call depth ({_MAX_CALL_DEPTH}) exceeded "
                f"in function '{func.name}'",
                line,
                col,
            )

        # Build a fresh scope that is a child of globals so that functions can
        # see each other but not callers' local variables (static scoping).
        call_env = Environment(parent=self._globals)

        # Bind parameters, applying the declared type coercion.
        for param, arg_val in zip(func.params, args):
            coerced = _coerce(arg_val, param.var_type)
            call_env.define(param.name, coerced)

        try:
            self._exec_block(func.body, call_env)
            # Semantic analyzer guarantees every path returns; reaching here is
            # a compiler bug, but we return a safe default instead of crashing.
            return_value: Value = 0
        except ReturnSignal as sig:
            return_value = sig.value
        finally:
            self._call_depth -= 1

        # Apply declared return type coercion.
        return _coerce(return_value, func.return_type)

    # ------------------------------------------------------------------
    # Step 3.3 — Expression evaluator
    # ------------------------------------------------------------------

    def _eval_expr(self, expr: Expr, env: Environment) -> Value:
        """Evaluate an expression and return its runtime value."""

        if isinstance(expr, IntLiteral):
            return expr.value  # already int

        if isinstance(expr, FloatLiteral):
            return expr.value  # already float

        if isinstance(expr, VarRef):
            return env.get(expr.name, expr.line, expr.col)

        if isinstance(expr, BinaryOp):
            return self._eval_binary(expr, env)

        if isinstance(expr, CallExpr):
            return self._eval_call(expr, env)

        raise FrancodeRuntimeError(
            f"Unsupported expression node: {type(expr).__name__}",
            getattr(expr, "line", 0),
            getattr(expr, "col", 0),
        )

    def _eval_binary(self, expr: BinaryOp, env: Environment) -> Value:
        """Evaluate a binary operation according to Francode type rules."""
        left = self._eval_expr(expr.left, env)
        right = self._eval_expr(expr.right, env)

        op = expr.op

        # --- Arithmetic ---
        if op == "+":
            result = left + right
            # Preserve int if both operands are int.
            return result if isinstance(left, float) or isinstance(right, float) else int(result)

        if op == "-":
            result = left - right
            return result if isinstance(left, float) or isinstance(right, float) else int(result)

        if op == "*":
            result = left * right
            return result if isinstance(left, float) or isinstance(right, float) else int(result)

        if op == "/":
            # Step 3.2 — division always returns float.
            if right == 0:
                raise FrancodeRuntimeError(
                    "Division by zero", expr.line, expr.col
                )
            return float(left) / float(right)

        # --- Comparisons — always return int 1 or 0 ---
        if op == "==":
            return 1 if left == right else 0
        if op == "!=":
            return 1 if left != right else 0
        if op == "<":
            return 1 if left < right else 0
        if op == ">":
            return 1 if left > right else 0
        if op == "<=":
            return 1 if left <= right else 0
        if op == ">=":
            return 1 if left >= right else 0

        raise FrancodeRuntimeError(
            f"Unknown binary operator '{op}'", expr.line, expr.col
        )

    def _eval_call(self, expr: CallExpr, env: Environment) -> Value:
        """Look up a function and execute it with evaluated arguments."""
        # Retrieve FuncDef from the environment's raw store (bypassing the type guard).
        func_node = self._globals._store.get(expr.callee)  # type: ignore[assignment]
        if not isinstance(func_node, FuncDef):
            raise FrancodeRuntimeError(
                f"Undefined function '{expr.callee}'", expr.line, expr.col
            )

        # Evaluate all arguments before entering the call.
        args: list[Value] = [self._eval_expr(arg, env) for arg in expr.args]

        return self._call_function(func_node, args, expr.line, expr.col)

    # ------------------------------------------------------------------
    # Condition validation helper (Step 3.6)
    # ------------------------------------------------------------------

    def _eval_condition(self, expr: Expr, env: Environment) -> int:
        """Evaluate *expr* and validate it is 0 or 1.

        The semantic analyzer already guarantees conditions are comparisons or
        IntLiteral(0/1), but we validate at runtime too for safety.
        """
        value = self._eval_expr(expr, env)
        if value == 0:
            return 0
        if value == 1:
            return 1
        raise FrancodeRuntimeError(
            f"Condition must evaluate to 0 or 1, got {value!r}",
            getattr(expr, "line", 0),
            getattr(expr, "col", 0),
        )


__all__ = [
    "Interpreter",
    "Environment",
    "FrancodeRuntimeError",
    "ReturnSignal",
    "Value",
]
