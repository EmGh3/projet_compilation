from typing import List, Optional, Union
from dataclasses import dataclass
import re
from lexical_analyzer import Lexer, Token, Keyword, Identifier as LexerIdentifier, Number as LexerNumber, Operator, \
    StringLiteral as LexerStringLiteral
"""
Grammar:
<program> ::= <statement_list>
<statement_list> ::= <statement> <statement_list> | ε
<statement> ::= <declaration> | <assignment> | <if_stmt>
<declaration> ::= <type> <identifier> ;
<assignment> ::= <identifier> = <expression> ;
<if_stmt> ::= if ( <condition> ) then { <statement_list> } | if ( <condition> ) then { <statement_list> } else { <statement_list> }
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
"""

# AST Node classes
@dataclass
class ASTNode:
    """Base class for all AST nodes"""
    pass


@dataclass
class Program(ASTNode):
    """Root node of the program"""
    statements: List[ASTNode]

    def __str__(self, indent=0):
        result = "Program\n"
        for stmt in self.statements:
            result += "  " * (indent + 1) + str(stmt) + "\n"
        return result.rstrip()


@dataclass
class DeclarationStmt(ASTNode):
    """Variable declaration statement"""
    var_type: str
    identifier: str

    def __str__(self):
        return f"DeclStmt({self.var_type}, {self.identifier})"


@dataclass
class AssignStmt(ASTNode):
    """Variable assignment statement"""
    identifier: str
    expression: 'Expression'

    def __str__(self):
        return f"AssignStmt({self.identifier}, {self.expression})"


@dataclass
class IfStmt(ASTNode):
    """If-then-else statement"""
    condition: 'Condition'
    body: List[ASTNode]
    else_body: Optional[List[ASTNode]] = None

    def __str__(self):
        result = f"IfStmt({self.condition})\n"
        for stmt in self.body:
            result += "    " + str(stmt) + "\n"
        if self.else_body:
            result += "  Else\n"
            for stmt in self.else_body:
                result += "    " + str(stmt) + "\n"
        return result.rstrip()


@dataclass
class Condition(ASTNode):
    """Condition for if statement"""
    left: 'Expression'
    operator: str
    right: 'Expression'

    def __str__(self):
        return f"Condition({self.left} {self.operator} {self.right})"


@dataclass
class BinaryOp(ASTNode):
    """Binary operation expression"""
    op: str
    left: 'Expression'
    right: 'Expression'

    def __str__(self):
        return f"BinaryOp({self.op}, {self.left}, {self.right})"


@dataclass
class UnaryOp(ASTNode):
    """Unary operation expression (negation)"""
    op: str
    operand: 'Expression'

    def __str__(self):
        return f"UnaryOp({self.op}, {self.operand})"


@dataclass
class Identifier(ASTNode):
    """Identifier node"""
    name: str

    def __str__(self):
        return f"ID({self.name})"


@dataclass
class Number(ASTNode):
    """Integer literal node"""
    value: int

    def __str__(self):
        return f"Num({self.value})"


@dataclass
class StringLiteral(ASTNode):
    """String literal node"""
    value: str

    def __str__(self):
        return f"String({self.value})"


Expression = Union[BinaryOp, UnaryOp, Identifier, Number, StringLiteral]


class ParserToken:
    """Wrapper class to convert Lexer tokens to parser-compatible tokens"""

    def __init__(self, lexer_token):
        self.lexer_token = lexer_token
        self.type = self._determine_type()
        self.value = self._determine_value()

    def _determine_type(self):
        """Determine the token type for the parser"""
        token = self.lexer_token
        token_str = str(token)

        # Check for string literals
        if isinstance(token, LexerStringLiteral) or token_str.startswith('STRING("'):
            return 'STRING'

        # Check for keywords
        if isinstance(token, Keyword) or token_str.startswith("KW('"):
            # Extract the keyword value
            if isinstance(token, Keyword):
                kw_value = str(token).replace("KW('", "").replace("')", "")
            else:
                kw_value = token_str.replace("KW('", "").replace("')", "")

            # Check if it's a type keyword
            if kw_value in ['int', 'string']:
                return 'TYPE'
            # Check if it's a control flow keyword
            elif kw_value in ['if', 'then', 'else']:
                return 'KEYWORD'
            else:
                return 'KEYWORD'

        # Check if token is an identifier that should be a TYPE
        if isinstance(token, LexerIdentifier) or token_str.startswith("ID('"):
            id_value = str(token).replace("ID('", "").replace("')", "")
            if id_value in ['int', 'string']:
                return 'TYPE'
            return 'IDENTIFIER'

        # Check for numbers
        if isinstance(token, LexerNumber) or token_str.startswith("NUM("):
            return 'NUMBER'

        # Check for operators
        if isinstance(token, Operator):
            symbol = str(token).strip("'")
            if symbol in ['+', '-', '*', '/']:
                return 'OPERATOR'
            elif symbol == '=':
                return 'OPERATOR'
            elif symbol in ['>', '<', '==', '!=','>=','<=']:
                return 'RELOP'
            elif symbol == ';':
                return 'SEMICOLON'
            elif symbol == '{':
                return 'LBRACE'
            elif symbol == '}':
                return 'RBRACE'
            elif symbol == '(':
                return 'LPAREN'
            elif symbol == ')':
                return 'RPAREN'
            else:
                return 'OPERATOR'

        # Check for string representations of operators
        if token_str.startswith("'") and token_str.endswith("'"):
            symbol = token_str.strip("'")
            if symbol == ';':
                return 'SEMICOLON'
            elif symbol == '=':
                return 'OPERATOR'
            elif symbol == '+':
                return 'OPERATOR'
            elif symbol == '-':
                return 'OPERATOR'
            elif symbol == '*':
                return 'OPERATOR'
            elif symbol == '/':
                return 'OPERATOR'
            elif symbol in ['>', '<', '==', '!=', '>=', '<=']:
                return 'RELOP'
            elif symbol == '{':
                return 'LBRACE'
            elif symbol == '}':
                return 'RBRACE'
            elif symbol == '(':
                return 'LPAREN'
            elif symbol == ')':
                return 'RPAREN'

        return 'UNKNOWN'

    def _determine_value(self):
        """Determine the token value for the parser"""
        token = self.lexer_token
        token_str = str(token)

        # Check for string literals
        if isinstance(token, LexerStringLiteral) or token_str.startswith('STRING("'):
            if isinstance(token, LexerStringLiteral):
                return token.value
            else:
                # Extract value from STRING("value") format
                match = re.search(r'STRING\("([^"]*)"\)', token_str)
                if match:
                    return match.group(1)
                return ""

        # Check for keywords
        if isinstance(token, Keyword) or token_str.startswith("KW('"):
            return token_str.replace("KW('", "").replace("')", "")

        # Check for identifiers
        if isinstance(token, LexerIdentifier) or token_str.startswith("ID('"):
            return token_str.replace("ID('", "").replace("')", "")

        # Check for numbers
        if isinstance(token, LexerNumber) or token_str.startswith("NUM("):
            num_str = token_str.replace("NUM(", "").replace(")", "")
            return num_str

        # Check for operators
        if isinstance(token, Operator):
            return str(token).strip("'")

        # Check for string representations of operators
        if token_str.startswith("'") and token_str.endswith("'"):
            return token_str.strip("'")

        return token_str

    def __repr__(self):
        return f"ParserToken({self.type}, {self.value})"


class RecursiveDescentParser:
    """Recursive descent parser for the language with if-then-else support and negative numbers"""

    def __init__(self, tokens: List[Token]):
        # Convert Lexer tokens to Parser tokens
        self.tokens = self._convert_tokens(tokens)
        self.pos = 0
        self.current_token = self.tokens[0] if self.tokens else None
        self.errors = []

    def _convert_tokens(self, lexer_tokens: List[Token]) -> List[ParserToken]:
        """Convert tokens from the Lexer to parser-compatible tokens"""
        parser_tokens = []
        for token in lexer_tokens:
            parser_token = ParserToken(token)
            # Only add known token types
            if parser_token.type != 'UNKNOWN':
                parser_tokens.append(parser_token)

        # Add EOF token
        eof_token = type('obj', (object,), {'type': 'EOF', 'value': ''})()
        parser_tokens.append(eof_token)

        return parser_tokens

    def advance(self):
        """Move to the next token"""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]

    def peek(self):
        """Look at the current token"""
        return self.current_token

    def peek_next(self):
        """Look at the next token without advancing"""
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return None

    def expect(self, token_type: str, value: Optional[str] = None) -> bool:
        """Check if current token matches expected type and optional value"""
        token = self.peek()
        if token.type != token_type:
            return False
        if value is not None and token.value != value:
            return False
        return True

    def consume(self, token_type: str, value: Optional[str] = None):
        """Consume a token if it matches, otherwise raise an error"""
        if self.expect(token_type, value):
            token = self.peek()
            self.advance()
            return token
        else:
            expected = f"{token_type}({value})" if value else token_type
            current = self.peek()
            self.error(f"Expected {expected}, got {current.type}({current.value})")
            # Error recovery: skip current token
            self.advance()
            return None

    def error(self, message: str):
        """Record an error message"""
        self.errors.append(f"Parse error at position {self.pos}: {message}")

    def parse(self) -> Optional[Program]:
        """Parse the entire program"""
        statements = self.parse_statement_list()

        if self.errors:
            print("Errors found during parsing:")
            for error in self.errors:
                print(f"  - {error}")
            return None

        return Program(statements)

    def parse_statement_list(self, stop_tokens=None) -> List[ASTNode]:
        """Parse a list of statements until a stop token or EOF"""
        if stop_tokens is None:
            stop_tokens = []

        statements = []

        while self.peek().type != 'EOF':
            # Check if we've encountered a stop token
            if self.peek().type in stop_tokens:
                break

            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)

        return statements

    def parse_statement(self) -> Optional[ASTNode]:
        """Parse a single statement (declaration, assignment, or if-then-else)"""
        # Check for declaration statement
        if self.peek().type == 'TYPE':
            return self.parse_declaration()
        # Check for if statement
        elif self.expect('KEYWORD', 'if'):
            return self.parse_if_stmt()
        # Check for assignment statement
        elif self.peek().type == 'IDENTIFIER':
            return self.parse_assignment()
        else:
            self.error(f"Unexpected token {self.peek().type}({self.peek().value})")
            self.advance()
            return None

    def parse_declaration(self) -> DeclarationStmt:
        """Parse a variable declaration: <type> <id> ;"""
        # Parse type
        type_token = self.consume('TYPE')
        if not type_token:
            return None

        # Parse identifier
        ident_token = self.consume('IDENTIFIER')
        if not ident_token:
            return None

        # Consume semicolon
        self.consume('SEMICOLON', ';')

        return DeclarationStmt(type_token.value, ident_token.value)

    def parse_if_stmt(self) -> IfStmt:
        """Parse an if-then-else statement: if ( <condition> ) then { <stmt_list> } [else { <stmt_list> }]"""
        # Consume 'if' keyword
        self.consume('KEYWORD', 'if')

        # Consume opening parenthesis
        self.consume('LPAREN', '(')

        # Parse condition
        condition = self.parse_condition()
        if not condition:
            return None

        # Consume closing parenthesis
        self.consume('RPAREN', ')')

        # Consume 'then' keyword
        self.consume('KEYWORD', 'then')

        # Consume opening brace
        self.consume('LBRACE', '{')

        # Parse body statements - stop when we hit a closing brace
        body = self.parse_statement_list(stop_tokens=['RBRACE'])

        # Consume closing brace
        self.consume('RBRACE', '}')

        # Check for optional else clause
        else_body = None
        if self.expect('KEYWORD', 'else'):
            # Consume 'else' keyword
            self.consume('KEYWORD', 'else')

            # Consume opening brace
            self.consume('LBRACE', '{')

            # Parse else body statements
            else_body = self.parse_statement_list(stop_tokens=['RBRACE'])

            # Consume closing brace
            self.consume('RBRACE', '}')

        return IfStmt(condition, body, else_body)

    def parse_condition(self) -> Condition:
        """Parse a condition: <expr> <relop> <expr>"""
        # Parse left expression
        left = self.parse_expression()
        if not left:
            return None

        # Parse relational operator
        relop_token = self.consume('RELOP')
        if not relop_token:
            return None

        # Parse right expression
        right = self.parse_expression()
        if not right:
            return None

        return Condition(left, relop_token.value, right)

    def parse_assignment(self) -> AssignStmt:
        """Parse a variable assignment: <id> = <expr> ;"""
        # Parse identifier
        ident_token = self.consume('IDENTIFIER')
        if not ident_token:
            return None

        # Consume equals sign
        self.consume('OPERATOR', '=')

        # Parse expression
        expr = self.parse_expression()

        # Consume semicolon
        self.consume('SEMICOLON', ';')

        return AssignStmt(ident_token.value, expr)

    def parse_expression(self) -> Optional[Expression]:
        """Parse an expression: <expr> + <term> | <term>"""
        # Parse first term
        left = self.parse_term()
        if not left:
            return None

        # Check for additional terms (addition and other binary operators)
        while self.expect('OPERATOR', '+') or self.expect('OPERATOR', '-') or \
                self.expect('OPERATOR', '*') or self.expect('OPERATOR', '/'):
            op_token = None
            if self.expect('OPERATOR', '+'):
                op_token = self.consume('OPERATOR', '+')
            elif self.expect('OPERATOR', '-'):
                op_token = self.consume('OPERATOR', '-')
            elif self.expect('OPERATOR', '*'):
                op_token = self.consume('OPERATOR', '*')
            elif self.expect('OPERATOR', '/'):
                op_token = self.consume('OPERATOR', '/')

            if not op_token:
                break

            right = self.parse_term()
            if not right:
                break
            left = BinaryOp(op_token.value, left, right)

        return left

    def parse_term(self) -> Optional[Expression]:
        """Parse a term: <id> | <number> | <string_lit> | <unary_expr>"""
        token = self.peek()

        # Check for unary minus (negative number)
        if token.type == 'OPERATOR' and token.value == '-':
            # Check if next token is a number
            next_token = self.peek_next()
            if next_token and next_token.type == 'NUMBER':
                # Consume the minus operator
                self.advance()
                # Consume the number
                num_token = self.peek()
                self.advance()
                # Create a negative number
                return Number(-int(num_token.value))
            else:
                # This is a binary operator, not unary
                # Let it be handled by the expression parser
                self.error(f"Expected number after unary minus, got {next_token.type if next_token else 'EOF'}")
                self.advance()
                return None

        if token.type == 'IDENTIFIER':
            self.advance()
            return Identifier(token.value)
        elif token.type == 'NUMBER':
            self.advance()
            return Number(int(token.value))
        elif token.type == 'STRING':
            self.advance()
            return StringLiteral(token.value)
        else:
            self.error(f"Expected identifier, number, or string, got {token.type}({token.value})")
            self.advance()
            return None