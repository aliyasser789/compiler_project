# Francode — Implementation Steps

This is the complete ordered roadmap for building the Francode compiler.
Check off items as they are completed. Do not skip steps — each one depends on the previous.

---

## Phase 1 — Front-End (COMPLETE)

### Step 1.1 — Token definitions
- [x] Define `TokenType` enum with all keywords, operators, punctuation
- [x] Define `Token` dataclass with `type`, `value`, `line`, `col`
- [x] Define `LexerError` exception class

### Step 1.2 — AST node definitions
- [x] Define `Node`, `Stmt`, `Expr` base classes with `slots=True`
- [x] Define `VarType` enum (`RAKM`, `KASR`)
- [x] Define literal nodes: `IntLiteral`, `FloatLiteral`
- [x] Define expression nodes: `VarRef`, `BinaryOp`, `CallExpr`
- [x] Define statement nodes: `VarDecl`, `Assign`, `PrintStmt`, `ReturnStmt`
- [x] Define control flow nodes: `IfStmt`, `WhileStmt`, `Block`
- [x] Define top-level nodes: `Param`, `FuncDef`, `Program`

### Step 1.3 — Lexer
- [x] Tokenize integer and float literals
- [x] Tokenize identifiers and keyword lookup
- [x] Tokenize all arithmetic and comparison operators (including two-char)
- [x] Tokenize all punctuation
- [x] Skip single-line comments `//`
- [x] Skip multi-line comments `/* */` with unterminated error
- [x] Track line and column for every token
- [x] Raise `LexerError` with location on unknown characters

### Step 1.4 — Parser
- [x] Recursive descent parser skeleton
- [x] Parse variable declarations (`rakm x = expr;`)
- [x] Parse assignment statements (`x = expr;`)
- [x] Parse `etba3(expr);` print statement
- [x] Parse `raga3 expr;` return statement
- [x] Parse `lw / tb lw / aw` if-elif-else chains
- [x] Parse `tol lma` while loops
- [x] Parse `rakm ya name(params) { }` function definitions
- [x] Parse expressions with correct precedence: comparison > term > factor > unary > primary
- [x] Parse function call expressions
- [x] Parse parenthesized expressions
- [x] Parse unary minus

### Step 1.5 — Semantic Analyzer
- [x] Two-pass design: collect all function signatures first
- [x] Lexical scope stack (push/pop on every block)
- [x] Reject variable redeclaration in same scope
- [x] Reject assignment to undeclared variable
- [x] Type inference for all expression types
- [x] Type compatibility checks (rakm ↔ kasr conversions allowed)
- [x] Division `/` always returns `kasr`
- [x] Comparison operators return `rakm`
- [x] Function call argument count and type checking
- [x] Return type checking against declared function return type
- [x] `raga3` only allowed inside a function
- [x] Function must contain at least one `raga3`
- [x] Condition validation (comparison or 0/1 literal)

---

## Phase 2 — Bug Fixes (DO THESE BEFORE INTERPRETER)

### Step 2.1 — Fix condition validation in semantic.py
- [ ] Allow `VarRef` inside conditions if the expression is a valid comparison
- [ ] Current bug: `tol lma (x > 0)` is incorrectly rejected
- [ ] Rule: condition must be a comparison `BinaryOp` or `IntLiteral(0/1)` — `VarRef`s are valid inside the comparison operands

### Step 2.2 — Add source locations to AST nodes
- [ ] Add `line: int` and `col: int` fields to the `Node` base class
- [ ] Update every parser construction site to pass token line/col into the node
- [ ] Update `SemanticAnalyzer._error()` to use actual node location instead of hardcoded `1, 1`

### Step 2.3 — Update function syntax in spec
- [ ] Parser uses `rakm ya name(...)` (explicit return type before `ya`)
- [ ] Spec shows `ya name(...)` (no return type before `ya`)
- [ ] Decision: keep parser's version — update `LANGUAGE_SPEC_v0_1.md` to match
- [ ] Update all examples in the spec file to use the correct syntax

---

## Phase 3 — Interpreter (HIGHEST PRIORITY)

### Step 3.1 — Environment (scope/variable store)
- [ ] Create `Environment` class with `define(name, value)`, `get(name)`, `set(name, value)`
- [ ] Support parent environment chaining for lexical scoping
- [ ] Raise `RuntimeError` on get/set of undefined variable
- [ ] Raise `RuntimeError` on redefinition in same scope

### Step 3.2 — Runtime values
- [ ] Define how values are stored at runtime: plain Python `int` and `float`
- [ ] Implement truncation-toward-zero for float-to-int conversion
- [ ] Implement division always returning float

### Step 3.3 — Expression evaluator
- [ ] Evaluate `IntLiteral` → Python `int`
- [ ] Evaluate `FloatLiteral` → Python `float`
- [ ] Evaluate `VarRef` → look up in current environment
- [ ] Evaluate `BinaryOp` for `+`, `-`, `*`
- [ ] Evaluate `BinaryOp` for `/` (always returns float)
- [ ] Evaluate `BinaryOp` for `==`, `!=`, `<`, `>`, `<=`, `>=` (returns 1 or 0)
- [ ] Evaluate `CallExpr` — look up function, bind args, execute body
- [ ] Handle implicit type conversion in binary operations

### Step 3.4 — Statement executor
- [ ] Execute `VarDecl` — evaluate initializer, store in current env
- [ ] Execute `Assign` — evaluate value, update existing binding
- [ ] Execute `PrintStmt` — evaluate expr, print result
- [ ] Execute `ReturnStmt` — evaluate expr, raise `ReturnSignal` to unwind the call stack
- [ ] Execute `Block` — push new scope, run each statement, pop scope
- [ ] Execute `IfStmt` — evaluate condition, run matching branch
- [ ] Execute `WhileStmt` — loop while condition is 1, break on 0
- [ ] Execute `FuncDef` — store function definition in global environment

### Step 3.5 — Function calls
- [ ] Store `FuncDef` nodes as callable values in the environment
- [ ] On `CallExpr`: create new child environment, bind params, execute body
- [ ] Catch `ReturnSignal` to get the return value
- [ ] Apply implicit conversion from return value to declared return type

### Step 3.6 — Runtime error handling
- [ ] Define `FrancodeRuntimeError` class with `message`, `line`, `col`
- [ ] Division by zero → runtime error
- [ ] Condition value not 0 or 1 → runtime error
- [ ] Stack overflow (infinite recursion) → runtime error with clean message

---

## Phase 4 — Entry Point & CLI

### Step 4.1 — Wire up the pipeline
- [ ] Create `src/francode/__main__.py`
- [ ] Accept a `.fc` file path as a command-line argument
- [ ] Read the file, run: Lexer → Parser → SemanticAnalyzer → Interpreter
- [ ] Print any `LexerError`, `ParserError`, `SemanticError`, `RuntimeError` cleanly to stderr
- [ ] Exit with code 0 on success, 1 on any error

### Step 4.2 — Package config
- [ ] Create `pyproject.toml` at project root
- [ ] Define package name `francode`, version `0.1.0`
- [ ] Set `python_requires = ">=3.12"`
- [ ] Add `francode` as a console script entry point
- [ ] Add `pytest` as a dev dependency

---

## Phase 5 — Examples

### Step 5.1 — Write .fc example programs
- [ ] `examples/hello.fc` — declare a variable and print it
- [ ] `examples/arithmetic.fc` — test all 4 operators including division
- [ ] `examples/conditionals.fc` — if / else if / else chain
- [ ] `examples/loop.fc` — while loop counting down
- [ ] `examples/functions.fc` — define and call a function
- [ ] `examples/fibonacci.fc` — recursive fibonacci (stress test)
- [ ] `examples/nested.fc` — nested loops and nested conditionals

---

## Phase 6 — Tests

### Step 6.1 — Lexer tests
- [ ] Test all keywords tokenize correctly
- [ ] Test integer and float literals
- [ ] Test all operators including two-char
- [ ] Test single-line and multi-line comments
- [ ] Test unterminated comment raises `LexerError`
- [ ] Test unknown character raises `LexerError`
- [ ] Test line/col tracking is accurate

### Step 6.2 — Parser tests
- [ ] Test variable declaration parses correctly
- [ ] Test all control flow constructs
- [ ] Test function definition parsing
- [ ] Test operator precedence produces correct AST shape
- [ ] Test unterminated block raises `ParserError`
- [ ] Test missing semicolon raises `ParserError`

### Step 6.3 — Semantic tests
- [ ] Test redeclaration error
- [ ] Test undeclared variable error
- [ ] Test return outside function error
- [ ] Test function with no return error
- [ ] Test wrong argument count error
- [ ] Test condition validation

### Step 6.4 — Interpreter tests
- [ ] Test arithmetic evaluation correctness
- [ ] Test division always returns float
- [ ] Test float-to-int truncation
- [ ] Test if/elif/else branching
- [ ] Test while loop executes and terminates
- [ ] Test function call with return value
- [ ] Test recursive function
- [ ] Test division by zero raises runtime error
- [ ] Test `etba3` prints correct output

---

## Phase 7 — Documentation

### Step 7.1 — README.md
- [ ] Project description and language overview
- [ ] Installation instructions (`pip install -e .`)
- [ ] How to run a `.fc` file
- [ ] Quick example of Francode code with output
- [ ] Link to full language spec in `docs/`

### Step 7.2 — Inline code documentation
- [ ] Review all docstrings for accuracy after interpreter is done
- [ ] Add module-level docstring to each file explaining its role

---

## Build order summary

1. Fix bugs (Phase 2) — ~1 hour
2. Interpreter (Phase 3) — core work, several hours
3. Entry point + pyproject.toml (Phase 4) — make it runnable
4. Example programs (Phase 5) — prove it works
5. Tests (Phase 6) — lock in correctness
6. README (Phase 7) — document it
