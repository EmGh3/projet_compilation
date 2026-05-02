import re
from typing import List, Tuple, Union
from collections import namedtuple


# Token types
class Token:
    """Base class for all tokens"""

    def __repr__(self):
        return str(self)


class Keyword(Token):
    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return f"KW('{self.value}')"

    def __eq__(self, other):
        return isinstance(other, Keyword) and self.value == other.value


class Identifier(Token):
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f"ID('{self.name}')"

    def __eq__(self, other):
        return isinstance(other, Identifier) and self.name == other.name


class Number(Token):
    def __init__(self, value: int):
        self.value = value

    def __str__(self):
        return f"NUM({self.value})"

    def __eq__(self, other):
        return isinstance(other, Number) and self.value == other.value


class Operator(Token):
    def __init__(self, symbol: str):
        self.symbol = symbol

    def __str__(self):
        return f"'{self.symbol}'"

    def __eq__(self, other):
        return isinstance(other, Operator) and self.symbol == other.symbol


class StringLiteral(Token):
    """Token for string literals (anything between double quotes)"""

    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return f'STRING("{self.value}")'

    def __eq__(self, other):
        return isinstance(other, StringLiteral) and self.value == other.value


class Lexer:
    """Lexical analyzer for the custom language"""

    def __init__(self):
        # Define patterns for different token types
        self.token_patterns = [
            ('STRING', r'"[^"]*"'),  # String literals (must be before other patterns)
            ('KEYWORD', r'\b(if|then|else|int|string)\b'),  # Keywords
            ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),  # Identifiers
            ('NUMBER', r'\d+'),  # Integer literals
            # Multi-character operators first
            ('OPERATOR', r'>=|<=|==|!=|[+\-*/=><{}();,!]'),  # Operators and symbols
            ('WHITESPACE', r'[ \t]+'),  # Spaces and tabs
            ('NEWLINE', r'\n'),  # Line breaks
        ]

        # Compile the combined regular expression
        self.token_re = re.compile('|'.join(f'(?P<{name}>{pattern})'
                                            for name, pattern in self.token_patterns))

        # Set of keywords for identification
        self.keywords = {'if', 'then', 'else', 'int', 'string'}

        # Set of operators/symbols
        self.operators = {'+', '-', '*', '/', '=', '>', '<', '>=', '<=', '==', '!=',
                          '{', '}', '(', ')', ';', ',', '!'}

    def tokenize_line(self, line: str) -> List[Token]:
        """Tokenize a single line of source code"""
        tokens = []

        # Remove trailing newline if present
        line = line.rstrip('\n')

        # Find all tokens in the line
        for match in self.token_re.finditer(line):
            token_type = match.lastgroup
            token_value = match.group()

            # Skip whitespace
            if token_type == 'WHITESPACE':
                continue

            # Create appropriate token object
            if token_type == 'STRING':
                # Remove the surrounding quotes for the value
                str_value = token_value[1:-1]  # Remove leading and trailing "
                tokens.append(StringLiteral(str_value))
            elif token_type == 'KEYWORD':
                tokens.append(Keyword(token_value))
            elif token_type == 'IDENTIFIER':
                # Check if it's actually a keyword
                if token_value in self.keywords:
                    tokens.append(Keyword(token_value))
                else:
                    tokens.append(Identifier(token_value))
            elif token_type == 'NUMBER':
                tokens.append(Number(int(token_value)))
            elif token_type == 'OPERATOR':
                tokens.append(Operator(token_value))

        return tokens

    def tokenize(self, source_code: str) -> List[Token]:
        """Tokenize entire source code"""
        all_tokens = []

        # Split source code into lines
        lines = source_code.split('\n')

        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue

            # Tokenize the line
            line_tokens = self.tokenize_line(line)
            all_tokens.extend(line_tokens)

        return all_tokens

    def format_tokens(self, tokens: List[Token]) -> str:
        """Format tokens as a string representation"""
        return '[' + ', '.join(str(token) for token in tokens) + ']'


def test_lexer():
    """Test the lexer with string literals and multi-character operators"""
    print("Testing Lexer with String Literals")
    print("=" * 60)

    lexer = Lexer()

    test_cases = [
        # String literals
        'name = "Alice";',
        'greeting = "Hello World";',
        'message = "Hello" + " World";',

        # Mixed with operators
        'x == 5;',
        'y != 10;',

        # If statements with strings
        'if (name == "Alice") then { greeting = "Hi"; }',

        # Complex expressions
        'result = (x == y) != (a == b);',

        # Strings with special characters
        'path = "C:\\Users\\Name";',
        'empty = "";',

        # Numbers in strings should not be tokenized as numbers
        'code = "12345";',
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Input: {repr(test_case)}")
        tokens = lexer.tokenize(test_case)
        output = lexer.format_tokens(tokens)
        print(f"Output: {output}")


def interactive_mode():
    """Interactive mode for testing the lexer"""
    print("Lexical Analyzer Interactive Mode")
    print("-" * 50)

    lexer = Lexer()

    while True:
        try:
            print("\nEnter code or type 'q' to exit: ", end="")
            user_input = input()

            if user_input.lower() == 'q':
                print("Exiting...")
                break

            if not user_input.strip():
                continue

            tokens = lexer.tokenize(user_input)
            output = lexer.format_tokens(tokens)
            print(f"Tokens: {output}")

        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    # Run tests first
    test_lexer()
    print("\n" + "=" * 60)
    # Then enter interactive mode
    interactive_mode()