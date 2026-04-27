from __future__ import annotations

import sys

from francode.tokens import LexerError
from francode.lexer import Lexer
from francode.parser import Parser, ParserError
from francode.semantic import SemanticAnalyzer, SemanticError
from francode.interpreter import Interpreter, FrancodeRuntimeError


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: francode <file.fc>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]

    try:
        source = open(path, encoding="utf-8").read()
    except OSError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
        SemanticAnalyzer().analyze(ast)
        Interpreter().execute(ast)
    except (LexerError, ParserError, SemanticError, FrancodeRuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()


__all__ = ["main"]
