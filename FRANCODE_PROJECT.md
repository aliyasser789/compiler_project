# Francode — Project Context

## What is this project?

Francode is a custom programming language and compiler built from scratch in Python.

The language is designed as an **educational language for Egyptian beginners and children**, using simplified Franco-Arabic keywords (Arabic written in Latin letters) to make programming concepts more approachable. For example: `rakm` means integer, `kasr` means float, `lw` means if, `etba3` means print.

This is both a **language design project** and a **compiler engineering project**.

---

## The two things being built

### 1. The Francode Language (v0.1)
A statically typed, C-like language with Franco-Arabic keywords. The full spec lives in `docs/LANGUAGE_SPEC_v0_1.md`. Key features in v0.1:
- Two types: `rakm` (integer) and `kasr` (float)
- Variables, arithmetic, comparisons
- `lw` / `tb lw` / `aw` (if / else if / else)
- `tol lma` (while loop)
- `ya` functions with `raga3` return
- `etba3` built-in print
- Single-line `//` and multi-line `/* */` comments

### 2. The Compiler/Interpreter (Python)
A tree-walk interpreter pipeline. No bytecode, no transpilation — the AST is walked directly at runtime.

Pipeline: `.fc source` → Lexer → Token list → Parser → AST → Semantic Analyzer → Interpreter → Output

---

## Repository

GitHub: https://github.com/aliyasser789/compiler_project

Structure:
```
COMPILER_PROJECT/
├── docs/
│   └── LANGUAGE_SPEC_v0_1.md      ← full language rules
├── examples/                       ← .fc sample programs (to be added)
├── src/
│   └── francode/
│       ├── __init__.py
│       ├── tokens.py               ← TokenType enum + Token dataclass
│       ├── ast_nodes.py            ← all AST node classes
│       ├── lexer.py                ← source → token list
│       ├── parser.py               ← token list → AST
│       ├── semantic.py             ← AST type/scope checker
│       └── interpreter.py          ← AST executor (IN PROGRESS)
├── tests/                          ← pytest test suite (to be added)
├── .gitignore
├── LICENSE
├── README.md
└── pyproject.toml                  ← (to be added)
```

---

## Tech Stack

- Language: Python 3.12+
- Testing: pytest
- No external runtime dependencies
- All source under `src/francode/` as a proper Python package

---

## Coding Conventions

- All files use `from __future__ import annotations`
- Dataclasses with `slots=True` for all AST nodes and data structures
- Type hints everywhere — no untyped functions
- `__all__` defined at the bottom of every module
- Error classes are dataclasses with `message`, `line`, `col` fields
- No global mutable state — all state lives in class instances
- Naming: snake_case for functions/variables, PascalCase for classes

---

## Current Status

### Done (front-end complete)
- `tokens.py` — all 10 keywords, all operators, correct enum design
- `ast_nodes.py` — full node hierarchy for every v0.1 construct
- `lexer.py` — full tokenizer with comment handling
- `parser.py` — recursive descent parser, correct operator precedence
- `semantic.py` — two-pass semantic analyzer, lexical scoping, type checking

### Known issues to fix before interpreter
1. **Condition validation too strict** — `semantic.py` rejects variables in conditions like `tol lma (x > 0)`. Should allow any comparison expression, not just literals.
2. **No line/col on AST nodes** — all errors report `line 1, col 1`. Need to add location fields to `Node` base class and thread token positions through the parser.
3. **Function syntax mismatch** — spec shows `ya name(...)` but parser requires `rakm ya name(...)`. Decision: keep parser's version (explicit return type) and update the spec.

### Not started (back-end)
- `interpreter.py` — tree-walk evaluator (highest priority)
- `__main__.py` — CLI entry point
- `pyproject.toml` — package config
- `examples/*.fc` — sample programs
- `tests/` — full test suite
- `README.md` — currently 0 bytes

---

## Language Keywords Reference

| Franco-Arabic | Meaning        | Usage                           |
|---------------|----------------|---------------------------------|
| `rakm`        | integer type   | `rakm x = 5;`                   |
| `kasr`        | float type     | `kasr y = 3.14;`                |
| `ya`          | function def   | `rakm ya add(rakm a) { }`       |
| `raga3`       | return         | `raga3 x;`                      |
| `lw`          | if             | `lw (x > 0) { }`               |
| `tb lw`       | else if        | `tb lw (x == 0) { }`           |
| `aw`          | else           | `aw { }`                        |
| `tol lma`     | while          | `tol lma (x > 0) { }`          |
| `etba3`       | print          | `etba3(x);`                     |

---

## Important Spec Rules (v0.1)

- Division `/` always returns `kasr` (float), even `rakm / rakm`
- Float-to-int truncates toward zero: `7.7 → 7`, `-7.7 → -7`
- No boolean type: `1` = true, `0` = false in conditions
- Conditions must be a comparison expression or literal `0`/`1`
- Blocks `{ }` are mandatory — no single-line bodies
- Every statement ends with `;`
- Redeclaring a variable in the same scope is an error
- Assigning to an undeclared variable is an error
- Functions must contain at least one `raga3`

---

## How to Run (once interpreter is done)

```bash
cd src
python -m francode examples/hello.fc
```

Or after installing:
```bash
francode examples/hello.fc
```
