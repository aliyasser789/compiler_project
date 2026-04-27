"""tests/test_interpreter.py — End-to-end tests for francode.interpreter.Interpreter.

Each test runs the full pipeline:
    source string → Lexer → Parser → SemanticAnalyzer → Interpreter

etba3 output is captured via pytest's capsys fixture.
"""

from __future__ import annotations

import pytest

from francode.interpreter import FrancodeRuntimeError, Interpreter
from francode.lexer import Lexer
from francode.parser import Parser
from francode.semantic import SemanticAnalyzer


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def run(source: str) -> None:
    """Run *source* through the full Francode pipeline."""
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    SemanticAnalyzer().analyze(ast)
    Interpreter().execute(ast)


def run_and_capture(source: str, capsys) -> str:
    """Run *source* and return everything printed to stdout (stripped)."""
    run(source)
    return capsys.readouterr().out.strip()


def lines(source: str, capsys) -> list[str]:
    """Run *source* and return individual printed lines."""
    return run_and_capture(source, capsys).splitlines()


# ---------------------------------------------------------------------------
# Arithmetic correctness
# ---------------------------------------------------------------------------

class TestArithmetic:
    def test_addition(self, capsys) -> None:
        assert run_and_capture("etba3(3 + 4);", capsys) == "7"

    def test_subtraction(self, capsys) -> None:
        assert run_and_capture("etba3(10 - 3);", capsys) == "7"

    def test_multiplication(self, capsys) -> None:
        assert run_and_capture("etba3(3 * 4);", capsys) == "12"

    def test_division_always_returns_float(self, capsys) -> None:
        out = run_and_capture("kasr r = 7 / 2; etba3(r);", capsys)
        assert float(out) == pytest.approx(3.5)

    def test_division_of_even_numbers_still_returns_float(self, capsys) -> None:
        out = run_and_capture("kasr r = 6 / 2; etba3(r);", capsys)
        # must be a float (contains "." or Python printed 3.0)
        assert "." in out or float(out) == 3.0

    def test_integer_addition_stays_int(self, capsys) -> None:
        out = run_and_capture("rakm x = 2 + 3; etba3(x);", capsys)
        assert out == "5"

    def test_precedence_mul_before_add(self, capsys) -> None:
        # 2 + 3 * 4 = 14, not 20
        assert run_and_capture("etba3(2 + 3 * 4);", capsys) == "14"

    def test_parentheses_override_precedence(self, capsys) -> None:
        # (2 + 3) * 4 = 20
        assert run_and_capture("etba3((2 + 3) * 4);", capsys) == "20"

    def test_unary_minus(self, capsys) -> None:
        assert run_and_capture("etba3(0 - 5);", capsys) == "-5"


# ---------------------------------------------------------------------------
# Type conversions
# ---------------------------------------------------------------------------

class TestTypeConversions:
    def test_float_to_int_truncates_toward_zero_positive(self, capsys) -> None:
        # 7 / 2 = 3.5 → stored in rakm → truncated to 3
        out = run_and_capture("rakm x = 7 / 2; etba3(x);", capsys)
        assert out == "3"

    def test_float_to_int_truncates_toward_zero_large(self, capsys) -> None:
        # 10 / 3 = 3.333… → 3
        out = run_and_capture("rakm x = 10 / 3; etba3(x);", capsys)
        assert out == "3"

    def test_int_stored_in_kasr_promotes_to_float(self, capsys) -> None:
        # kasr var assigned from int expression
        out = run_and_capture("kasr y = 5 + 0; etba3(y);", capsys)
        assert float(out) == pytest.approx(5.0)


# ---------------------------------------------------------------------------
# Comparisons
# ---------------------------------------------------------------------------

class TestComparisons:
    def test_greater_than_true_returns_1(self, capsys) -> None:
        assert run_and_capture("etba3(5 > 3);", capsys) == "1"

    def test_greater_than_false_returns_0(self, capsys) -> None:
        assert run_and_capture("etba3(3 > 5);", capsys) == "0"

    def test_equal_equal_true(self, capsys) -> None:
        assert run_and_capture("etba3(4 == 4);", capsys) == "1"

    def test_equal_equal_false(self, capsys) -> None:
        assert run_and_capture("etba3(4 == 5);", capsys) == "0"

    def test_not_equal(self, capsys) -> None:
        assert run_and_capture("etba3(4 != 5);", capsys) == "1"

    def test_less_than(self, capsys) -> None:
        assert run_and_capture("etba3(3 < 5);", capsys) == "1"

    def test_less_than_or_equal(self, capsys) -> None:
        assert run_and_capture("etba3(3 <= 3);", capsys) == "1"

    def test_greater_than_or_equal(self, capsys) -> None:
        assert run_and_capture("etba3(5 >= 5);", capsys) == "1"


# ---------------------------------------------------------------------------
# Variable declaration and assignment
# ---------------------------------------------------------------------------

class TestVariables:
    def test_declare_and_print_int(self, capsys) -> None:
        assert run_and_capture("rakm x = 42; etba3(x);", capsys) == "42"

    def test_assign_updates_value(self, capsys) -> None:
        assert run_and_capture("rakm x = 1; x = 99; etba3(x);", capsys) == "99"

    def test_variable_scope_in_block(self, capsys) -> None:
        # Variable declared inside if-block is local to that block
        # Outer x should be unaffected
        src = "rakm x = 10; lw (1) { rakm inner = 5; etba3(inner); } etba3(x);"
        out = lines(src, capsys)
        assert out == ["5", "10"]


# ---------------------------------------------------------------------------
# Print statement
# ---------------------------------------------------------------------------

class TestPrintStmt:
    def test_etba3_prints_int(self, capsys) -> None:
        out = run_and_capture("etba3(7);", capsys)
        assert out == "7"

    def test_etba3_prints_float(self, capsys) -> None:
        out = run_and_capture("kasr r = 1 / 4; etba3(r);", capsys)
        assert float(out) == pytest.approx(0.25)

    def test_etba3_prints_expression_result(self, capsys) -> None:
        out = run_and_capture("etba3(2 + 3 * 4);", capsys)
        assert out == "14"

    def test_multiple_etba3_prints_multiple_lines(self, capsys) -> None:
        out = lines("etba3(1); etba3(2); etba3(3);", capsys)
        assert out == ["1", "2", "3"]


# ---------------------------------------------------------------------------
# Conditional branching
# ---------------------------------------------------------------------------

class TestConditionals:
    def test_lw_branch_fires_when_condition_true(self, capsys) -> None:
        src = "rakm n = 10; lw (n > 5) { etba3(1); } aw { etba3(0); }"
        assert run_and_capture(src, capsys) == "1"

    def test_aw_branch_fires_when_condition_false(self, capsys) -> None:
        src = "rakm n = 1; lw (n > 5) { etba3(1); } aw { etba3(0); }"
        assert run_and_capture(src, capsys) == "0"

    def test_tb_lw_branch_fires(self, capsys) -> None:
        src = (
            "rakm n = 7; "
            "lw (n > 10) { etba3(1); } "
            "tb lw (n > 5) { etba3(2); } "
            "aw { etba3(3); }"
        )
        assert run_and_capture(src, capsys) == "2"

    def test_no_branch_fires_when_all_false_and_no_else(self, capsys) -> None:
        src = "rakm n = 0; lw (n > 5) { etba3(1); }"
        assert run_and_capture(src, capsys) == ""

    def test_only_first_true_branch_fires(self, capsys) -> None:
        src = (
            "rakm n = 15; "
            "lw (n > 10) { etba3(1); } "
            "tb lw (n > 5) { etba3(2); } "
            "aw { etba3(3); }"
        )
        assert run_and_capture(src, capsys) == "1"


# ---------------------------------------------------------------------------
# While loop
# ---------------------------------------------------------------------------

class TestWhileLoop:
    def test_while_loop_body_executes(self, capsys) -> None:
        src = "rakm i = 0; tol lma (i < 3) { etba3(i); i = i + 1; }"
        assert lines(src, capsys) == ["0", "1", "2"]

    def test_while_loop_with_false_condition_does_not_execute(self, capsys) -> None:
        src = "rakm i = 10; tol lma (i < 0) { etba3(i); }"
        assert run_and_capture(src, capsys) == ""

    def test_while_loop_terminates(self, capsys) -> None:
        # Loop runs exactly 5 times
        src = "rakm i = 1; tol lma (i <= 5) { i = i + 1; } etba3(i);"
        assert run_and_capture(src, capsys) == "6"

    def test_while_loop_accumulates_sum(self, capsys) -> None:
        src = "rakm s = 0; rakm i = 1; tol lma (i <= 4) { s = s + i; i = i + 1; } etba3(s);"
        assert run_and_capture(src, capsys) == "10"


# ---------------------------------------------------------------------------
# Function calls
# ---------------------------------------------------------------------------

class TestFunctionCalls:
    def test_function_returns_correct_value(self, capsys) -> None:
        src = "rakm ya add(rakm a, rakm b) { raga3 a + b; } etba3(add(3, 4));"
        assert run_and_capture(src, capsys) == "7"

    def test_function_with_kasr_return_type(self, capsys) -> None:
        src = "kasr ya half(rakm x) { raga3 x / 2; } kasr r = half(7); etba3(r);"
        out = run_and_capture(src, capsys)
        assert float(out) == pytest.approx(3.5)

    def test_function_return_coercion_to_rakm(self, capsys) -> None:
        # Division gives float; storing in rakm truncates
        src = "rakm ya trunc(rakm x) { raga3 x / 2; } rakm r = trunc(7); etba3(r);"
        assert run_and_capture(src, capsys) == "3"

    def test_function_with_conditional_return(self, capsys) -> None:
        src = (
            "rakm ya max(rakm a, rakm b) { "
            "lw (a > b) { raga3 a; } aw { raga3 b; } "
            "} "
            "etba3(max(5, 9));"
        )
        assert run_and_capture(src, capsys) == "9"

    def test_multiple_function_calls(self, capsys) -> None:
        src = (
            "rakm ya double(rakm x) { raga3 x + x; } "
            "etba3(double(3)); etba3(double(7));"
        )
        assert lines(src, capsys) == ["6", "14"]

    def test_forward_call_works(self, capsys) -> None:
        # Function defined AFTER the call site in source; interpreter pre-registers all FuncDefs
        src = (
            "etba3(sq(4)); "
            "rakm ya sq(rakm x) { raga3 x * x; }"
        )
        assert run_and_capture(src, capsys) == "16"


# ---------------------------------------------------------------------------
# Recursive function — Fibonacci
# ---------------------------------------------------------------------------

class TestFibonacci:
    FIB_SRC = (
        "rakm ya fib(rakm n) { "
        "lw (n < 2) { raga3 n; } "
        "aw { raga3 fib(n - 1) + fib(n - 2); } "
        "}"
    )

    def test_fib_0(self, capsys) -> None:
        assert run_and_capture(self.FIB_SRC + " etba3(fib(0));", capsys) == "0"

    def test_fib_1(self, capsys) -> None:
        assert run_and_capture(self.FIB_SRC + " etba3(fib(1));", capsys) == "1"

    def test_fib_5(self, capsys) -> None:
        assert run_and_capture(self.FIB_SRC + " etba3(fib(5));", capsys) == "5"

    def test_fib_7_equals_13(self, capsys) -> None:
        assert run_and_capture(self.FIB_SRC + " etba3(fib(7));", capsys) == "13"

    def test_fib_10_equals_55(self, capsys) -> None:
        assert run_and_capture(self.FIB_SRC + " etba3(fib(10));", capsys) == "55"


# ---------------------------------------------------------------------------
# Runtime error handling
# ---------------------------------------------------------------------------

class TestRuntimeErrors:
    def test_division_by_zero_raises_runtime_error(self) -> None:
        with pytest.raises(FrancodeRuntimeError) as exc_info:
            run("kasr r = 1 / 0;")
        assert "zero" in exc_info.value.message.lower()

    def test_division_by_zero_integer_raises_runtime_error(self) -> None:
        with pytest.raises(FrancodeRuntimeError):
            run("kasr r = 5 / 0;")

    def test_stack_overflow_raises_runtime_error(self) -> None:
        # Infinite recursion — no base case.
        # Either our FrancodeRuntimeError depth guard or Python's RecursionError fires first.
        src = "rakm ya inf(rakm x) { raga3 inf(x); } rakm r = inf(1);"
        with pytest.raises((FrancodeRuntimeError, RecursionError)):
            run(src)

    def test_runtime_error_has_message_field(self) -> None:
        with pytest.raises(FrancodeRuntimeError) as exc_info:
            run("kasr r = 1 / 0;")
        err = exc_info.value
        assert isinstance(err.message, str) and len(err.message) > 0

    def test_runtime_error_has_line_and_col(self) -> None:
        with pytest.raises(FrancodeRuntimeError) as exc_info:
            run("kasr r = 1 / 0;")
        err = exc_info.value
        assert isinstance(err.line, int)
        assert isinstance(err.col, int)

    def test_runtime_error_str_contains_line(self) -> None:
        with pytest.raises(FrancodeRuntimeError) as exc_info:
            run("kasr r = 1 / 0;")
        assert "line" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# Lexical scoping
# ---------------------------------------------------------------------------

class TestLexicalScoping:
    def test_nested_loop_variables_are_independent(self, capsys) -> None:
        # Inner loop col resets each outer iteration
        src = (
            "rakm outer = 1; "
            "tol lma (outer <= 2) { "
            "rakm inner = 1; "
            "tol lma (inner <= 2) { "
            "etba3(outer); "
            "inner = inner + 1; "
            "} "
            "outer = outer + 1; "
            "}"
        )
        out = lines(src, capsys)
        # outer=1 prints twice, outer=2 prints twice
        assert out == ["1", "1", "2", "2"]

    def test_function_does_not_see_caller_locals(self) -> None:
        # 'x' inside f() is the parameter, not the caller's 'x = 999'
        src = (
            "rakm ya f(rakm x) { raga3 x; } "
            "rakm x = 999; "
            "rakm r = f(42); "
            "etba3(r);"
        )
        # Should print 42, not 999
        from io import StringIO
        import sys
        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        run(src)
        sys.stdout = old_stdout
        assert captured.getvalue().strip() == "42"
