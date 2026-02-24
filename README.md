# Toy Language Specification v0.1

## 1. Overview

This document defines version 0.1 of a custom programming language
implemented in Python.

The goal of v0.1 is to create a small but complete language that supports:

- Integer arithmetic
- Variables
- Conditional statements
- Loops
- Functions
- Basic printing

This version focuses on clarity and simplicity. Advanced features like
types, classes, arrays, and strings are intentionally excluded.

---

## 2. Syntax Style

The language follows a C-like syntax style.

### 2.1 Blocks

Blocks are defined using curly braces:

```
{
    statement1;
    statement2;
}
```

### 2.2 Statement Termination

Each statement must end with a semicolon `;`

Example:

```
let x = 5;
x = x + 1;
```

### 2.3 Comments

Single-line comments:

```
// this is a comment
```

Multi-line comments:

```
/*
   this is
   a multi-line
   comment
*/
```
### 3.1 Data Types
- **Integer** only (signed).
- No floats, strings, arrays, or booleans in v0.1.
  - Conditions use integers: `0` = false, non-zero = true.
  ## 4. Program Structure and Scope

### 4.1 Program Structure
A program is a sequence of:
- Function definitions (`func ... { ... }`)
- Top-level statements (e.g., `let x = 5; print(x);`)

Top-level statements execute in order from top to bottom.

### 4.2 Scopes
Scopes are created by:
- The top-level program (global scope)
- Each function body
- Each block `{ ... }` inside `if` / `while`

### 4.3 Name Resolution
When referencing a variable name:
- The compiler searches the current scope first.
- If not found, it searches outward scope-by-scope.
- If not found anywhere: **error**.

### 4.4 Variable Declaration Rules
- `let x = expr;` declares a **new** variable in the current scope.
- Declaring the same name twice in the same scope is an **error**.
- Assigning to an undeclared variable is an **error**.

Example:
```
let x = 1;
{
    let x = 2;  // allowed (new inner scope)
    print(x);   // prints 2
}
print(x);       // prints 1
```
## 5. Operator Precedence and Associativity

Expressions follow standard precedence rules.

From highest to lowest precedence:

1. Parentheses: `(expr)`
2. Multiplication / Division: `* /`
3. Addition / Subtraction: `+ -`
4. Comparisons: `== != < > <= >=`

### 5.1 Associativity
- `* / + -` are **left-associative**:
  - `10 - 3 - 2` is `(10 - 3) - 2`
- Comparisons are **not chainable** in v0.1:
  - `1 < x < 3` is **not allowed**
  - You must write: `(1 < x) == 1 && (x < 3) == 1` (note: `&&` not supported in v0.1)
  - So for v0.1, do comparisons one at a time.

### 5.2 Examples
```
let a = 2 + 3 * 4;       // 2 + (3*4) = 14
let b = (2 + 3) * 4;     // 20
let c = 10 - 3 - 2;      // (10-3)-2 = 5
```
## 6. Keywords and Tokens (Lexer Contract)

### 6.1 Keywords
The following words are reserved and cannot be used as identifiers:

- `let`
- `func`
- `if`
- `else`
- `while`
- `return`

### 6.2 Operators
Arithmetic:
- `+` `-` `*` `/`

Assignment:
- `=`

Comparisons:
- `==` `!=` `<` `>` `<=` `>=`

### 6.3 Punctuation
- `(` `)` for grouping and function calls
- `{` `}` for blocks
- `,` for separating function parameters/arguments
- `;` for ending statements

### 6.4 Identifiers
Identifiers are names for variables and functions.

Rules:
- Start with a letter or underscore: `[A-Za-z_]`
- Followed by letters, digits, or underscores: `[A-Za-z0-9_]*`
- Examples: `x`, `_temp`, `add2`, `my_var`

### 6.5 Integer Literals
Integers are sequences of digits:
- Examples: `0`, `7`, `42`, `123456`

### 6.6 Whitespace
Spaces, tabs, and newlines are ignored except as separators between tokens.

### 6.7 Comments
- Single-line comment starts with `//` and ends at newline
- Multi-line comment starts with `/*` and ends with `*/`