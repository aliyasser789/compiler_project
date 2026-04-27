"""tests/test_lexer.py — Unit tests for francode.lexer.Lexer."""

from __future__ import annotations

import pytest

from francode.lexer import Lexer
from francode.tokens import LexerError, Token, TokenType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def tokenize(source: str) -> list[Token]:
    """Run the lexer and return all tokens (including EOF)."""
    return Lexer(source).tokenize()


def types(source: str) -> list[TokenType]:
    """Return only the token types produced by the lexer."""
    return [t.type for t in tokenize(source)]


# ---------------------------------------------------------------------------
# Keywords
# ---------------------------------------------------------------------------

class TestKeywords:
    def test_rakm_keyword(self) -> None:
        assert types("rakm")[0] == TokenType.RAKM

    def test_kasr_keyword(self) -> None:
        assert types("kasr")[0] == TokenType.KASR

    def test_ya_keyword(self) -> None:
        assert types("ya")[0] == TokenType.YA

    def test_lw_keyword(self) -> None:
        assert types("lw")[0] == TokenType.LW

    def test_aw_keyword(self) -> None:
        assert types("aw")[0] == TokenType.AW

    def test_tb_keyword(self) -> None:
        assert types("tb")[0] == TokenType.TB

    def test_tol_keyword(self) -> None:
        assert types("tol")[0] == TokenType.TOL

    def test_lma_keyword(self) -> None:
        assert types("lma")[0] == TokenType.LMA

    def test_raga3_keyword(self) -> None:
        assert types("raga3")[0] == TokenType.RAGA3

    def test_etba3_keyword(self) -> None:
        assert types("etba3")[0] == TokenType.ETBA3

    def test_all_10_keywords_present(self) -> None:
        keyword_source = "rakm kasr ya lw aw tb tol lma raga3 etba3"
        toks = tokenize(keyword_source)
        # 10 keywords + EOF
        assert len(toks) == 11

    def test_identifier_not_confused_with_keyword(self) -> None:
        # "rakmx" is an identifier, not the keyword "rakm"
        tok = tokenize("rakmx")[0]
        assert tok.type == TokenType.IDENT
        assert tok.value == "rakmx"


# ---------------------------------------------------------------------------
# Literals
# ---------------------------------------------------------------------------

class TestLiterals:
    def test_integer_literal_type(self) -> None:
        tok = tokenize("42")[0]
        assert tok.type == TokenType.INT

    def test_integer_literal_value(self) -> None:
        tok = tokenize("42")[0]
        assert tok.value == 42

    def test_integer_zero(self) -> None:
        tok = tokenize("0")[0]
        assert tok.type == TokenType.INT
        assert tok.value == 0

    def test_float_literal_type(self) -> None:
        tok = tokenize("3.14")[0]
        assert tok.type == TokenType.FLOAT

    def test_float_literal_value(self) -> None:
        tok = tokenize("3.14")[0]
        assert tok.value == pytest.approx(3.14)

    def test_float_with_leading_zero(self) -> None:
        tok = tokenize("0.5")[0]
        assert tok.type == TokenType.FLOAT
        assert tok.value == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# Operators — single character
# ---------------------------------------------------------------------------

class TestSingleCharOperators:
    @pytest.mark.parametrize("src,expected", [
        ("+", TokenType.PLUS),
        ("-", TokenType.MINUS),
        ("*", TokenType.STAR),
        ("/", TokenType.SLASH),
        ("=", TokenType.EQUAL),
        ("<", TokenType.LT),
        (">", TokenType.GT),
    ])
    def test_single_char_operator(self, src: str, expected: TokenType) -> None:
        assert types(src)[0] == expected


# ---------------------------------------------------------------------------
# Operators — two character
# ---------------------------------------------------------------------------

class TestTwoCharOperators:
    def test_eqeq(self) -> None:
        assert types("==")[0] == TokenType.EQEQ

    def test_noteq(self) -> None:
        assert types("!=")[0] == TokenType.NOTEQ

    def test_lte(self) -> None:
        assert types("<=")[0] == TokenType.LTE

    def test_gte(self) -> None:
        assert types(">=")[0] == TokenType.GTE

    def test_eqeq_not_confused_with_two_equals(self) -> None:
        # "==" should produce EQEQ not EQUAL EQUAL
        toks = tokenize("==")
        assert toks[0].type == TokenType.EQEQ
        assert toks[1].type == TokenType.EOF

    def test_lte_not_confused_with_lt_equal(self) -> None:
        # "<=" is one token, not LT then EQUAL
        toks = tokenize("<=")
        assert toks[0].type == TokenType.LTE
        assert toks[1].type == TokenType.EOF


# ---------------------------------------------------------------------------
# Punctuation
# ---------------------------------------------------------------------------

class TestPunctuation:
    @pytest.mark.parametrize("src,expected", [
        ("(", TokenType.LPAREN),
        (")", TokenType.RPAREN),
        ("{", TokenType.LBRACE),
        ("}", TokenType.RBRACE),
        (",", TokenType.COMMA),
        (";", TokenType.SEMICOLON),
    ])
    def test_punctuation(self, src: str, expected: TokenType) -> None:
        assert types(src)[0] == expected


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

class TestComments:
    def test_single_line_comment_is_skipped(self) -> None:
        # Only an integer should remain; the comment is consumed
        toks = tokenize("42 // this is a comment\n")
        assert toks[0].type == TokenType.INT
        assert toks[1].type == TokenType.EOF

    def test_single_line_comment_only_produces_eof(self) -> None:
        toks = tokenize("// only a comment")
        assert toks == [Token(TokenType.EOF, None, 1, 18)]

    def test_multi_line_comment_is_skipped(self) -> None:
        toks = tokenize("/* block */ 99")
        assert toks[0].type == TokenType.INT
        assert toks[0].value == 99

    def test_multi_line_comment_spanning_lines_is_skipped(self) -> None:
        src = "1 /* start\n   middle\n   end */ 2"
        toks = tokenize(src)
        assert toks[0].value == 1
        assert toks[1].value == 2

    def test_unterminated_block_comment_raises_lexer_error(self) -> None:
        with pytest.raises(LexerError):
            tokenize("/* not closed")

    def test_unterminated_block_comment_message(self) -> None:
        with pytest.raises(LexerError, match="Unterminated"):
            tokenize("/* oops")


# ---------------------------------------------------------------------------
# Unknown characters
# ---------------------------------------------------------------------------

class TestUnknownCharacters:
    def test_unknown_char_raises_lexer_error(self) -> None:
        with pytest.raises(LexerError):
            tokenize("@")

    def test_unknown_char_hash_raises_lexer_error(self) -> None:
        with pytest.raises(LexerError):
            tokenize("#")

    def test_unknown_char_message_contains_char(self) -> None:
        with pytest.raises(LexerError, match="@"):
            tokenize("@")


# ---------------------------------------------------------------------------
# Line and column tracking
# ---------------------------------------------------------------------------

class TestLocationTracking:
    def test_first_token_starts_at_line1_col1(self) -> None:
        tok = tokenize("rakm")[0]
        assert tok.line == 1
        assert tok.col == 1

    def test_col_advances_correctly(self) -> None:
        # "rakm " is 5 chars; "x" starts at col 6
        toks = tokenize("rakm x")
        ident_tok = toks[1]
        assert ident_tok.type == TokenType.IDENT
        assert ident_tok.col == 6

    def test_newline_resets_col_and_increments_line(self) -> None:
        toks = tokenize("rakm\nx")
        ident_tok = toks[1]
        assert ident_tok.line == 2
        assert ident_tok.col == 1

    def test_multiline_col_tracking(self) -> None:
        src = "rakm\nkasr y"
        toks = tokenize(src)
        # toks: RAKM(1,1) KASR(2,1) IDENT(2,6) EOF
        assert toks[1].line == 2
        assert toks[1].col == 1
        assert toks[2].line == 2
        assert toks[2].col == 6

    def test_eof_is_last_token(self) -> None:
        toks = tokenize("42")
        assert toks[-1].type == TokenType.EOF
