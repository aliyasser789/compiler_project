"""tests/test_parser.py — Unit tests for francode.parser.Parser."""

from __future__ import annotations

import pytest

from francode.ast_nodes import (
    Assign,
    BinaryOp,
    Block,
    CallExpr,
    FloatLiteral,
    FuncDef,
    IfStmt,
    IntLiteral,
    Param,
    PrintStmt,
    ReturnStmt,
    VarDecl,
    VarRef,
    VarType,
    WhileStmt,
)
from francode.lexer import Lexer
from francode.parser import Parser, ParserError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse(source: str):
    """Lex + parse *source* and return the Program node."""
    tokens = Lexer(source).tokenize()
    return Parser(tokens).parse()


def parse_first(source: str):
    """Return the first top-level item from parsing *source*."""
    return parse(source).items[0]


# ---------------------------------------------------------------------------
# Variable declarations
# ---------------------------------------------------------------------------

class TestVarDecl:
    def test_rakm_decl_produces_var_decl_node(self) -> None:
        node = parse_first("rakm x = 5;")
        assert isinstance(node, VarDecl)

    def test_rakm_decl_var_type(self) -> None:
        node = parse_first("rakm x = 5;")
        assert node.var_type == VarType.RAKM

    def test_rakm_decl_name(self) -> None:
        node = parse_first("rakm x = 5;")
        assert node.name == "x"

    def test_rakm_decl_initializer_is_int_literal(self) -> None:
        node = parse_first("rakm x = 5;")
        assert isinstance(node.initializer, IntLiteral)
        assert node.initializer.value == 5

    def test_kasr_decl_var_type(self) -> None:
        node = parse_first("kasr y = 3;")
        assert node.var_type == VarType.KASR

    def test_float_initializer(self) -> None:
        node = parse_first("kasr pi = 3;")
        assert isinstance(node.initializer, IntLiteral)

    def test_decl_with_float_literal(self) -> None:
        node = parse_first("kasr pi = 3.14;")
        assert isinstance(node.initializer, FloatLiteral)
        assert node.initializer.value == pytest.approx(3.14)


# ---------------------------------------------------------------------------
# Assignment
# ---------------------------------------------------------------------------

class TestAssignment:
    def test_assignment_produces_assign_node(self) -> None:
        prog = parse("rakm x = 0; x = 10;")
        assert isinstance(prog.items[1], Assign)

    def test_assignment_name(self) -> None:
        prog = parse("rakm x = 0; x = 10;")
        node = prog.items[1]
        assert node.name == "x"

    def test_assignment_value(self) -> None:
        prog = parse("rakm x = 0; x = 10;")
        node = prog.items[1]
        assert isinstance(node.value, IntLiteral)
        assert node.value.value == 10


# ---------------------------------------------------------------------------
# Print statement
# ---------------------------------------------------------------------------

class TestPrintStmt:
    def test_print_produces_print_node(self) -> None:
        node = parse_first("etba3(42);")
        assert isinstance(node, PrintStmt)

    def test_print_value(self) -> None:
        node = parse_first("etba3(42);")
        assert isinstance(node.value, IntLiteral)
        assert node.value.value == 42


# ---------------------------------------------------------------------------
# Return statement
# ---------------------------------------------------------------------------

class TestReturnStmt:
    def test_return_produces_return_node(self) -> None:
        prog = parse("rakm ya f() { raga3 1; }")
        body = prog.items[0].body
        assert isinstance(body.statements[0], ReturnStmt)

    def test_return_value(self) -> None:
        prog = parse("rakm ya f() { raga3 7; }")
        ret = prog.items[0].body.statements[0]
        assert isinstance(ret.value, IntLiteral)
        assert ret.value.value == 7


# ---------------------------------------------------------------------------
# If / elif / else
# ---------------------------------------------------------------------------

class TestIfStmt:
    def test_lw_produces_if_node(self) -> None:
        node = parse_first("lw (1) { etba3(1); }")
        assert isinstance(node, IfStmt)

    def test_lw_condition(self) -> None:
        node = parse_first("lw (1) { etba3(1); }")
        assert isinstance(node.condition, IntLiteral)
        assert node.condition.value == 1

    def test_lw_then_block_has_statement(self) -> None:
        node = parse_first("lw (1) { etba3(1); }")
        assert isinstance(node.then_block, Block)
        assert len(node.then_block.statements) == 1

    def test_aw_produces_else_block(self) -> None:
        node = parse_first("lw (1) { etba3(1); } aw { etba3(0); }")
        assert node.else_block is not None

    def test_no_aw_gives_none_else_block(self) -> None:
        node = parse_first("lw (1) { etba3(1); }")
        assert node.else_block is None

    def test_tb_lw_produces_elif_part(self) -> None:
        src = "lw (1) { etba3(1); } tb lw (0) { etba3(0); }"
        node = parse_first(src)
        assert len(node.elif_parts) == 1

    def test_multiple_elif_parts(self) -> None:
        src = (
            "lw (1) { etba3(1); } "
            "tb lw (0) { etba3(2); } "
            "tb lw (0) { etba3(3); }"
        )
        node = parse_first(src)
        assert len(node.elif_parts) == 2


# ---------------------------------------------------------------------------
# While loop
# ---------------------------------------------------------------------------

class TestWhileStmt:
    def test_tol_lma_produces_while_node(self) -> None:
        node = parse_first("tol lma (1) { etba3(1); }")
        assert isinstance(node, WhileStmt)

    def test_while_condition(self) -> None:
        node = parse_first("tol lma (1) { etba3(1); }")
        assert isinstance(node.condition, IntLiteral)

    def test_while_body_is_block(self) -> None:
        node = parse_first("tol lma (1) { etba3(1); }")
        assert isinstance(node.body, Block)


# ---------------------------------------------------------------------------
# Function definition
# ---------------------------------------------------------------------------

class TestFuncDef:
    def test_func_def_produces_func_def_node(self) -> None:
        node = parse_first("rakm ya add(rakm a, rakm b) { raga3 a; }")
        assert isinstance(node, FuncDef)

    def test_func_def_name(self) -> None:
        node = parse_first("rakm ya add(rakm a, rakm b) { raga3 a; }")
        assert node.name == "add"

    def test_func_def_return_type_rakm(self) -> None:
        node = parse_first("rakm ya f(rakm x) { raga3 x; }")
        assert node.return_type == VarType.RAKM

    def test_func_def_return_type_kasr(self) -> None:
        node = parse_first("kasr ya f(rakm x) { raga3 x; }")
        assert node.return_type == VarType.KASR

    def test_func_def_param_count(self) -> None:
        node = parse_first("rakm ya add(rakm a, rakm b) { raga3 a; }")
        assert len(node.params) == 2

    def test_func_def_param_names(self) -> None:
        node = parse_first("rakm ya add(rakm a, rakm b) { raga3 a; }")
        assert node.params[0].name == "a"
        assert node.params[1].name == "b"

    def test_func_def_param_types(self) -> None:
        node = parse_first("rakm ya f(rakm a, kasr b) { raga3 a; }")
        assert node.params[0].var_type == VarType.RAKM
        assert node.params[1].var_type == VarType.KASR

    def test_func_def_no_params(self) -> None:
        node = parse_first("rakm ya f() { raga3 1; }")
        assert node.params == []


# ---------------------------------------------------------------------------
# Function calls (CallExpr)
# ---------------------------------------------------------------------------

class TestCallExpr:
    def test_call_expr_produces_call_node(self) -> None:
        # parse inside a print so we get a CallExpr
        node = parse_first("etba3(add(1, 2));")
        assert isinstance(node.value, CallExpr)

    def test_call_expr_callee(self) -> None:
        node = parse_first("etba3(add(1, 2));")
        assert node.value.callee == "add"

    def test_call_expr_args(self) -> None:
        node = parse_first("etba3(add(1, 2));")
        assert len(node.value.args) == 2

    def test_call_expr_no_args(self) -> None:
        node = parse_first("etba3(f());")
        assert isinstance(node.value, CallExpr)
        assert node.value.args == []


# ---------------------------------------------------------------------------
# Operator precedence
# ---------------------------------------------------------------------------

class TestOperatorPrecedence:
    def test_mul_binds_tighter_than_add(self) -> None:
        # 1 + 2 * 3  should parse as  1 + (2 * 3)
        # i.e. the root BinaryOp has op='+' and right is another BinaryOp with op='*'
        node = parse_first("etba3(1 + 2 * 3);")
        expr = node.value
        assert isinstance(expr, BinaryOp)
        assert expr.op == "+"
        assert isinstance(expr.right, BinaryOp)
        assert expr.right.op == "*"

    def test_add_left_associative(self) -> None:
        # 1 + 2 + 3  →  (1 + 2) + 3  — left is another BinaryOp
        node = parse_first("etba3(1 + 2 + 3);")
        expr = node.value
        assert isinstance(expr, BinaryOp)
        assert expr.op == "+"
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.op == "+"

    def test_comparison_is_lowest_precedence(self) -> None:
        # 1 + 2 < 3 + 4  →  (1+2) < (3+4)
        node = parse_first("etba3(1 + 2 < 3 + 4);")
        expr = node.value
        assert isinstance(expr, BinaryOp)
        assert expr.op == "<"
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.op == "+"

    def test_parentheses_override_precedence(self) -> None:
        # (1 + 2) * 3  — root op is *, left is the + group
        node = parse_first("etba3((1 + 2) * 3);")
        expr = node.value
        assert isinstance(expr, BinaryOp)
        assert expr.op == "*"
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.op == "+"


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

class TestParserErrors:
    def test_missing_semicolon_raises_parser_error(self) -> None:
        with pytest.raises(ParserError):
            parse("rakm x = 5")  # no semicolon

    def test_missing_semicolon_after_print_raises_error(self) -> None:
        with pytest.raises(ParserError):
            parse("etba3(1)")  # no semicolon

    def test_unterminated_block_raises_parser_error(self) -> None:
        with pytest.raises(ParserError):
            parse("lw (1) { etba3(1);")  # no closing }

    def test_missing_return_type_before_ya_raises_error(self) -> None:
        with pytest.raises(ParserError):
            parse("ya add() { raga3 1; }")  # 'ya' without return type

    def test_missing_lparen_after_lw_raises_error(self) -> None:
        with pytest.raises(ParserError):
            parse("lw 1 { etba3(1); }")

    def test_missing_rparen_in_function_call_raises_error(self) -> None:
        with pytest.raises(ParserError):
            parse("etba3(1 + 2;")
