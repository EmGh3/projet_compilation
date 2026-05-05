"""
Semantic Analyzer — Phase 3 du compilateur

Améliorations apportées :
  - Détection des variables NON INITIALISÉES (déclarées mais jamais assignées)
  - Support du type bool et des littéraux true/false
  - Support de WhileStmt
  - Support de DeclarationStmt avec initialisation (int x = 5;)
  - Les erreurs indiquent le nom de la variable et le contexte précis
  - Avertissement si une variable est déclarée mais jamais utilisée
"""

from __future__ import annotations
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field

from syntax_analyzer import (
    ASTNode, Program, DeclarationStmt, AssignStmt, IfStmt, WhileStmt,
    Condition, BinaryOp, UnaryOp, Identifier, Number, StringLiteral,
    BoolLiteralNode, Expression,
)

VALID_TYPES = {'int', 'string', 'bool'}

# Opérateurs valides par type pour les conditions
VALID_RELOPS: Dict[str, Set[str]] = {
    'int':    {'>', '<', '==', '!=', '>=', '<='},
    'string': {'==', '!='},
    'bool':   {'==', '!='},
}


# ---------------------------------------------------------------------------
# Table des symboles
# ---------------------------------------------------------------------------

@dataclass
class SymbolInfo:
    name: str
    var_type: str
    scope_level: int
    initialized: bool = False   # True dès qu'une valeur lui est assignée
    used: bool = False           # True dès qu'on la lit dans une expression

    def __str__(self) -> str:
        init = "initialisée" if self.initialized else "NON initialisée"
        return f"{self.name}: {self.var_type} (portée {self.scope_level}, {init})"


class SymbolTable:
    """Pile de portées (scopes). Le scope 0 est global."""

    def __init__(self):
        self.scopes: List[Dict[str, SymbolInfo]] = [{}]
        self.current_scope: int = 0
        # Historique complet pour le rapport final
        self.all_symbols: List[SymbolInfo] = []

    def enter_scope(self):
        self.current_scope += 1
        self.scopes.append({})

    def exit_scope(self) -> List[SymbolInfo]:
        """Quitte la portée courante et retourne les symboles qui y étaient déclarés."""
        exiting = list(self.scopes[-1].values())
        self.scopes.pop()
        self.current_scope -= 1
        return exiting

    def declare(self, name: str, var_type: str, initialized: bool = False) -> bool:
        """Déclare une variable dans la portée courante. False si déjà déclarée."""
        if name in self.scopes[self.current_scope]:
            return False
        info = SymbolInfo(name, var_type, self.current_scope, initialized)
        self.scopes[self.current_scope][name] = info
        self.all_symbols.append(info)
        return True

    def lookup(self, name: str) -> Optional[SymbolInfo]:
        """Cherche la variable de la portée courante vers le scope global."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def mark_initialized(self, name: str):
        """Marque la variable comme initialisée (dans la portée la plus proche)."""
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name].initialized = True
                return

    def mark_used(self, name: str):
        """Marque la variable comme utilisée."""
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name].used = True
                return

    def __str__(self) -> str:
        lines = ["Table des symboles :", "=" * 50]
        for level, scope in enumerate(self.scopes):
            lines.append(f"Portée {level} :")
            if scope:
                for info in scope.values():
                    lines.append(f"  {info}")
            else:
                lines.append("  (vide)")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Erreurs et avertissements
# ---------------------------------------------------------------------------

class SemanticError:
    def __init__(self, message: str, node: Optional[ASTNode] = None):
        self.message = message
        self.node = node

    def __str__(self) -> str:
        return f"Erreur sémantique : {self.message}"


# ---------------------------------------------------------------------------
# Analyseur sémantique
# ---------------------------------------------------------------------------

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors: List[SemanticError] = []
        self.warnings: List[str] = []

    def _error(self, msg: str, node: Optional[ASTNode] = None):
        self.errors.append(SemanticError(msg, node))

    def _warn(self, msg: str):
        self.warnings.append(msg)

    # ------------------------------------------------------------------
    # Point d'entrée
    # ------------------------------------------------------------------

    def analyze(self, ast: Program) -> bool:
        """
        Analyse l'AST. Retourne True si aucune erreur sémantique.
        """
        self.errors.clear()
        self.warnings.clear()
        self._analyze_program(ast)
        self._check_unused_variables()
        return len(self.errors) == 0

    # ------------------------------------------------------------------
    # Nœuds du programme
    # ------------------------------------------------------------------

    def _analyze_program(self, program: Program):
        for stmt in program.statements:
            self._analyze_statement(stmt)

    def _analyze_statement(self, stmt: ASTNode):
        if isinstance(stmt, DeclarationStmt):
            self._analyze_declaration(stmt)
        elif isinstance(stmt, AssignStmt):
            self._analyze_assignment(stmt)
        elif isinstance(stmt, IfStmt):
            self._analyze_if_stmt(stmt)
        elif isinstance(stmt, WhileStmt):
            self._analyze_while_stmt(stmt)
        else:
            self._error(f"Type de nœud inconnu : {type(stmt).__name__}", stmt)

    # --- Déclaration ---
    def _analyze_declaration(self, decl: DeclarationStmt):
        if decl.var_type not in VALID_TYPES:
            self._error(
                f"Type invalide '{decl.var_type}'. Types valides : {', '.join(VALID_TYPES)}",
                decl,
            )

        initialized = False

        if decl.init_expr is not None:
            expr_type = self._infer_type(decl.init_expr)
            if expr_type is not None and expr_type != decl.var_type:
                self._error(
                    f"Initialisation invalide : impossible d'assigner un {expr_type} "
                    f"à '{decl.identifier}' de type {decl.var_type}",
                    decl,
                )
            initialized = (expr_type == decl.var_type)

        if not self.symbol_table.declare(decl.identifier, decl.var_type, initialized):
            self._error(
                f"Variable '{decl.identifier}' déjà déclarée dans cette portée", decl
            )

    # --- Assignation ---
    def _analyze_assignment(self, assign: AssignStmt):
        info = self.symbol_table.lookup(assign.identifier)
        if info is None:
            self._error(
                f"Variable '{assign.identifier}' utilisée avant déclaration", assign
            )
            return

        expr_type = self._infer_type(assign.expression)
        if expr_type is None:
            return  # Erreur déjà signalée dans _infer_type

        if info.var_type != expr_type:
            self._error(
                f"Incompatibilité de types : impossible d'assigner un {expr_type} "
                f"à '{assign.identifier}' de type {info.var_type}",
                assign,
            )
        else:
            self.symbol_table.mark_initialized(assign.identifier)

    # --- If ---
    def _analyze_if_stmt(self, stmt: IfStmt):
        self._analyze_condition(stmt.condition)

        self.symbol_table.enter_scope()
        for s in stmt.body:
            self._analyze_statement(s)
        leaving = self.symbol_table.exit_scope()
        self._warn_uninitialized_in_scope(leaving)

        if stmt.else_body:
            self.symbol_table.enter_scope()
            for s in stmt.else_body:
                self._analyze_statement(s)
            leaving = self.symbol_table.exit_scope()
            self._warn_uninitialized_in_scope(leaving)

    # --- While ---
    def _analyze_while_stmt(self, stmt: WhileStmt):
        self._analyze_condition(stmt.condition)

        self.symbol_table.enter_scope()
        for s in stmt.body:
            self._analyze_statement(s)
        leaving = self.symbol_table.exit_scope()
        self._warn_uninitialized_in_scope(leaving)

    # --- Condition ---
    def _analyze_condition(self, cond: Condition):
        left_type = self._infer_type(cond.left)
        right_type = self._infer_type(cond.right)

        if left_type is None or right_type is None:
            return

        if left_type != right_type:
            self._error(
                f"Incompatibilité dans la condition : comparaison entre {left_type} et {right_type}",
                cond,
            )
            return

        valid_ops = VALID_RELOPS.get(left_type, set())
        if cond.operator not in valid_ops:
            self._error(
                f"Opérateur '{cond.operator}' invalide pour le type {left_type}. "
                f"Opérateurs valides : {', '.join(sorted(valid_ops))}",
                cond,
            )

    # ------------------------------------------------------------------
    # Inférence de type des expressions
    # ------------------------------------------------------------------

    def _infer_type(self, expr: Expression) -> Optional[str]:
        if isinstance(expr, Number):
            return 'int'

        if isinstance(expr, StringLiteral):
            return 'string'

        if isinstance(expr, BoolLiteralNode):
            return 'bool'

        if isinstance(expr, Identifier):
            info = self.symbol_table.lookup(expr.name)
            if info is None:
                self._error(f"Variable '{expr.name}' utilisée avant déclaration", expr)
                return None
            if not info.initialized:
                self._warn(
                    f"Variable '{expr.name}' utilisée avant d'avoir été initialisée"
                )
            self.symbol_table.mark_used(expr.name)
            return info.var_type

        if isinstance(expr, BinaryOp):
            return self._infer_binary_op(expr)

        if isinstance(expr, UnaryOp):
            operand_type = self._infer_type(expr.operand)
            if operand_type != 'int':
                self._error(
                    f"L'opérateur unaire '{expr.op}' requiert un int, obtenu {operand_type}",
                    expr,
                )
                return None
            return 'int'

        self._error(f"Type d'expression inconnu : {type(expr).__name__}", expr)
        return None

    def _infer_binary_op(self, binop: BinaryOp) -> Optional[str]:
        left_t = self._infer_type(binop.left)
        right_t = self._infer_type(binop.right)

        if left_t is None or right_t is None:
            return None

        if binop.op == '+':
            # int + int → int  |  string + string → string (concaténation)
            if left_t == right_t and left_t in ('int', 'string'):
                return left_t
            self._error(
                f"L'opérateur '+' ne peut pas être appliqué à {left_t} et {right_t}. "
                f"Combinaisons valides : int+int, string+string",
                binop,
            )
            return None

        if binop.op in ('-', '*', '/'):
            if left_t == 'int' and right_t == 'int':
                return 'int'
            self._error(
                f"L'opérateur '{binop.op}' requiert deux int, obtenu {left_t} et {right_t}",
                binop,
            )
            return None

        self._error(f"Opérateur binaire inconnu : '{binop.op}'", binop)
        return None

    # ------------------------------------------------------------------
    # Vérifications post-analyse
    # ------------------------------------------------------------------

    def _check_unused_variables(self):
        """Avertit pour toute variable déclarée mais jamais lue."""
        for info in self.symbol_table.all_symbols:
            if not info.used:
                self._warn(
                    f"Variable '{info.name}' déclarée (portée {info.scope_level}) "
                    f"mais jamais utilisée"
                )

    def _warn_uninitialized_in_scope(self, symbols: List[SymbolInfo]):
        """Avertit pour les variables d'une portée sortante non initialisées."""
        for info in symbols:
            if not info.initialized:
                self._warn(
                    f"Variable '{info.name}' (portée {info.scope_level}) "
                    f"déclarée mais jamais initialisée"
                )

    # ------------------------------------------------------------------
    # Rapport
    # ------------------------------------------------------------------

    def get_report(self) -> str:
        lines = [
            "=" * 60,
            "RAPPORT D'ANALYSE SÉMANTIQUE",
            "=" * 60,
            "",
            str(self.symbol_table),
        ]

        if self.errors:
            lines += ["", "ERREURS :", "-" * 60]
            for i, e in enumerate(self.errors, 1):
                lines.append(f"  {i}. {e}")
        else:
            lines.append("\n✓ Aucune erreur sémantique détectée !")

        if self.warnings:
            lines += ["", "AVERTISSEMENTS :", "-" * 60]
            for i, w in enumerate(self.warnings, 1):
                lines.append(f"  {i}. {w}")

        lines += [
            "",
            "=" * 60,
            f"Résumé : {len(self.errors)} erreur(s), {len(self.warnings)} avertissement(s)",
            "=" * 60,
        ]
        return "\n".join(lines)
