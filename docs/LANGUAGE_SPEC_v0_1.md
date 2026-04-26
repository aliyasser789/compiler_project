# Francode Language Specification v0.1

## 1. Overview

Francode v0.1 is a custom programming language implemented in Python.

The goal of Francode is to serve as an educational programming language designed to introduce children and beginners to core programming concepts in a structured and culturally adapted way.

Francode is designed to teach programming fundamentals clearly and progressively, particularly in an Egyptian educational context, using simplified Arabic-inspired keywords.

Version 0.1 focuses on introducing the following core programming concepts:

- Integer and floating-point arithmetic
- Statically typed variables
- Conditional statements (including nested conditionals)
- Loops (including nested loops)
- Functions
- Basic printing

Advanced features such as arrays, strings, boolean types, classes, and complex data structures are intentionally excluded in v0.1 to keep the language simple and focused.

---

## 2. Syntax Style

Francode follows a C-like syntax structure.

### 2.1 Blocks

Blocks are defined using curly braces:

```
{
    statement1;
    statement2;
}
```

Braces are mandatory for control flow bodies.  
Single-line bodies without `{}` are not allowed.

---

### 2.2 Statement Termination

Each statement must end with a semicolon `;`.

Example:

```
rakm x = 5;
x = x + 1;
```

---

### 2.3 Comments

Single-line comment:

```
// this is a comment
```

Multi-line comment:

```
/*
   multi-line
   comment
*/
```

---

## 3. Data Types

Francode v0.1 supports two numeric types.

### 3.1 rakm (Integer)

Represents signed integers.

Example:

```
rakm x = 5;
```

---

### 3.2 kasr (Float)

Represents floating-point numbers.

Example:

```
kasr y = 7.3;
```

---

### 3.3 Type System Rules

- Variables are statically typed.
- Type is fixed at declaration.
- Redeclaring a variable in the same scope is an error.
- Assigning to an undeclared variable is an error.

---

### 3.4 Implicit Conversions

Francode allows implicit conversions:

- `rakm → kasr` (integer to float) is allowed.
- `kasr → rakm` (float to integer) is allowed.

Float-to-integer conversion:

- Always truncates toward zero.
- `7.7 → 7`
- `-7.7 → -7`

Truncation happens automatically wherever a `rakm` is expected.

---

### 3.5 Boolean Semantics

Francode does not have a boolean type.

Instead:

- `1` represents true.
- `0` represents false.
- Any value other than `1` or `0` inside a condition is an error.

Valid:

```
lw (1) { ... }
```

Error:

```
lw (3) { ... }
```

---

## 4. Program Structure and Scope

### 4.1 Program Structure

A program consists of:

- Function definitions
- Top-level statements

Top-level statements execute in order from top to bottom.

---

### 4.2 Function Declaration

Functions are declared using the keyword `ya`.

Example:

```
rakm ya add(rakm a, rakm b) {
    rakm result = a + b;
    raga3 result;
}
```

---

### 4.3 Scopes

Scopes are created by:

- The global program
- Each function body
- Each block `{ ... }`

Variable lookup follows lexical scoping:

- Search current scope first
- Then outer scope
- If not found → error

---

### 4.4 Variable Declaration Rules

Examples:

```
rakm x = 5;
kasr y = 3.2;
```

Rules:

- Type remains fixed after declaration.
- Assignments must respect type rules and implicit conversions.

---

## 5. Control Flow

### 5.1 If Statement

Keyword: `lw`

```
lw (condition) {
    ...
}
```

---

### 5.2 Else If

Keyword sequence: `tb lw`

```
lw (condition1) {
    ...
}
tb lw (condition2) {
    ...
}
aw {
    ...
}
```

---

### 5.3 Else

Keyword: `aw`

---

### 5.4 While Loop

Keyword sequence: `tol lma`

Only while loops are supported in v0.1.

```
tol lma (condition) {
    ...
}
```

---

## 6. Expressions and Operators

### 6.1 Arithmetic Operators

- `+`
- `-`
- `*`
- `/`

Division `/` always returns `kasr`.

Example:

```
rakm x = 5 / 2;   // 5 / 2 = 2.5 → truncated to 2
```

---

### 6.2 Comparison Operators

- `==`
- `!=`
- `<`
- `>`
- `<=`
- `>=`

Comparison results:

- `1` if true
- `0` if false

---

### 6.3 Operator Precedence

From highest to lowest:

1. Parentheses `( )`
2. `* /`
3. `+ -`
4. Comparisons

All arithmetic operators are left-associative.

---

## 7. Built-in Function

### 7.1 Printing

Built-in function:

```
etba3(expression);
```

Example:

```
rakm x = 5;
etba3(x);
```

---

## 8. Keywords

Reserved keywords:

- `rakm`
- `kasr`
- `ya`
- `lw`
- `aw`
- `tb`
- `tol`
- `lma`
- `raga3`
- `etba3`

Identifiers cannot use these names.

---

## 9. Identifiers

Rules:

- Must start with a letter or underscore.
- Followed by letters, digits, or underscores.
- Case-sensitive.

Examples:

```
x
_sum
value1
```

---

## 10. Whitespace

Whitespace is ignored except as separator between tokens.