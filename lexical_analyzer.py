"""
Lexical Analyzer — Phase 1 du compilateur

Améliorations apportées :
  - Chaque token porte son numéro de ligne (line) et sa colonne (col)
  - Attribut token_type explicite sur chaque classe (plus de parsing par str())
  - Support des commentaires // (ligne) et /* ... */ (bloc)
  - Nouveaux mots-clés : while, bool
  - Nouveaux littéraux : true, false
  - Erreurs lexicales avec position précise (ligne + colonne)
"""

import re
from typing import List, Tuple


# ---------------------------------------------------------------------------
# Classes de tokens
# ---------------------------------------------------------------------------

class Token:
    """Classe de base pour tous les tokens."""
    token_type: str = "TOKEN"

    def __init__(self, line: int = 0, col: int = 0):
        self.line = line
        self.col = col

    def __repr__(self):
        return str(self)


class Keyword(Token):
    token_type = "KEYWORD"

    def __init__(self, value: str, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.value = value

    def __str__(self):
        return f"KW('{self.value}')"

    def __eq__(self, other):
        return isinstance(other, Keyword) and self.value == other.value


class Identifier(Token):
    token_type = "IDENTIFIER"

    def __init__(self, name: str, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.name = name

    def __str__(self):
        return f"ID('{self.name}')"

    def __eq__(self, other):
        return isinstance(other, Identifier) and self.name == other.name


class Number(Token):
    token_type = "NUMBER"

    def __init__(self, value: int, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.value = value

    def __str__(self):
        return f"NUM({self.value})"

    def __eq__(self, other):
        return isinstance(other, Number) and self.value == other.value


class Operator(Token):
    token_type = "OPERATOR"

    def __init__(self, symbol: str, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.symbol = symbol

    def __str__(self):
        return f"'{self.symbol}'"

    def __eq__(self, other):
        return isinstance(other, Operator) and self.symbol == other.symbol


class StringLiteral(Token):
    token_type = "STRING"

    def __init__(self, value: str, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.value = value

    def __str__(self):
        return f'STRING("{self.value}")'

    def __eq__(self, other):
        return isinstance(other, StringLiteral) and self.value == other.value


class BoolLiteral(Token):
    """Token pour les littéraux booléens : true / false."""
    token_type = "BOOL"

    def __init__(self, value: bool, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.value = value

    def __str__(self):
        return f"BOOL({'true' if self.value else 'false'})"

    def __eq__(self, other):
        return isinstance(other, BoolLiteral) and self.value == other.value


class LexicalError(Exception):
    """Erreur lexicale avec position précise."""

    def __init__(self, message: str, line: int, col: int):
        super().__init__(f"Erreur lexicale à la ligne {line}, col {col} : {message}")
        self.lex_line = line
        self.lex_col = col


# ---------------------------------------------------------------------------
# Lexer
# ---------------------------------------------------------------------------

class Lexer:
    """
    Analyseur lexical.

    Mots-clés supportés  : if, then, else, while, int, string, bool
    Littéraux booléens   : true, false
    Commentaires         : // ... fin de ligne  |  /* ... */
    """

    KEYWORDS = {'if', 'then', 'else', 'while', 'int', 'string', 'bool'}
    BOOL_LITERALS = {'true', 'false'}

    # Patterns dans l'ordre de priorité (IMPORTANT : block avant line)
    _TOKEN_PATTERNS: List[Tuple[str, str]] = [
        ('BLOCK_COMMENT', r'/\*.*?\*/'),
        ('LINE_COMMENT',  r'//[^\n]*'),
        ('STRING',        r'"[^"]*"'),
        ('NUMBER',        r'\d+'),
        ('OPERATOR',      r'>=|<=|==|!=|[+\-*/=><{}();,!]'),
        ('WORD',          r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('NEWLINE',       r'\n'),
        ('WHITESPACE',    r'[ \t\r]+'),
        ('UNKNOWN',       r'.'),
    ]

    def __init__(self):
        combined = '|'.join(
            f'(?P<{name}>{pat})' for name, pat in self._TOKEN_PATTERNS
        )
        self._re = re.compile(combined, re.DOTALL)

    def tokenize(self, source_code: str) -> List[Token]:
        """
        Tokenise le code source complet.
        Retourne la liste des tokens (espaces et commentaires ignorés).
        Lève LexicalError sur tout caractère non reconnu.
        """
        tokens: List[Token] = []
        line = 1
        line_start = 0

        for m in self._re.finditer(source_code):
            kind = m.lastgroup
            value = m.group()
            col = m.start() - line_start + 1

            if kind == 'NEWLINE':
                line += 1
                line_start = m.end()

            elif kind in ('WHITESPACE', 'LINE_COMMENT'):
                pass  # ignoré

            elif kind == 'BLOCK_COMMENT':
                # Compter les sauts de ligne à l'intérieur du commentaire
                nl_count = value.count('\n')
                if nl_count:
                    line += nl_count
                    line_start = m.start() + value.rfind('\n') + 1

            elif kind == 'UNKNOWN':
                raise LexicalError(f"Caractère inconnu '{value}'", line, col)

            elif kind == 'STRING':
                tokens.append(StringLiteral(value[1:-1], line, col))

            elif kind == 'NUMBER':
                tokens.append(Number(int(value), line, col))

            elif kind == 'OPERATOR':
                tokens.append(Operator(value, line, col))

            elif kind == 'WORD':
                if value in self.KEYWORDS:
                    tokens.append(Keyword(value, line, col))
                elif value in self.BOOL_LITERALS:
                    tokens.append(BoolLiteral(value == 'true', line, col))
                else:
                    tokens.append(Identifier(value, line, col))

        return tokens

    def format_tokens(self, tokens: List[Token]) -> str:
        """Formate la liste de tokens en une seule chaîne lisible."""
        return '[' + ', '.join(str(t) for t in tokens) + ']'
