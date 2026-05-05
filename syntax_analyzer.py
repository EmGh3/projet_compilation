"""
Syntax Analyzer — Phase 2 du compilateur (Recursive Descent Parser)

Améliorations apportées :
  - ParserToken supprimé : on utilise directement isinstance() sur les tokens du Lexer
  - Numéros de ligne dans chaque erreur de parsing
  - Nouvelle instruction : while (condition) { ... }
  - Déclaration avec initialisation : int x = 5;  string s = "hello";
  - Expressions parenthésées : (x + 1) * 2
  - Type bool et littéraux true/false
  - Récupération d'erreurs améliorée (synchronisation sur ';' et '}')

Grammaire :
  <program>      ::= <statement_list>
  <stmt_list>    ::= <statement> <stmt_list> | ε
  <statement>    ::= <declaration> | <assignment> | <if_stmt> | <while_stmt>
  <declaration>  ::= <type> <id> [ = <expression> ] ;
  <assignment>   ::= <id> = <expression> ;
  <if_stmt>      ::= if ( <condition> ) then { <stmt_list> } [ else { <stmt_list> } ]
  <while_stmt>   ::= while ( <condition> ) { <stmt_list> }
  <condition>    ::= <expression> <relop> <expression>
  <expression>   ::= <term> { <binop> <term> }
  <term>         ::= <id> | <number> | <string> | <bool> | ( <expression> ) | - <number>
  <type>         ::= int | string | bool
  <relop>        ::= <= | >= | > | < | == | !=
  <binop>        ::= + | - | * | /
"""

from __future__ import annotations
from typing import List, Optional, Union
from dataclasses import dataclass, field

from lexical_analyzer import (
    Token, Keyword, Identifier as LexIdent, Number as LexNumber,
    Operator, StringLiteral as LexString, BoolLiteral,
)


# ---------------------------------------------------------------------------
# Nœuds de l'AST
# ---------------------------------------------------------------------------

@dataclass
class ASTNode:
    """Classe de base pour tous les nœuds de l'AST."""
    pass


@dataclass
class Program(ASTNode):
    statements: List[ASTNode]

    def __str__(self, indent: int = 0) -> str:
        pad = "  " * indent
        lines = [f"{pad}Program"]
        for s in self.statements:
            if hasattr(s, '__str__') and 'indent' in s.__str__.__code__.co_varnames:
                lines.append(s.__str__(indent + 1))
            else:
                lines.append("  " * (indent + 1) + str(s))
        return "\n".join(lines)


@dataclass
class DeclarationStmt(ASTNode):
    """int x;  ou  int x = 5;"""
    var_type: str
    identifier: str
    init_expr: Optional['Expression'] = None  # optionnel : valeur initiale

    def __str__(self) -> str:
        if self.init_expr:
            return f"DeclStmt({self.var_type}, {self.identifier} = {self.init_expr})"
        return f"DeclStmt({self.var_type}, {self.identifier})"


@dataclass
class AssignStmt(ASTNode):
    identifier: str
    expression: 'Expression'

    def __str__(self) -> str:
        return f"AssignStmt({self.identifier}, {self.expression})"


@dataclass
class IfStmt(ASTNode):
    condition: 'Condition'
    body: List[ASTNode]
    else_body: Optional[List[ASTNode]] = None

    def __str__(self, indent: int = 0) -> str:
        pad = "  " * indent
        lines = [f"{pad}IfStmt({self.condition})"]
        for s in self.body:
            lines.append("  " * (indent + 1) + str(s))
        if self.else_body:
            lines.append(f"{pad}  Else")
            for s in self.else_body:
                lines.append("  " * (indent + 1) + str(s))
        return "\n".join(lines)


@dataclass
class WhileStmt(ASTNode):
    """while (condition) { stmt_list }"""
    condition: 'Condition'
    body: List[ASTNode]

    def __str__(self, indent: int = 0) -> str:
        pad = "  " * indent
        lines = [f"{pad}WhileStmt({self.condition})"]
        for s in self.body:
            lines.append("  " * (indent + 1) + str(s))
        return "\n".join(lines)


@dataclass
class Condition(ASTNode):
    left: 'Expression'
    operator: str
    right: 'Expression'

    def __str__(self) -> str:
        return f"Condition({self.left} {self.operator} {self.right})"


@dataclass
class BinaryOp(ASTNode):
    op: str
    left: 'Expression'
    right: 'Expression'

    def __str__(self) -> str:
        return f"BinaryOp({self.op}, {self.left}, {self.right})"


@dataclass
class UnaryOp(ASTNode):
    op: str
    operand: 'Expression'

    def __str__(self) -> str:
        return f"UnaryOp({self.op}, {self.operand})"


@dataclass
class Identifier(ASTNode):
    name: str

    def __str__(self) -> str:
        return f"ID({self.name})"


@dataclass
class Number(ASTNode):
    value: int

    def __str__(self) -> str:
        return f"Num({self.value})"


@dataclass
class StringLiteral(ASTNode):
    value: str

    def __str__(self) -> str:
        return f'String("{self.value}")'


@dataclass
class BoolLiteralNode(ASTNode):
    value: bool

    def __str__(self) -> str:
        return f"Bool({'true' if self.value else 'false'})"


Expression = Union[BinaryOp, UnaryOp, Identifier, Number, StringLiteral, BoolLiteralNode]

# Opérateurs relationnels et arithmétiques
RELOPS = {'>', '<', '==', '!=', '>=', '<='}
BINOPS = {'+', '-', '*', '/'}
TYPES  = {'int', 'string', 'bool'}


# ---------------------------------------------------------------------------
# Erreur de parsing
# ---------------------------------------------------------------------------

class ParseError:
    def __init__(self, message: str, line: int, col: int):
        self.message = message
        self.line = line
        self.col = col

    def __str__(self) -> str:
        return f"Erreur syntaxique à la ligne {self.line}, col {self.col} : {self.message}"


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class RecursiveDescentParser:
    """
    Parser par descente récursive.
    Utilise directement isinstance() sur les tokens du Lexer — aucun
    re-parsing par représentation textuelle.
    """

    def __init__(self, tokens: List[Token]):
        # Filtre défensif : on ne garde que les vrais tokens
        self.tokens = [t for t in tokens if isinstance(t, Token)]
        self.pos = 0
        self.errors: List[ParseError] = []

    # ------------------------------------------------------------------
    # Helpers de navigation
    # ------------------------------------------------------------------

    def _cur(self) -> Optional[Token]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _peek_next(self) -> Optional[Token]:
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return None

    def _advance(self) -> Optional[Token]:
        tok = self._cur()
        self.pos += 1
        return tok

    def _at_end(self) -> bool:
        return self.pos >= len(self.tokens)

    # Vérification de type + valeur sans toucher à str()
    def _is_keyword(self, value: str) -> bool:
        t = self._cur()
        return isinstance(t, Keyword) and t.value == value

    def _is_type_keyword(self) -> bool:
        t = self._cur()
        return isinstance(t, Keyword) and t.value in TYPES

    def _is_operator(self, symbol: str) -> bool:
        t = self._cur()
        return isinstance(t, Operator) and t.symbol == symbol

    def _is_relop(self) -> bool:
        t = self._cur()
        return isinstance(t, Operator) and t.symbol in RELOPS

    def _is_binop(self) -> bool:
        t = self._cur()
        return isinstance(t, Operator) and t.symbol in BINOPS

    def _pos_info(self) -> tuple:
        """Retourne (line, col) du token courant."""
        t = self._cur()
        if t:
            return t.line, t.col
        return 0, 0

    # ------------------------------------------------------------------
    # Gestion des erreurs + récupération
    # ------------------------------------------------------------------

    def _error(self, msg: str):
        line, col = self._pos_info()
        self.errors.append(ParseError(msg, line, col))

    def _consume_keyword(self, value: str) -> bool:
        if self._is_keyword(value):
            self._advance()
            return True
        t = self._cur()
        got = str(t) if t else "fin de fichier"
        self._error(f"Mot-clé '{value}' attendu, obtenu {got}")
        return False

    def _consume_operator(self, symbol: str, context: str = "") -> bool:
        if self._is_operator(symbol):
            self._advance()
            return True
        t = self._cur()
        got = str(t) if t else "fin de fichier"
        if symbol == ';':
            ctx = f" après {context}" if context else ""
            self._error(f"';' manquant{ctx} — obtenu {got}")
        else:
            self._error(f"Opérateur '{symbol}' attendu, obtenu {got}")
        return False

    def _consume_identifier(self) -> Optional[str]:
        t = self._cur()
        if isinstance(t, LexIdent):
            self._advance()
            return t.name
        got = str(t) if t else "fin de fichier"
        self._error(f"Identifiant attendu, obtenu {got}")
        return None

    def _synchronize(self):
        """
        Récupération d'erreur après un ';' manquant.
        - Consomme les tokens jusqu'à trouver ';' (qu'il consomme aussi).
        - S'arrête DEVANT '}' sans le consommer, pour ne pas briser la
          structure des blocs if/else/while en cours de parsing.
        """
        while not self._at_end():
            t = self._cur()
            if isinstance(t, Operator) and t.symbol == ';':
                self._advance()   # consomme le ';', on peut reprendre
                return
            if isinstance(t, Operator) and t.symbol == '}':
                return            # on s'arrête AVANT le '}', sans le toucher
            self._advance()

    # ------------------------------------------------------------------
    # Point d'entrée
    # ------------------------------------------------------------------

    def parse(self) -> Optional[Program]:
        stmts = self._parse_statement_list()
        if self.errors:
            return None
        return Program(stmts)

    # ------------------------------------------------------------------
    # Règles grammaticales
    # ------------------------------------------------------------------

    def _parse_statement_list(self, stop_on_rbrace: bool = False) -> List[ASTNode]:
        stmts = []
        while not self._at_end():
            t = self._cur()
            if stop_on_rbrace and isinstance(t, Operator) and t.symbol == '}':
                break
            stmt = self._parse_statement()
            if stmt is not None:
                stmts.append(stmt)
        return stmts

    def _parse_statement(self) -> Optional[ASTNode]:
        t = self._cur()

        if t is None:
            return None

        # Déclaration : int | string | bool
        if self._is_type_keyword():
            return self._parse_declaration()

        # If
        if self._is_keyword('if'):
            return self._parse_if_stmt()

        # While
        if self._is_keyword('while'):
            return self._parse_while_stmt()

        # Assignation
        if isinstance(t, LexIdent):
            return self._parse_assignment()

        self._error(f"Instruction inattendue : {t}")
        self._synchronize()
        return None

    # --- Déclaration : <type> <id> [ = <expr> ] ; ---
    def _parse_declaration(self) -> Optional[DeclarationStmt]:
        type_tok = self._advance()   # consomme le mot-clé de type
        var_type = type_tok.value

        name = self._consume_identifier()
        if name is None:
            self._synchronize()
            return None

        init_expr = None
        # Initialisation optionnelle : = <expr>
        if self._is_operator('='):
            self._advance()  # consomme '='
            init_expr = self._parse_expression()

        if not self._consume_operator(';', f"la déclaration de '{name}'"):
            self._synchronize()
        return DeclarationStmt(var_type, name, init_expr)

    # --- Assignation : <id> = <expr> ; ---
    def _parse_assignment(self) -> Optional[AssignStmt]:
        name = self._consume_identifier()
        if name is None:
            self._synchronize()
            return None

        if not self._consume_operator('='):
            self._synchronize()
            return None

        expr = self._parse_expression()
        if expr is None:
            self._synchronize()
            return None

        if not self._consume_operator(';', f"l'assignation de '{name}'"):
            self._synchronize()
        return AssignStmt(name, expr)

    # --- If : if ( <cond> ) then { <stmts> } [ else { <stmts> } ] ---
    def _parse_if_stmt(self) -> Optional[IfStmt]:
        self._consume_keyword('if')

        if not self._consume_operator('('):
            self._synchronize(); return None
        cond = self._parse_condition()
        if cond is None:
            self._synchronize(); return None
        if not self._consume_operator(')'):
            self._synchronize(); return None

        self._consume_keyword('then')

        if not self._consume_operator('{'):
            self._synchronize(); return None
        body = self._parse_statement_list(stop_on_rbrace=True)
        if not self._consume_operator('}'):
            self._synchronize(); return None

        else_body = None
        if self._is_keyword('else'):
            self._advance()
            if not self._consume_operator('{'):
                self._synchronize(); return None
            else_body = self._parse_statement_list(stop_on_rbrace=True)
            if not self._consume_operator('}'):
                self._synchronize()

        return IfStmt(cond, body, else_body)

    # --- While : while ( <cond> ) { <stmts> } ---
    def _parse_while_stmt(self) -> Optional[WhileStmt]:
        self._consume_keyword('while')

        # Au lieu de return None direct, on signale juste l'erreur
        if not self._consume_operator('('):
            # On ne s'arrête pas forcément ici, on tente de parser la condition quand même
            pass 

        cond = self._parse_condition()
        
        if not self._consume_operator(')'):
            pass

        if not self._consume_operator('{'):
            self._synchronize() # On synchronise seulement si on ne trouve pas le début du bloc
            return None

        body = self._parse_statement_list(stop_on_rbrace=True)
        self._consume_operator('}')

        return WhileStmt(cond, body)

    # --- Condition : <expr> <relop> <expr>  |  <bool_expr> ---
    def _parse_condition(self) -> Optional[Condition]:
        left = self._parse_expression()
        if left is None:
            return None

        # Condition booléenne seule : while (true) / while (actif) / if (b) then
        # Si le prochain token est ')' sans relop → condition implicite == true
        if not self._is_relop():
            t = self._cur()
            if isinstance(t, Operator) and t.symbol == ')':
                return Condition(left, '==', BoolLiteralNode(True))
            self._error(f"Opérateur relationnel attendu, obtenu {t}")
            return None

        op = self._cur().symbol
        self._advance()

        right = self._parse_expression()
        if right is None:
            return None

        return Condition(left, op, right)

    # --- Expression : <term> { <binop> <term> } ---
    def _parse_expression(self) -> Optional[Expression]:
        left = self._parse_term()
        if left is None:
            return None

        while self._is_binop():
            op = self._cur().symbol
            self._advance()
            right = self._parse_term()
            if right is None:
                break
            left = BinaryOp(op, left, right)

        return left

    # --- Term : id | number | string | bool | ( expr ) | - number ---
    def _parse_term(self) -> Optional[Expression]:
        t = self._cur()

        if t is None:
            self._error("Expression attendue, fin de fichier atteinte")
            return None

        # Négatif unaire : - <number>
        if isinstance(t, Operator) and t.symbol == '-':
            next_t = self._peek_next()
            if isinstance(next_t, LexNumber):
                self._advance()       # consomme '-'
                num = self._advance() # consomme le nombre
                return Number(-num.value)
            else:
                self._error(f"Nombre attendu après '-', obtenu {next_t}")
                self._advance()
                return None

        # Expression parenthésée : ( expr )
        if isinstance(t, Operator) and t.symbol == '(':
            self._advance()  # consomme '('
            expr = self._parse_expression()
            if not self._consume_operator(')'):
                self._synchronize()
            return expr

        if isinstance(t, LexIdent):
            self._advance()
            return Identifier(t.name)

        if isinstance(t, LexNumber):
            self._advance()
            return Number(t.value)

        if isinstance(t, LexString):
            self._advance()
            return StringLiteral(t.value)

        if isinstance(t, BoolLiteral):
            self._advance()
            return BoolLiteralNode(t.value)

        # Tokens structurels : jamais une expression valide
        if isinstance(t, Operator) and t.symbol in ('}', '{', ';', ')'):
            self._error(
                f"Expression attendue à la ligne {t.line}, col {t.col} "
                f"— '{t.symbol}' n'est pas une valeur valide"
            )
            return None  # NE PAS consommer le token structurel

        self._error(f"Terme inattendu : {t}")
        self._advance()
        return None