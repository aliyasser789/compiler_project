from __future__ import annotations

import io
from contextlib import redirect_stdout
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from francode.tokens import LexerError
from francode.lexer import Lexer
from francode.parser import Parser, ParserError
from francode.semantic import SemanticAnalyzer, SemanticError
from francode.interpreter import Interpreter, FrancodeRuntimeError

app = FastAPI(title="Francode Playground API")

# Allow all origins so the frontend can be opened as a local file (file://)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve examples/ relative to the project root (two levels above this file)
_EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class RunRequest(BaseModel):
    source: str


class RunResponse(BaseModel):
    success: bool
    output: str
    error: str | None = None
    line: int | None = None
    col: int | None = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/examples")
def list_examples() -> dict[str, str]:
    """Return every .fc file in examples/ as a name → source mapping."""
    return {
        path.stem: path.read_text(encoding="utf-8")
        for path in sorted(_EXAMPLES_DIR.glob("*.fc"))
    }


@app.post("/run", response_model=RunResponse)
def run_code(req: RunRequest) -> RunResponse:
    """Run Francode source through the full pipeline and return output or error."""
    buf = io.StringIO()
    try:
        # Redirect stdout so print() calls inside the interpreter are captured
        with redirect_stdout(buf):
            tokens = Lexer(req.source).tokenize()
            ast    = Parser(tokens).parse()
            SemanticAnalyzer().analyze(ast)
            Interpreter().execute(ast)
        return RunResponse(success=True, output=buf.getvalue())

    except LexerError as exc:
        # LexerError is a plain exception; line/col are embedded in its message
        return RunResponse(success=False, output=buf.getvalue(), error=str(exc))

    except (ParserError, SemanticError, FrancodeRuntimeError) as exc:
        # These dataclass-based errors carry structured line/col fields
        return RunResponse(
            success=False,
            output=buf.getvalue(),
            error=exc.message,
            line=exc.line,
            col=exc.col,
        )
