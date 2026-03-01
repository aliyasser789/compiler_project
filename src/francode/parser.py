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
    Param,
    PrintStmt,
    Program,
    ReturnStmt,
    Stmt,
    TopLevel,
    VarDecl,
    VarRef,
    VarType,
    WhileStmt,
)
from francode.tokens import Token, TokenType


@dataclass(slots=True)
class ParserError(Exception):
    """Error raised when the parser encounters invalid token structure."""

    message: str
    line: int
    col: int

    def __str__(self) -> str:
        """Return a human-readable parser error message."""
        return f"ParserError at line {self.line} col {self.col}: {self.message}"


class Parser:
    """Token parser scaffold for francode v0.1."""

    def __init__(self, tokens: list[Token]) -> None:
        """Initialize parser state and ensure an EOF token is present."""
        self.tokens = list(tokens)
        self.current = 0

        if self.tokens:
            last = self.tokens[-1]
            if last.type != TokenType.EOF:
                self.tokens.append(Token(TokenType.EOF, None, line=last.line, col=last.col))
        else:
            self.tokens.append(Token(TokenType.EOF, None, line=1, col=1))

    def peek(self) -> Token:
        """Return the current token without consuming it."""
        return self.tokens[self.current]

    def previous(self) -> Token:
        """Return the previously consumed token."""
        return self.tokens[self.current - 1]

    def is_at_end(self) -> bool:
        """Return True when the parser is positioned at EOF."""
        return self.peek().type == TokenType.EOF

    def advance(self) -> Token:
        """Consume and return the current token."""
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def check(self, ttype: TokenType) -> bool:
        """Return True if the current token matches the requested type."""
        if self.is_at_end():
            return False
        return self.peek().type == ttype

    def match(self, *types: TokenType) -> bool:
        """Consume the current token if it matches any provided type."""
        for ttype in types:
            if self.check(ttype):
                self.advance()
                return True
        return False

    def expect(self, ttype: TokenType, message: str) -> Token:
        """Consume and return a token of the expected type or raise ParserError."""
        if self.check(ttype):
            return self.advance()

        token = self.peek()
        full_message = (
            f"{message} (expected {ttype.name}, got {token.type.name})"
        )
        raise ParserError(full_message, token.line, token.col)

    def error(self, token: Token, message: str) -> None:
        """Raise a ParserError anchored to a specific token location."""
        raise ParserError(message, token.line, token.col)

    def parse(self) -> Program:
        """Parse tokens into a program AST."""
        items: list[TopLevel] = []
        while not self.is_at_end():
            items.append(self.parse_top_level())
        return Program(items=items)

    def parse_top_level(self) -> TopLevel:
        """Parse a top-level declaration or statement."""
        if self.check(TokenType.YA):
            return self.parse_function_def()
        return self.parse_statement()

    def parse_function_def(self) -> FuncDef:
        """Parse a function definition."""
        self.expect(TokenType.YA, "Expected 'ya' to start function definition")
        name_tok = self.expect(TokenType.IDENT, "Expected function name")
        self.expect(TokenType.LPAREN, "Expected '(' after function name")

        params: list[Param] = []
        if not self.check(TokenType.RPAREN):
            params.append(self.parse_param())
            while self.match(TokenType.COMMA):
                params.append(self.parse_param())

        self.expect(TokenType.RPAREN, "Expected ')' after function parameters")
        body = self.parse_block()
        return FuncDef(name=str(name_tok.value), params=params, body=body)

    def parse_param(self) -> Param:
        """Parse a typed function parameter."""
        if self.match(TokenType.RAKM):
            var_type = VarType.RAKM
        elif self.match(TokenType.KASR):
            var_type = VarType.KASR
        else:
            self.error(self.peek(), "Expected parameter type 'rakm' or 'kasr'")
            raise AssertionError("Unreachable")

        ident_tok = self.expect(TokenType.IDENT, "Expected parameter name")
        return Param(name=str(ident_tok.value), var_type=var_type)

    def parse_block(self) -> Block:
        """Parse a block statement."""
        self.expect(TokenType.LBRACE, "Expected '{' to start block")
        statements: list[Stmt] = []
        while not self.check(TokenType.RBRACE):
            if self.is_at_end():
                self.error(self.peek(), "Unterminated block; expected '}'")
            statements.append(self.parse_statement())
        self.expect(TokenType.RBRACE, "Expected '}' to end block")
        return Block(statements=statements)

    def parse_statement(self) -> Stmt:
        """Parse a statement."""
        if self.check(TokenType.RAKM) or self.check(TokenType.KASR):
            return self.parse_var_decl()
        if self.check(TokenType.IDENT):
            return self.parse_assignment()
        if self.check(TokenType.ETBA3):
            return self.parse_print_stmt()
        if self.check(TokenType.RAGA3):
            return self.parse_return_stmt()
        if self.check(TokenType.LW):
            return self.parse_if_stmt()
        if self.check(TokenType.TOL):
            return self.parse_while_stmt()
        if self.check(TokenType.LBRACE):
            return self.parse_block()

        self.error(self.peek(), "Unexpected token at start of statement")
        raise AssertionError("Unreachable")

    def parse_var_decl(self) -> VarDecl:
        """Parse a variable declaration statement."""
        if self.match(TokenType.RAKM):
            var_type = VarType.RAKM
        elif self.match(TokenType.KASR):
            var_type = VarType.KASR
        else:
            self.error(self.peek(), "Expected variable type 'rakm' or 'kasr'")
            raise AssertionError("Unreachable")

        name_tok = self.expect(TokenType.IDENT, "Expected variable name")
        self.expect(TokenType.EQUAL, "Expected '=' after variable name")
        initializer = self.parse_expression()
        self.expect(TokenType.SEMICOLON, "Expected ';' after variable declaration")
        return VarDecl(var_type=var_type, name=str(name_tok.value), initializer=initializer)

    def parse_assignment(self) -> Assign:
        """Parse an assignment statement."""
        name_tok = self.expect(TokenType.IDENT, "Expected variable name")
        self.expect(TokenType.EQUAL, "Expected '=' in assignment")
        value = self.parse_expression()
        self.expect(TokenType.SEMICOLON, "Expected ';' after assignment")
        return Assign(name=str(name_tok.value), value=value)

    def parse_print_stmt(self) -> PrintStmt:
        """Parse a print statement."""
        self.expect(TokenType.ETBA3, "Expected 'etba3' to start print statement")
        self.expect(TokenType.LPAREN, "Expected '(' after 'etba3'")
        value = self.parse_expression()
        self.expect(TokenType.RPAREN, "Expected ')' after print expression")
        self.expect(TokenType.SEMICOLON, "Expected ';' after print statement")
        return PrintStmt(value=value)

    def parse_return_stmt(self) -> ReturnStmt:
        """Parse a return statement."""
        self.expect(TokenType.RAGA3, "Expected 'raga3' to start return statement")
        value: Expr | None = None
        if not self.check(TokenType.SEMICOLON):
            value = self.parse_expression()
        self.expect(TokenType.SEMICOLON, "Expected ';' after return statement")
        return ReturnStmt(value=value)

    def parse_if_stmt(self) -> IfStmt:
        """Parse an if statement with optional elif and else branches."""
        self.expect(TokenType.LW, "Expected 'lw' to start if statement")
        self.expect(TokenType.LPAREN, "Expected '(' after 'lw'")
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN, "Expected ')' after if condition")
        then_block = self.parse_block()

        elif_parts: list[tuple[Expr, Block]] = []
        while self.match(TokenType.TB):
            self.expect(TokenType.LW, "Expected 'lw' after 'tb' in elif clause")
            self.expect(TokenType.LPAREN, "Expected '(' after 'tb lw'")
            elif_condition = self.parse_expression()
            self.expect(TokenType.RPAREN, "Expected ')' after elif condition")
            elif_block = self.parse_block()
            elif_parts.append((elif_condition, elif_block))

        else_block: Block | None = None
        if self.match(TokenType.AW):
            else_block = self.parse_block()

        return IfStmt(
            condition=condition,
            then_block=then_block,
            elif_parts=elif_parts,
            else_block=else_block,
        )

    def parse_while_stmt(self) -> WhileStmt:
        """Parse a while statement."""
        self.expect(TokenType.TOL, "Expected 'tol' to start while statement")
        self.expect(TokenType.LMA, "Expected 'lma' after 'tol'")
        self.expect(TokenType.LPAREN, "Expected '(' after 'tol lma'")
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN, "Expected ')' after while condition")
        body = self.parse_block()
        return WhileStmt(condition=condition, body=body)

    def parse_expression(self) -> Expr:
        """Parse an expression."""
        return self.parse_comparison()

    def parse_comparison(self) -> Expr:
        """Parse comparison expressions."""
        left = self.parse_term()
        while self.match(
            TokenType.EQEQ,
            TokenType.NOTEQ,
            TokenType.LT,
            TokenType.GT,
            TokenType.LTE,
            TokenType.GTE,
        ):
            op_tok = self.previous()
            right = self.parse_term()
            left = BinaryOp(op=self._token_to_operator(op_tok.type), left=left, right=right)
        return left

    def parse_term(self) -> Expr:
        """Parse additive expressions."""
        left = self.parse_factor()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op_tok = self.previous()
            right = self.parse_factor()
            left = BinaryOp(op=self._token_to_operator(op_tok.type), left=left, right=right)
        return left

    def parse_factor(self) -> Expr:
        """Parse multiplicative expressions."""
        left = self.parse_unary()
        while self.match(TokenType.STAR, TokenType.SLASH):
            op_tok = self.previous()
            right = self.parse_unary()
            left = BinaryOp(op=self._token_to_operator(op_tok.type), left=left, right=right)
        return left

    def parse_unary(self) -> Expr:
        """Parse unary expressions."""
        if self.match(TokenType.MINUS):
            right = self.parse_unary()
            return BinaryOp(op="-", left=IntLiteral(0), right=right)
        return self.parse_call_or_primary()

    def parse_call_or_primary(self) -> Expr:
        """Parse call expressions and primary expressions."""
        expr = self.parse_primary()
        if isinstance(expr, VarRef) and self.match(TokenType.LPAREN):
            args: list[Expr] = []
            if not self.check(TokenType.RPAREN):
                args.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    args.append(self.parse_expression())
            self.expect(TokenType.RPAREN, "Expected ')' after arguments")
            return CallExpr(callee=expr.name, args=args)
        return expr

    def parse_primary(self) -> Expr:
        """Parse primary expressions."""
        if self.match(TokenType.INT):
            return IntLiteral(value=int(self.previous().value))
        if self.match(TokenType.FLOAT):
            return FloatLiteral(value=float(self.previous().value))
        if self.match(TokenType.IDENT):
            return VarRef(name=str(self.previous().value))
        if self.match(TokenType.LPAREN):
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN, "Expected ')' after expression")
            return expr
        self.error(self.peek(), "Expected expression")
        raise AssertionError("Unreachable")

    def _token_to_operator(self, token_type: TokenType) -> str:
        """Map token type to AST operator string."""
        operator_map = {
            TokenType.PLUS: "+",
            TokenType.MINUS: "-",
            TokenType.STAR: "*",
            TokenType.SLASH: "/",
            TokenType.EQEQ: "==",
            TokenType.NOTEQ: "!=",
            TokenType.LT: "<",
            TokenType.GT: ">",
            TokenType.LTE: "<=",
            TokenType.GTE: ">=",
        }
        if token_type not in operator_map:
            raise ValueError(f"Unsupported operator token: {token_type.name}")
        return operator_map[token_type]


__all__ = ["Parser", "ParserError"]

