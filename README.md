# Projet Compilation - Language Analyzer

This project implements a complete compiler pipeline for a custom programming language with three main analysis stages: lexical, syntax, and semantic analysis.

## Overview

The compiler processes source code through three distinct phases:

1. **Lexical Analysis** - Breaks down source code into tokens
2. **Syntax Analysis** - Builds an Abstract Syntax Tree (AST) from tokens
3. **Semantic Analysis** - Validates type safety and variable scope

---

## 1. Lexical Analyzer (lexical_analyzer.py)

### Purpose
The lexical analyzer (also called a scanner or tokenizer) is the first stage of the compilation process. It reads the raw source code as a stream of characters and converts it into a sequence of meaningful tokens.

### How It Works
- **Pattern Matching**: Uses regular expressions to identify different token types
- **Token Creation**: Creates appropriate token objects for each recognized pattern
- **Whitespace Handling**: Removes whitespace and handles line breaks
- **Error Handling**: Recognizes and handles unknown characters

### Supported Token Types
- **Keywords**: `if`, `then`, `else`, `int`, `string`
- **Identifiers**: Variable names matching pattern `[a-zA-Z_][a-zA-Z0-9_]*`
- **Numbers**: Integer literals (`[0-9]+`)
- **String Literals**: Text enclosed in double quotes (`"..."")
- **Operators**: Arithmetic (`+`, `-`, `*`, `/`), Assignment (`=`), Comparison (`>`, `<`, `>=`, `<=`, `==`, `!=`)
- **Delimiters**: Parentheses `()`, Braces `{}`, Semicolon `;`

### Token Output Format
- `KW('keyword')` - Keywords
- `ID('name')` - Identifiers
- `NUM(value)` - Numbers
- `STRING("value")` - String literals
- `'symbol'` - Operators and delimiters

### Example
```
Input:  int x = 5;
Output: [KW('int'), ID('x'), '=', NUM(5), ';']
```

---

## 2. Syntax Analyzer (syntax_analyzer.py)

### Purpose
The syntax analyzer (parser) takes the stream of tokens from the lexical analyzer and builds an Abstract Syntax Tree (AST) that represents the hierarchical structure of the program according to the language grammar.

### How It Works
- **Recursive Descent Parsing**: Uses a recursive descent algorithm where each grammar rule is implemented as a method
- **Token Consumption**: Advances through tokens while matching expected patterns
- **Error Recovery**: Provides basic error recovery and reports parse errors
- **AST Construction**: Builds tree nodes representing program structure

### Supported AST Nodes
- `Program` - Root node containing all statements
- `DeclarationStmt` - Variable declarations (`type identifier;`)
- `AssignStmt` - Variable assignments (`identifier = expression;`)
- `IfStmt` - Conditional statements with if-then-else blocks
- `Condition` - Boolean expressions with relational operators
- `BinaryOp` - Binary operations (arithmetic and logical)
- `UnaryOp` - Unary operations (negation)
- `Identifier` - Variable references
- `Number` - Integer literals
- `StringLiteral` - String literals

### Language Grammar

```
<program> ::= <statement_list>

<statement_list> ::= <statement> <statement_list> | ε

<statement> ::= <declaration> | <assignment> | <if_stmt>

<declaration> ::= <type> <identifier> ;

<assignment> ::= <identifier> = <expression> ;

<if_stmt> ::= if ( <condition> ) then { <statement_list> } 
            | if ( <condition> ) then { <statement_list> } else { <statement_list> }

<condition> ::= <expression> <relop> <expression>

<expression> ::= <term> <binop> <expression> | <term>

<term> ::= <identifier> | <number> | <string_literal> | <unary_expr>

<unary_expr> ::= - <number>

<type> ::= int | string

<relop> ::= <= | >= | > | < | == | !=

<binop> ::= + | - | * | /

<identifier> ::= [a-zA-Z_][a-zA-Z0-9_]*

<number> ::= [0-9]+ | -[0-9]+

<string_literal> ::= "[^"]*"
```

### Example Parse Tree
```
Input:  int x = 5;
AST:    Program
        └── DeclarationStmt(int, x)
```

---

## 3. Semantic Analyzer (semantic_analyzer.py)

### Purpose
The semantic analyzer validates that the program is semantically correct. It performs type checking, variable scope resolution, and ensures variables are declared before use.

### How It Works
- **Symbol Table Management**: Maintains a symbol table to track variable declarations and their types
- **Scope Tracking**: Manages scope levels, especially for if-then-else blocks
- **Type Checking**: Validates that operations are applied to compatible types
- **Declaration Checking**: Ensures all variables are declared before use
- **Error Collection**: Gathers all semantic errors for reporting

### Key Validations

#### 1. Variable Declaration
- All variables must be declared before use
- Variables cannot be redeclared in the same scope
- Valid types: `int`, `string`

#### 2. Type Checking
- **Arithmetic Operations** (`-`, `*`, `/`): Require `int` operands, return `int`
- **Addition** (`+`): 
  - `int + int` → `int`
  - `string + string` → `string` (concatenation)
  - Mixed types are not allowed
- **Assignment**: Value type must match variable type
- **Conditions**: Both sides of comparison must have compatible types

#### 3. Scope Management
- Global scope for top-level declarations
- New scopes created for `if-then` and `else` blocks
- Variables declared in inner scopes don't affect outer scopes
- Inner scopes can access variables from outer scopes

#### 4. Symbol Table
Tracks for each variable:
- Name
- Type (`int` or `string`)
- Scope level
- Declaration line number

### Example Semantic Analysis
```
Input:
  int x = 5;
  x = "hello";

Errors Found:
  - Type mismatch: Cannot assign string to variable 'x' of type int
```

### Output Report
The semantic analyzer generates a detailed report including:
- Complete symbol table with all declared variables and their types
- All semantic errors found
- All warnings
- Summary statistics

---

## Compilation Pipeline

```
Source Code
    ↓
[Lexical Analyzer] → Tokens
    ↓
[Syntax Analyzer] → AST
    ↓
[Semantic Analyzer] → Validation Report
```

---

## Usage

The three analyzers work together to provide a complete compilation stage:

1. Create a `Lexer` instance and tokenize source code
2. Create a `RecursiveDescentParser` with the tokens and parse them
3. Create a `SemanticAnalyzer` instance and analyze the AST
   
To use the compiler in interactive mode run
```
python interactive_compiler.py
```

---

## Error Handling

- **Lexical Errors**: Unknown characters (handled by skipping)
- **Syntax Errors**: Unexpected token sequence (parser error recovery)
- **Semantic Errors**: Type mismatches, undeclared variables, scope violations

All errors are collected and reported to help identify compilation issues.
