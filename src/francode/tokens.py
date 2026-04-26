from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    # Keywords
    RAKM = auto()
    KASR = auto()
    YA = auto()
    LW = auto()
    AW = auto()
    TB = auto()
    TOL = auto()
    LMA = auto()
    RAGA3 = auto()
    ETBA3 = auto()

    # Identifiers and literals
    IDENT = auto()
    INT = auto()
    FLOAT = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    EQUAL = auto()
    EQEQ = auto()
    NOTEQ = auto()
    LT = auto()
    GT = auto()
    LTE = auto()
    GTE = auto()

    # Punctuation
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    COMMA = auto()
    SEMICOLON = auto()
    EOF = auto()


@dataclass(slots=True)
class Token:
    type: TokenType
    value: str | int | float | None
    line: int
    col: int


class LexerError(Exception):
    pass
