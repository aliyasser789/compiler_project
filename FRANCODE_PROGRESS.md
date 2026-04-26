# Francode — Progress Log

This file tracks what has been completed, what is in progress, and what to work on next.
Update this file at the end of every working session.

---

## Overall Status

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | Front-end (Lexer, Parser, AST, Semantic) | ✅ Complete |
| Phase 2 | Bug fixes | 🔴 Not started |
| Phase 3 | Interpreter | 🔴 Not started |
| Phase 4 | Entry point & CLI | 🔴 Not started |
| Phase 5 | Example programs | 🔴 Not started |
| Phase 6 | Tests | 🔴 Not started |
| Phase 7 | Documentation | 🔴 Not started |

---

## Completed Work

### Session 1 — Project setup & front-end
**Date:** Early April 2026

**What was built:**
- `tokens.py` — `TokenType` enum with all 10 keywords, all operators, all punctuation. `Token` dataclass with `type`, `value`, `line`, `col`.
- `ast_nodes.py` — Full AST node hierarchy: base classes `Node`/`Stmt`/`Expr`, `VarType` enum, all literal/expression/statement/top-level nodes. Uses `slots=True` dataclasses throughout.
- `lexer.py` — Full tokenizer: integers, floats, identifiers, keyword lookup, all operators (including two-char lookahead), single-line and multi-line comments, line/col tracking, `LexerError` on unknown chars.
- `parser.py` — Recursive descent parser for all v0.1 constructs. Correct operator precedence chain. Function definitions, control flow, expressions, unary minus.
- `semantic.py` — Two-pass semantic analyzer. Pass 1 collects all function signatures. Pass 2 type-checks everything. Lexical scope stack, redeclaration detection, type compatibility, return checking, condition validation.
- `__init__.py` — Package init (currently only exports from tokens.py — needs expansion later).
- GitHub repo created: https://github.com/aliyasser789/compiler_project
- Language spec written: `docs/LANGUAGE_SPEC_v0_1.md`

---

## Known Bugs (must fix before interpreter)

### Bug 1 — Condition validation too strict (semantic.py)
**File:** `src/francode/semantic.py` — `check_condition()` method
**Problem:** Rejects `VarRef` inside conditions. Code like `tol lma (x > 0)` fails because the left side of the comparison is a `VarRef`, not a literal.
**Fix:** `check_condition` should allow any `BinaryOp` with a comparison operator. The operands can be any valid expression (VarRef, literals, arithmetic). Only a bare non-comparison expression used directly as a condition (like just `x`) should be checked against the 0/1 rule.

### Bug 2 — All errors report line 1, col 1
**Files:** `src/francode/ast_nodes.py`, `src/francode/parser.py`, `src/francode/semantic.py`
**Problem:** The `Node` base class has no `line`/`col` fields. `SemanticAnalyzer._error()` hardcodes `line=1, col=1`. All semantic error messages are useless for debugging.
**Fix:** Add `line: int` and `col: int` to the `Node` dataclass. Update every node construction in `parser.py` to pass in the token's location. Update `_error()` to accept and use node location.

### Bug 3 — Function syntax mismatch between spec and parser
**Files:** `docs/LANGUAGE_SPEC_v0_1.md`, `src/francode/parser.py`
**Problem:** The spec shows `ya add(rakm a, rakm b) { }` but the parser requires `rakm ya add(rakm a, rakm b) { }`.
**Decision:** Keep the parser's version — explicit return type is better language design. Update the spec to match.

---

## Next Session Goals

### Priority 1 — Fix Bug 1 (30 min)
Fix `check_condition()` in `semantic.py` to allow VarRefs inside comparison operands.

### Priority 2 — Fix Bug 2 (1–2 hours)
Add location fields to AST nodes and thread them through the parser.

### Priority 3 — Fix Bug 3 (15 min)
Update the spec file to show `rakm ya` syntax instead of `ya` alone.

### Priority 4 — Start interpreter
Begin `src/francode/interpreter.py`:
1. `Environment` class first
2. Expression evaluator
3. Statement executor
4. Function call handling

---

## Session Log

### [Add new sessions below this line]

#### Session 2 — [DATE]
**What was done:**
-

**Bugs fixed:**
-

**What's next:**
-

---

## Decisions Made

| Decision | Chosen Option | Reason |
|----------|---------------|--------|
| Execution model | Tree-walk interpreter | Simpler for v0.1, no bytecode needed |
| Type conversions | Both rakm↔kasr allowed | Spec explicitly allows both directions |
| Division result | Always kasr | Spec rule: `/` always returns float |
| Function syntax | `rakm ya name(...)` | Explicit return type is clearer |
| Python version | 3.12+ | Needed for `slots=True` + modern type hints |
| Test framework | pytest | Standard, simple, no boilerplate |
