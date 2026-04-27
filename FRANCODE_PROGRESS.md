# Francode — Progress Log

This file tracks what has been completed, what is in progress, and what to work on next.
Update this file at the end of every working session.

---

## Overall Status

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | Front-end (Lexer, Parser, AST, Semantic) | ✅ Complete |
| Phase 2 | Bug fixes | ✅ Complete |
| Phase 3 | Interpreter | ✅ Complete |
| Phase 4 | Entry point & CLI | ✅ Complete |
| Phase 5 | Example programs | ✅ Complete |
| Phase 6 | Tests | ✅ Complete — 181/181 pass |
| Phase 7 | Web Playground (browser UI) | 🔴 Not started |
| Phase 8 | Documentation | 🔴 Not started |

---

## Completed Work

### Session 1 — Project setup & front-end
**Date:** Early April 2026
**Who:** Full team

**What was built:**
- `tokens.py` — `TokenType` enum with all 10 keywords, all operators, all punctuation. `Token` dataclass with `type`, `value`, `line`, `col`.
- `ast_nodes.py` — Full AST node hierarchy: base classes `Node`/`Stmt`/`Expr`, `VarType` enum, all literal/expression/statement/top-level nodes. Uses `slots=True` dataclasses throughout.
- `lexer.py` — Full tokenizer: integers, floats, identifiers, keyword lookup, all operators (including two-char lookahead), single-line and multi-line comments, line/col tracking, `LexerError` on unknown chars.
- `parser.py` — Recursive descent parser for all v0.1 constructs. Correct operator precedence chain. Function definitions, control flow, expressions, unary minus.
- `semantic.py` — Two-pass semantic analyzer. Pass 1 collects all function signatures. Pass 2 type-checks everything. Lexical scope stack, redeclaration detection, type compatibility, return checking, condition validation.
- `__init__.py` — Package init.
- GitHub repo created: https://github.com/aliyasser789/compiler_project
- Language spec written: `docs/LANGUAGE_SPEC_v0_1.md`

---

### Session 2 — Bug fixes (Phase 2)
**Date:** Late April 2026
**Who:** Full team

**What was done:**
All three known bugs from Phase 2 were fixed before starting the interpreter.

**Bug 1 — Condition validation too strict (`semantic.py`)**
- Problem: `check_condition()` rejected `VarRef` nodes inside conditions. Code like `tol lma (x > 0)` was incorrectly rejected because the left operand was a `VarRef`, not a literal.
- Fix: Updated `check_condition()` to allow any `BinaryOp` with a comparison operator as a valid condition. Operands can be any valid expression (VarRef, literals, arithmetic). Only a bare non-comparison expression used directly as a condition (like just `x` alone) gets checked against the 0/1 rule.

**Bug 2 — All errors reported line 1, col 1 (`ast_nodes.py`, `parser.py`, `semantic.py`)**
- Problem: The `Node` base class had no `line`/`col` fields. `SemanticAnalyzer._error()` hardcoded `line=1, col=1`, making all error messages useless for debugging.
- Fix: Added `line: int` and `col: int` to the `Node` dataclass. Updated every node construction site in `parser.py` to pass in the token's location. Updated `_error()` to accept and use actual node location.

**Bug 3 — Function syntax mismatch between spec and parser (`docs/LANGUAGE_SPEC_v0_1.md`)**
- Problem: The spec showed `ya add(rakm a, rakm b) { }` but the parser required `rakm ya add(rakm a, rakm b) { }`.
- Decision: Kept the parser's version (explicit return type is better language design). Updated `LANGUAGE_SPEC_v0_1.md` to match.

**Problems encountered during bug fixes:**
- Git merge conflicts appeared in `ast_nodes.py`, `parser.py`, and `semantic.py` after teammates pushed changes simultaneously. The conflict was between the original version and the Bug 2 fix (adding `line`/`col` to nodes).
- The package was inconsistently named — some files imported from `codawy` (a teammate's folder name) instead of `francode`.
- `src/francode/__init__.py` was deleted in one branch and modified in another, causing a modify/delete conflict.

**How conflicts were fixed:**
- Ran `git merge --abort` to reset to a clean state, then used `git stash` to save local changes before pulling.
- Resolved all `<<<<<<`/`=======`/`>>>>>>>` conflict markers manually — kept the version with `line=`/`col=` kwargs on nodes (the correct Bug 2 version).
- Replaced all `from codawy.` imports with `from francode.` across all files.
- Kept `src/francode/__init__.py` (did not delete it).
- Teammates who had too-broken local state did a fresh clone: `git clone https://github.com/aliyasser789/compiler_project.git`

---

### Session 3 — Interpreter (Phase 3)
**Date:** Late April 2026
**Who:** Teammate

**What was built (`src/francode/interpreter.py`):**
- `Environment` class with `define()`, `get()`, `set()`, and parent-chaining for lexical scoping. Raises `RuntimeError` on get/set of undefined variable and on redefinition in same scope.
- Runtime value semantics: plain Python `int` for `rakm`, `float` for `kasr`. Truncation-toward-zero for float-to-int conversion. Division always returns `float`.
- Full expression evaluator: `IntLiteral`, `FloatLiteral`, `VarRef`, `BinaryOp` (all arithmetic and comparison operators), `CallExpr`.
- Full statement executor: `VarDecl`, `Assign`, `PrintStmt`, `ReturnStmt`, `Block`, `IfStmt`, `WhileStmt`, `FuncDef`.
- Function call handling: `FuncDef` nodes stored as callable values in the global environment. On `CallExpr`, creates a new child environment, binds params, executes body, catches `ReturnSignal` to get return value.
- `ReturnSignal` implemented as a Python exception to cleanly unwind the call stack.
- `FrancodeRuntimeError` dataclass with `message`, `line`, `col` fields.
- Runtime error handling: division by zero, invalid condition values, stack overflow guard (soft cap at 500 frames, also catches Python's native `RecursionError`).

---

### Session 4 — Entry point & CLI (Phase 4)
**Date:** Late April 2026
**Who:** Ali

**What was built:**
- `src/francode/__main__.py` — accepts a `.fc` file path as a CLI argument, runs the full pipeline (Lexer → Parser → SemanticAnalyzer → Interpreter), prints any error cleanly to stderr with line/col, exits with code 0 on success and 1 on error.
- `pyproject.toml` — package name `francode`, version `0.1.0`, `python_requires = ">=3.12"`, `francode` console script entry point, `pytest` as dev dependency.

**Verified working:**
```
python -m francode test.fc
```
Running `etba3(5);` printed `5` correctly. Phase 4 confirmed complete.

**Problems encountered:**
- Initial test showed empty output — the `test.fc` file wasn't saved at the time. Once saved, it worked correctly.
- The `codawy` vs `francode` naming conflict required a cleanup pass to ensure all imports were consistent before `__main__.py` could run without `ImportError`.

---

### Session 5 — Example programs (Phase 5)
**Date:** Late April 2026
**Who:** Teammate

**What was built (`examples/` folder):**
- `hello.fc` — declare a variable and print it
- `arithmetic.fc` — all 4 operators including division
- `conditionals.fc` — if / else if / else chain
- `loop.fc` — while loop counting down
- `functions.fc` — define and call a function
- `fibonacci.fc` — recursive fibonacci (stress test)
- `nested.fc` — nested loops and nested conditionals

---

### Session 6 — Tests (Phase 6)
**Date:** Late April 2026
**Who:** Full team

**Result: 181/181 tests pass.**

| File | Tests | Coverage |
|------|-------|----------|
| `test_lexer.py` | 37 | All 10 keywords, int/float literals, single/two-char operators, all punctuation, single-line and multi-line comments, unterminated comment error, unknown char error, line/col tracking |
| `test_parser.py` | 52 | `VarDecl`, `Assign`, `PrintStmt`, `ReturnStmt`, `IfStmt` (lw/tb lw/aw), `WhileStmt`, `FuncDef` (all fields), `CallExpr`, operator precedence (4 cases), 6 parser error cases |
| `test_semantic.py` | 32 | Valid programs (9), scope errors, return errors, function call errors, condition validation (4 cases), `SemanticError` struct |
| `test_interpreter.py` | 60 | Arithmetic + precedence, type coercions, all 6 comparison operators, variables, `etba3` output via `capsys`, conditionals, while loops, function calls, recursive fibonacci up to fib(10), runtime errors, lexical scoping |

**Two fixes made during testing:**
1. Stack overflow test — updated to accept both `FrancodeRuntimeError` and Python's native `RecursionError`, since Python's stack limit (~1000 frames) can fire before the interpreter's soft cap (500 frames) in certain call patterns.
2. Redeclaration in block test — original test used a param name and a local variable in the function body block (different scopes, semantically valid). Fixed to declare the same name twice in the same block, which is the actual error case.

---

## Next Session Goals

### Phase 7 — Web Playground
Build a browser-based UI so users can type Francode code, hit run, and see output without installing anything. Planned components:
- A lightweight backend API (Flask or FastAPI) wrapping the compiler pipeline
- A frontend with a code editor and output panel
- Pre-loaded example programs users can select from a dropdown

### Phase 8 — Documentation
After the playground is complete:
- `README.md` — project description, installation, CLI usage, playground usage, quick example with output
- Inline docstrings review across all modules
- Link to full language spec in `docs/`

---

## Session Log

### [Add new sessions below this line]

#### Session 7 — [DATE]
**What was done:**
-

**Problems encountered:**
-

**What's next:**
-

---

## Problems Encountered & How They Were Fixed

| Problem | When | Fix |
|---------|------|-----|
| Git merge conflicts in `ast_nodes.py`, `parser.py`, `semantic.py` | Phase 2 | `git merge --abort` → `git stash` → pull → `git stash pop` → manual conflict resolution. Kept the `line=`/`col=` version throughout. |
| Package named `codawy` in some files, `francode` in others | Phase 2–4 | Replaced all `from codawy.` with `from francode.` across all files. Verified imports end-to-end. |
| `src/francode/__init__.py` deleted in one branch, modified in another | Phase 2 | Kept the file (did not delete). Resolved as modify/delete conflict by accepting the modified version. |
| `git stash` failed mid-conflict because index was dirty | Phase 2 | Ran `git merge --abort` first to reset the index, then stashed cleanly. |
| Teammate's local repo too broken to recover | Phase 2 | Fresh clone: `git clone https://github.com/aliyasser789/compiler_project.git` |
| Stack overflow test unreliable across environments | Phase 6 | Accept both `FrancodeRuntimeError` and `RecursionError` in the test — Python's native limit fires unpredictably. |
| Redeclaration test was testing different scopes (valid code) | Phase 6 | Fixed test to declare the same name twice in the same block, which is the actual error case. |
| `test.fc` showed empty output on first CLI run | Phase 4 | File wasn't saved. Once saved, `python -m francode test.fc` worked correctly. |

---

## Decisions Made

| Decision | Chosen Option | Reason |
|----------|---------------|--------|
| Execution model | Tree-walk interpreter | Simpler for v0.1, no bytecode needed |
| Type conversions | Both rakm↔kasr allowed | Spec explicitly allows both directions |
| Division result | Always kasr | Spec rule: `/` always returns float |
| Function syntax | `rakm ya name(...)` | Explicit return type is clearer — spec updated to match |
| Python version | 3.12+ | Needed for `slots=True` + modern type hints |
| Test framework | pytest | Standard, simple, no boilerplate |
| ReturnSignal | Python exception | Cleanly unwinds call stack without passing return values up manually |
| Stack overflow guard | Soft cap 500 + catch RecursionError | Python's native limit is environment-dependent |
| Frontend UI | Web playground (browser-based) | No installation needed, most accessible for users |
| Web playground phase order | Before documentation (Phase 7) | README needs to document the playground — can't write docs for something that doesn't exist yet |
