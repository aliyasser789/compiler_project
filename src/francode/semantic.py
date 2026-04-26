from __future__ import annotations

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
    Node,
    PrintStmt,
    Program,
    ReturnStmt,
    Stmt,
    VarDecl,
    VarRef,
    VarType,
    WhileStmt,
)


@dataclass(slots=True)
class SemanticError(Exception):
    """Error raised when semantic rules are violated."""

    message: str
    line: int
    col: int

    def __str__(self) -> str:
        """Return a human-readable semantic error message."""
        return f"SemanticError at line {self.line} col {self.col}: {self.message}"


@dataclass(slots=True)
class FuncSymbol:
    """Function symbol entry stored in the semantic function table."""

    name: str
    return_type: VarType
    param_types: list[VarType]


class SemanticAnalyzer:
    """Two-pass semantic analyzer for Codawy v0.1."""

    def __init__(self) -> None:
        self.scopes: list[dict[str, VarType]] = []
        self.functions: dict[str, FuncSymbol] = {}
        self.current_function: FuncSymbol | None = None

    def analyze(self, program: Program) -> None:
        """Run semantic analysis on a program AST."""
        self.pass1_collect_functions(program)
        self.pass2_check_program(program)

    def pass1_collect_functions(self, program: Program) -> None:
        """Collect all function signatures before statement checking."""
        for item in program.items:
            if not isinstance(item, FuncDef):
                continue

            if item.name in self.functions:
                self._error(f"Duplicate function declaration '{item.name}'", item)

            seen_params: set[str] = set()
            for param in item.params:
                if param.name in seen_params:
                    self._error(
                        f"Duplicate parameter name '{param.name}' in function '{item.name}'",
                        param,
                    )
                seen_params.add(param.name)

            self.functions[item.name] = FuncSymbol(
                name=item.name,
                return_type=item.return_type,
                param_types=[param.var_type for param in item.params],
            )

    def pass2_check_program(self, program: Program) -> None:
        """Type-check top-level items using collected function signatures."""
        self.scopes = [{}]
        self.current_function = None

        for item in program.items:
            if isinstance(item, FuncDef):
                self._check_function(item)
            else:
                self.check_stmt(item)

    def check_stmt(self, stmt: Stmt) -> None:
        """Validate a statement against active scopes/function context."""
        if isinstance(stmt, VarDecl):
            scope = self._current_scope()
            if stmt.name in scope:
                self._error(
                    f"Redeclaration of variable '{stmt.name}' in the same scope",
                    stmt,
                )
            init_type = self.infer_expr_type(stmt.initializer)
            if not self._is_convertible(init_type, stmt.var_type):
                self._error(
                    f"Cannot initialize variable '{stmt.name}' of type {stmt.var_type.name} "
                    f"with expression of type {init_type.name}",
                    stmt,
                )
            scope[stmt.name] = stmt.var_type
            return

        if isinstance(stmt, Assign):
            target_type = self._lookup_var(stmt.name)
            if target_type is None:
                self._error(f"Assignment to undeclared variable '{stmt.name}'", stmt)
            value_type = self.infer_expr_type(stmt.value)
            if not self._is_convertible(value_type, target_type):
                self._error(
                    f"Cannot assign expression of type {value_type.name} "
                    f"to variable '{stmt.name}' of type {target_type.name}",
                    stmt,
                )
            return

        if isinstance(stmt, PrintStmt):
            self.infer_expr_type(stmt.value)
            return

        if isinstance(stmt, ReturnStmt):
            if self.current_function is None:
                self._error("'raga3' is only allowed inside a function", stmt)
            if stmt.value is None:
                self._error("'raga3' requires a return expression in Codawy v0.1", stmt)
            value_type = self.infer_expr_type(stmt.value)
            if not self._is_convertible(value_type, self.current_function.return_type):
                self._error(
                    f"Return type mismatch in function '{self.current_function.name}': "
                    f"expected {self.current_function.return_type.name}, got {value_type.name}",
                    stmt,
                )
            return

        if isinstance(stmt, IfStmt):
            self.check_condition(stmt.condition)
            self._check_block(stmt.then_block)
            for elif_cond, elif_block in stmt.elif_parts:
                self.check_condition(elif_cond)
                self._check_block(elif_block)
            if stmt.else_block is not None:
                self._check_block(stmt.else_block)
            return

        if isinstance(stmt, WhileStmt):
            self.check_condition(stmt.condition)
            self._check_block(stmt.body)
            return

        if isinstance(stmt, Block):
            self._check_block(stmt)
            return

        self._error(f"Unsupported statement node: {type(stmt).__name__}", stmt)

    def infer_expr_type(self, expr: Expr) -> VarType:
        """Infer and validate the resulting type of an expression."""
        if isinstance(expr, IntLiteral):
            return VarType.RAKM

        if isinstance(expr, FloatLiteral):
            return VarType.KASR

        if isinstance(expr, VarRef):
            var_type = self._lookup_var(expr.name)
            if var_type is None:
                self._error(f"Use of undeclared variable '{expr.name}'", expr)
            return var_type

        if isinstance(expr, CallExpr):
            symbol = self.functions.get(expr.callee)
            if symbol is None:
                self._error(f"Call to undefined function '{expr.callee}'", expr)

            if len(expr.args) != len(symbol.param_types):
                self._error(
                    f"Function '{expr.callee}' expects {len(symbol.param_types)} argument(s), "
                    f"got {len(expr.args)}",
                    expr,
                )

            for idx, (arg_expr, param_type) in enumerate(
                zip(expr.args, symbol.param_types), start=1
            ):
                arg_type = self.infer_expr_type(arg_expr)
                if not self._is_convertible(arg_type, param_type):
                    self._error(
                        f"Argument {idx} for function '{expr.callee}' has type "
                        f"{arg_type.name}, expected {param_type.name}",
                        arg_expr,
                    )

            return symbol.return_type

        if isinstance(expr, BinaryOp):
            left_type = self.infer_expr_type(expr.left)
            right_type = self.infer_expr_type(expr.right)

            if expr.op == "/":
                return VarType.KASR

            if expr.op in {"==", "!=", "<", ">", "<=", ">="}:
                return VarType.RAKM

            if expr.op in {"+", "-", "*"}:
                if left_type == VarType.KASR or right_type == VarType.KASR:
                    return VarType.KASR
                return VarType.RAKM

            self._error(f"Unsupported binary operator '{expr.op}'", expr)

        self._error(f"Unsupported expression node: {type(expr).__name__}", expr)

    def check_condition(self, expr: Expr) -> None:
        """Enforce Codawy v0.1 condition form restrictions."""
        if isinstance(expr, IntLiteral) and expr.value in (0, 1):
            return

        if isinstance(expr, BinaryOp) and expr.op in {
            "==",
            "!=",
            "<",
            ">",
            "<=",
            ">=",
        }:
            # Ensure both sides are semantically valid expressions.
            self.infer_expr_type(expr.left)
            self.infer_expr_type(expr.right)
            return

        self._error(
            "Condition must be IntLiteral(0/1) or a comparison expression "
            "(==, !=, <, >, <=, >=)",
            expr,
        )

    def _check_function(self, func: FuncDef) -> None:
        """Validate function body within function-local scope context."""
        symbol = self.functions[func.name]
        prev_function = self.current_function
        self.current_function = symbol

        self._push_scope()
        try:
            for param in func.params:
                scope = self._current_scope()
                if param.name in scope:
                    # Defensive check; pass1 already validates this.
                    self._error(
                        f"Duplicate parameter name '{param.name}' in function '{func.name}'",
                        param,
                    )
                scope[param.name] = param.var_type

            self._check_block(func.body)
            if not self._contains_return(func.body):
                self._error(
                    f"Function '{func.name}' must contain at least one 'raga3' statement",
                    func,
                )
        finally:
            self._pop_scope()
            self.current_function = prev_function

    def _check_block(self, block: Block) -> None:
        """Check block statements in a new nested lexical scope."""
        self._push_scope()
        try:
            for stmt in block.statements:
                self.check_stmt(stmt)
        finally:
            self._pop_scope()

    def _contains_return(self, block: Block) -> bool:
        """Return True if block contains at least one return statement recursively."""
        for stmt in block.statements:
            if isinstance(stmt, ReturnStmt):
                return True

            if isinstance(stmt, Block) and self._contains_return(stmt):
                return True

            if isinstance(stmt, IfStmt):
                if self._contains_return(stmt.then_block):
                    return True
                for _, elif_block in stmt.elif_parts:
                    if self._contains_return(elif_block):
                        return True
                if stmt.else_block is not None and self._contains_return(stmt.else_block):
                    return True

            if isinstance(stmt, WhileStmt) and self._contains_return(stmt.body):
                return True

        return False

    def _is_convertible(self, src: VarType, dst: VarType) -> bool:
        """Return whether a value of src type can be converted to dst type."""
        return src in {VarType.RAKM, VarType.KASR} and dst in {VarType.RAKM, VarType.KASR}

    def _lookup_var(self, name: str) -> VarType | None:
        """Look up a variable name from innermost to outermost scope."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def _push_scope(self) -> None:
        """Push a new variable scope."""
        self.scopes.append({})

    def _pop_scope(self) -> None:
        """Pop the innermost variable scope."""
        self.scopes.pop()

    def _current_scope(self) -> dict[str, VarType]:
        """Return the current innermost variable scope."""
        if not self.scopes:
            self._error("Internal semantic analyzer error: no active scope")
        return self.scopes[-1]

    def _error(self, message: str, node: Node | None = None) -> None:
        """Raise a semantic error, using the node's source location when available."""
        if node is not None:
            raise SemanticError(message, node.line, node.col)
        raise SemanticError(message, 0, 0)


# Example semantic errors:
# - Redeclaration of variable 'x' in the same scope
# - Call to undefined function 'sum'
# - 'raga3' is only allowed inside a function
# - Condition must be IntLiteral(0/1) or a comparison expression


__all__ = ["SemanticAnalyzer", "SemanticError", "FuncSymbol"]
