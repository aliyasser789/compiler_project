from __future__ import annotations

from francode.tokens import LexerError, Token, TokenType


KEYWORDS: dict[str, TokenType] = {
    "rakm": TokenType.RAKM,
    "kasr": TokenType.KASR,
    "ya": TokenType.YA,
    "lw": TokenType.LW,
    "aw": TokenType.AW,
    "tb": TokenType.TB,
    "tol": TokenType.TOL,
    "lma": TokenType.LMA,
    "raga3": TokenType.RAGA3,
    "etba3": TokenType.ETBA3,
}


class Lexer:
    def __init__(self, source: str) -> None:
        self.source = source
        self.index = 0
        self.line = 1
        self.col = 1

    def peek(self, offset: int = 0) -> str | None:
        pos = self.index + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]

    def advance(self) -> str | None:
        ch = self.peek()
        if ch is None:
            return None

        self.index += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def match(self, expected_char: str) -> bool:
        if self.peek() == expected_char:
            self.advance()
            return True
        return False

    def skip_whitespace_and_comments(self) -> None:
        while True:
            ch = self.peek()
            if ch is None:
                return

            if ch in {" ", "\t", "\n", "\r"}:
                self.advance()
                continue

            if ch == "/" and self.peek(1) == "/":
                self.advance()
                self.advance()
                while self.peek() not in {None, "\n"}:
                    self.advance()
                continue

            if ch == "/" and self.peek(1) == "*":
                start_line = self.line
                start_col = self.col
                self.advance()
                self.advance()

                while True:
                    current = self.peek()
                    if current is None:
                        raise LexerError(
                            f"Unterminated multi-line comment at line {start_line} col {start_col}"
                        )
                    if current == "*" and self.peek(1) == "/":
                        self.advance()
                        self.advance()
                        break
                    self.advance()
                continue

            return

    def read_number(self) -> Token:
        start_line = self.line
        start_col = self.col
        digits: list[str] = []

        while (ch := self.peek()) is not None and ch.isdigit():
            digits.append(self.advance() or "")

        if self.peek() == ".":
            next_ch = self.peek(1)
            if next_ch is not None and next_ch.isdigit():
                digits.append(self.advance() or "")
                while (ch := self.peek()) is not None and ch.isdigit():
                    digits.append(self.advance() or "")
                return Token(
                    type=TokenType.FLOAT,
                    value=float("".join(digits)),
                    line=start_line,
                    col=start_col,
                )
            raise LexerError(
                f"Unexpected character '.' at line {self.line} col {self.col}"
            )

        return Token(
            type=TokenType.INT,
            value=int("".join(digits)),
            line=start_line,
            col=start_col,
        )

    def read_identifier_or_keyword(self) -> Token:
        start_line = self.line
        start_col = self.col
        chars: list[str] = []

        while (ch := self.peek()) is not None and (ch.isalnum() or ch == "_"):
            chars.append(self.advance() or "")

        lexeme = "".join(chars)
        keyword_type = KEYWORDS.get(lexeme)
        if keyword_type is not None:
            return Token(type=keyword_type, value=None, line=start_line, col=start_col)

        return Token(type=TokenType.IDENT, value=lexeme, line=start_line, col=start_col)

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []

        while True:
            self.skip_whitespace_and_comments()
            ch = self.peek()

            if ch is None:
                tokens.append(Token(type=TokenType.EOF, value=None, line=self.line, col=self.col))
                break

            start_line = self.line
            start_col = self.col

            if ch.isdigit():
                tokens.append(self.read_number())
                continue

            if ch.isalpha() or ch == "_":
                tokens.append(self.read_identifier_or_keyword())
                continue

            # Two-character operators first
            if ch == "=" and self.peek(1) == "=":
                self.advance()
                self.advance()
                tokens.append(Token(TokenType.EQEQ, None, start_line, start_col))
                continue
            if ch == "!" and self.peek(1) == "=":
                self.advance()
                self.advance()
                tokens.append(Token(TokenType.NOTEQ, None, start_line, start_col))
                continue
            if ch == "<" and self.peek(1) == "=":
                self.advance()
                self.advance()
                tokens.append(Token(TokenType.LTE, None, start_line, start_col))
                continue
            if ch == ">" and self.peek(1) == "=":
                self.advance()
                self.advance()
                tokens.append(Token(TokenType.GTE, None, start_line, start_col))
                continue

            # Single-character operators and punctuation
            single_char_map: dict[str, TokenType] = {
                "+": TokenType.PLUS,
                "-": TokenType.MINUS,
                "*": TokenType.STAR,
                "/": TokenType.SLASH,
                "=": TokenType.EQUAL,
                "<": TokenType.LT,
                ">": TokenType.GT,
                "(": TokenType.LPAREN,
                ")": TokenType.RPAREN,
                "{": TokenType.LBRACE,
                "}": TokenType.RBRACE,
                ",": TokenType.COMMA,
                ";": TokenType.SEMICOLON,
            }
            token_type = single_char_map.get(ch)
            if token_type is not None:
                self.advance()
                tokens.append(Token(token_type, None, start_line, start_col))
                continue

            raise LexerError(f"Unexpected character '{ch}' at line {start_line} col {start_col}")

        return tokens


if __name__ == "__main__":
    source_code = """ya add(rakm a, rakm b) {
  rakm x = 10 + 2;
  kasr y = 5 / 2;
  // comment here
  /* multi
     line */
  lw (x >= 10) { etba3(x); }
  aw { raga3 x; }
}"""

    lexer = Lexer(source_code)
    for token in lexer.tokenize():
        if token.value is None:
            print(f"{token.type.name} at {token.line}:{token.col}")
        else:
            print(f"{token.type.name}({token.value}) at {token.line}:{token.col}")
