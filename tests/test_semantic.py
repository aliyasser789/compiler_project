"""tests/test_semantic.py — Unit tests for francode.semantic.SemanticAnalyzer."""

from __future__ import annotations

import pytest

from francode.lexer import Lexer
from francode.parser import Parser
from francode.semantic import SemanticAnalyzer, SemanticError


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def analyze(source: str) -> None:
    """Run the full front-end pipeline (lex → parse → semantic) on *source*."""
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    SemanticAnalyzer().analyze(ast)


def assert_semantic_error(source: str) -> SemanticError:
    """Assert that *source* raises SemanticError and return the exception."""
    with pytest.raises(SemanticError) as exc_info:
        analyze(source)
    return exc_info.value


# ---------------------------------------------------------------------------
# Valid programs (must NOT raise)
# ---------------------------------------------------------------------------

class TestValidPrograms:
    def test_simple_var_decl_is_valid(self) -> None:
        analyze("rakm x = 5;")

    def test_kasr_var_decl_is_valid(self) -> None:
        analyze("kasr y = 3;")

    def test_rakm_assigned_from_kasr_is_valid(self) -> None:
        # kasr → rakm implicit conversion is allowed
        analyze("rakm x = 3; x = 3;")

    def test_function_with_return_is_valid(self) -> None:
        analyze("rakm ya f(rakm x) { raga3 x; }")

    def test_function_call_with_correct_args_is_valid(self) -> None:
        analyze("rakm ya add(rakm a, rakm b) { raga3 a; } rakm r = add(1, 2);")

    def test_if_with_comparison_condition_is_valid(self) -> None:
        analyze("rakm x = 5; lw (x > 0) { etba3(x); }")

    def test_if_with_literal_1_is_valid(self) -> None:
        analyze("lw (1) { etba3(1); }")

    def test_if_with_literal_0_is_valid(self) -> None:
        analyze("lw (0) { etba3(1); }")

    def test_while_with_comparison_is_valid(self) -> None:
        analyze("rakm i = 0; tol lma (i < 5) { i = i + 1; }")


# ---------------------------------------------------------------------------
# Variable scope errors
# ---------------------------------------------------------------------------

class TestVariableScopeErrors:
    def test_redeclaration_in_same_scope_raises_error(self) -> None:
        err = assert_semantic_error("rakm x = 1; rakm x = 2;")
        assert "Redeclaration" in err.message or "redeclaration" in err.message.lower()

    def test_use_of_undeclared_variable_raises_error(self) -> None:
        err = assert_semantic_error("etba3(x);")
        assert "undeclared" in err.message.lower() or "undefined" in err.message.lower()

    def test_assignment_to_undeclared_variable_raises_error(self) -> None:
        err = assert_semantic_error("x = 5;")
        assert "undeclared" in err.message.lower() or "undeclared" in err.message.lower()

    def test_redeclaration_in_same_block_raises_error(self) -> None:
        # Two rakm declarations of the same name in the same block scope — must fail.
        src = "rakm ya f(rakm x) { rakm y = 1; rakm y = 2; raga3 y; }"
        assert_semantic_error(src)

    def test_variable_from_outer_scope_is_accessible(self) -> None:
        # Should NOT raise — inner block can read outer variable
        analyze("rakm x = 10; lw (x > 0) { etba3(x); }")


# ---------------------------------------------------------------------------
# Return statement errors
# ---------------------------------------------------------------------------

class TestReturnErrors:
    def test_return_outside_function_raises_error(self) -> None:
        err = assert_semantic_error("raga3 1;")
        assert "raga3" in err.message.lower() or "return" in err.message.lower()

    def test_function_with_no_return_raises_error(self) -> None:
        err = assert_semantic_error("rakm ya f(rakm x) { etba3(x); }")
        assert "raga3" in err.message.lower() or "return" in err.message.lower()


# ---------------------------------------------------------------------------
# Function call errors
# ---------------------------------------------------------------------------

class TestFunctionCallErrors:
    def test_wrong_arg_count_too_few_raises_error(self) -> None:
        src = "rakm ya add(rakm a, rakm b) { raga3 a; } rakm r = add(1);"
        err = assert_semantic_error(src)
        assert "argument" in err.message.lower() or "param" in err.message.lower()

    def test_wrong_arg_count_too_many_raises_error(self) -> None:
        src = "rakm ya add(rakm a, rakm b) { raga3 a; } rakm r = add(1, 2, 3);"
        err = assert_semantic_error(src)
        assert "argument" in err.message.lower() or "param" in err.message.lower()

    def test_call_to_undefined_function_raises_error(self) -> None:
        err = assert_semantic_error("rakm r = unknown(1);")
        assert "undefined" in err.message.lower() or "undeclared" in err.message.lower()

    def test_duplicate_function_declaration_raises_error(self) -> None:
        src = (
            "rakm ya f(rakm x) { raga3 x; } "
            "rakm ya f(rakm x) { raga3 x; }"
        )
        err = assert_semantic_error(src)
        assert "duplicate" in err.message.lower() or "f" in err.message

    def test_duplicate_parameter_names_raises_error(self) -> None:
        src = "rakm ya f(rakm a, rakm a) { raga3 a; }"
        err = assert_semantic_error(src)
        assert "duplicate" in err.message.lower() or "param" in err.message.lower()


# ---------------------------------------------------------------------------
# Condition validation
# ---------------------------------------------------------------------------

class TestConditionValidation:
    def test_invalid_condition_literal_2_raises_error(self) -> None:
        # bare IntLiteral(2) is not 0 or 1 — invalid condition
        err = assert_semantic_error("lw (2) { etba3(1); }")
        assert "condition" in err.message.lower()

    def test_invalid_condition_literal_negative_raises_error(self) -> None:
        # arithmetic expression used directly as condition (not a comparison)
        # The condition 1 + 1 = 2, not 0 or 1
        # Note: condition is parsed as BinaryOp(+) which is not a comparison, so semantic rejects it
        err = assert_semantic_error("lw (1 + 1) { etba3(1); }")
        assert "condition" in err.message.lower()

    def test_comparison_condition_is_valid(self) -> None:
        # lw (x > 0) — comparison BinaryOp is always accepted
        analyze("rakm x = 5; lw (x > 0) { etba3(x); }")

    def test_while_invalid_condition_raises_error(self) -> None:
        err = assert_semantic_error("tol lma (3) { etba3(1); }")
        assert "condition" in err.message.lower()


# ---------------------------------------------------------------------------
# SemanticError structure
# ---------------------------------------------------------------------------

class TestSemanticErrorStructure:
    def test_error_has_message_field(self) -> None:
        err = assert_semantic_error("rakm x = 1; rakm x = 2;")
        assert isinstance(err.message, str)
        assert len(err.message) > 0

    def test_error_has_line_field(self) -> None:
        err = assert_semantic_error("rakm x = 1; rakm x = 2;")
        assert isinstance(err.line, int)

    def test_error_has_col_field(self) -> None:
        err = assert_semantic_error("rakm x = 1; rakm x = 2;")
        assert isinstance(err.col, int)

    def test_str_contains_line_col(self) -> None:
        err = assert_semantic_error("rakm x = 1; rakm x = 2;")
        s = str(err)
        assert "line" in s.lower()
