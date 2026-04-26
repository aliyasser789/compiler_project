from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import TypeAlias


@dataclass(slots=True)
class Node:
    """Base class for all AST nodes."""

    line: int = field(default=0, kw_only=True)
    col: int = field(default=0, kw_only=True)


@dataclass(slots=True)
class Stmt(Node):
    """Base class for all statement nodes."""


@dataclass(slots=True)
class Expr(Node):
    """Base class for all expression nodes."""


class VarType(Enum):
    """Variable types supported by Codawy v0.1."""

    RAKM = "RAKM"
    KASR = "KASR"


@dataclass(slots=True)
class IntLiteral(Expr):
    """Integer literal expression."""

    value: int


@dataclass(slots=True)
class FloatLiteral(Expr):
    """Float literal expression."""

    value: float


@dataclass(slots=True)
class VarRef(Expr):
    """Variable reference expression."""

    name: str


@dataclass(slots=True)
class BinaryOp(Expr):
    """Binary operation expression."""

    op: str
    left: Expr
    right: Expr


@dataclass(slots=True)
class CallExpr(Expr):
    """Function call expression."""

    callee: str
    args: list[Expr]


@dataclass(slots=True)
class Block(Stmt):
    """Block statement containing nested statements."""

    statements: list[Stmt]


@dataclass(slots=True)
class VarDecl(Stmt):
    """Variable declaration statement."""

    var_type: VarType
    name: str
    initializer: Expr


@dataclass(slots=True)
class Assign(Stmt):
    """Variable assignment statement."""

    name: str
    value: Expr


@dataclass(slots=True)
class PrintStmt(Stmt):
    """Print statement for expression output."""

    value: Expr


@dataclass(slots=True)
class ReturnStmt(Stmt):
    """Return statement with optional expression."""

    value: Expr | None


@dataclass(slots=True)
class IfStmt(Stmt):
    """Conditional statement with optional elif and else parts."""

    condition: Expr
    then_block: Block
    elif_parts: list[tuple[Expr, Block]]
    else_block: Block | None


@dataclass(slots=True)
class WhileStmt(Stmt):
    """While loop statement."""

    condition: Expr
    body: Block


@dataclass(slots=True)
class Param(Node):
    """Function parameter declaration."""

    name: str
    var_type: VarType


@dataclass(slots=True)
class FuncDef(Node):
    """Function definition at top level."""

    name: str
    return_type: VarType
    params: list[Param]
    body: Block


TopLevel: TypeAlias = FuncDef | Stmt


@dataclass(slots=True)
class Program(Node):
    """Root program node containing top-level items."""

    items: list[TopLevel]


__all__ = [
    "Node",
    "Stmt",
    "Expr",
    "Program",
    "TopLevel",
    "VarType",
    "IntLiteral",
    "FloatLiteral",
    "VarRef",
    "BinaryOp",
    "CallExpr",
    "Block",
    "VarDecl",
    "Assign",
    "PrintStmt",
    "ReturnStmt",
    "IfStmt",
    "WhileStmt",
    "FuncDef",
    "Param",
]
