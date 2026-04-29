# Francode 🇪🇬

Francode is a custom programming language and tree-walk interpreter built from scratch in Python. It uses **Franco-Arabic keywords** — Arabic written in Latin letters — to make programming approachable for Egyptian beginners and children. By replacing English keywords with familiar words like `rakm` (number), `lw` (if), and `etba3` (print), Francode lowers the barrier to entry and lets learners focus on programming concepts rather than an unfamiliar language.

---

## Keywords

| Franco-Arabic | Meaning | Usage Example |
|---|---|---|
| `rakm` | Integer type | `rakm x = 5;` |
| `kasr` | Float type | `kasr y = 3.14;` |
| `ya` | Define a function | `rakm ya add(rakm a, rakm b) { ... }` |
| `raga3` | Return a value | `raga3 a + b;` |
| `lw` | If | `lw (x > 0) { ... }` |
| `tb lw` | Else if | `tb lw (x == 0) { ... }` |
| `aw` | Else | `aw { ... }` |
| `tol lma` | While loop | `tol lma (x > 0) { ... }` |
| `etba3` | Print to stdout | `etba3(x);` |

---

## Quick Example

The program below defines a function that adds two numbers, then calls it and prints the result.

```francode
// functions.fc
// Define a function that returns the sum of two integers
rakm ya add(rakm a, rakm b) {
    raga3 a + b;
}

// Call it and print the result
rakm s = add(4, 6);
etba3(s);
```

**Expected output:**
```
10
```

Run it yourself:
```bash
python -m francode examples/functions.fc
```

---

## Installation

**Requires Python 3.12 or later.**

```bash
# 1. Clone the repository
git clone https://github.com/aliyasser789/compiler_project.git
cd compiler_project

# 2. Install the package in editable mode
pip install -e .
```

---

## CLI Usage

Run any `.fc` file by passing its path to the `francode` module:

```bash
python -m francode examples/hello.fc
```

Or use the installed console script directly:

```bash
francode examples/hello.fc
```

**Exit codes:**
- `0` — program ran successfully
- `1` — any error occurred (lex, parse, semantic, or runtime)

**Errors** are printed to `stderr` with the exact line and column number, for example:

```
[Line 3, Col 5] SemanticError: variable 'x' already declared in this scope
```

---

## Web Playground

A browser-based playground lets users write and run Francode code without installing anything.

### 1. Install backend dependencies

```bash
pip install -r playground/requirements.txt
```

### 2. Start the backend

```bash
python -m uvicorn playground.backend.main:app --reload
```

### 3. Open the frontend

Open `playground/frontend/index.html` in your browser.

The playground includes:
- An **examples dropdown** — load any built-in `.fc` program with one click
- A **Run** button — executes the code and shows output in the output panel
- A **Clear** button — resets the editor and output

---

## Project Structure

```
compiler_project/
├── docs/                   # Language specification
│   └── LANGUAGE_SPEC_v0_1.md
├── examples/               # Example .fc programs
│   ├── hello.fc
│   ├── arithmetic.fc
│   ├── conditionals.fc
│   ├── loop.fc
│   ├── functions.fc
│   ├── fibonacci.fc
│   └── nested.fc
├── src/francode/           # Interpreter source code
│   ├── tokens.py
│   ├── ast_nodes.py
│   ├── lexer.py
│   ├── parser.py
│   ├── semantic.py
│   ├── interpreter.py
│   └── __main__.py
├── tests/                  # Pytest test suite (181 tests)
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_semantic.py
│   └── test_interpreter.py
├── playground/             # Web playground (backend + frontend)
│   ├── backend/
│   └── frontend/
└── pyproject.toml
```

---

## Language Specification

For the full language reference — including type rules, operator precedence, scoping rules, and grammar — see:

📄 [`docs/LANGUAGE_SPEC_v0_1.md`](docs/LANGUAGE_SPEC_v0_1.md)
