from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from syntax_analyzer import (
    ASTNode, Program, DeclarationStmt, AssignStmt, IfStmt,
    Condition, BinaryOp, Identifier, Number, StringLiteral, Expression
)


@dataclass
class SymbolInfo:
    """Information about a symbol in the symbol table"""
    name: str
    var_type: str
    scope_level: int
    declared_line: int = 0

    def __str__(self):
        return f"{self.name}: {self.var_type} (scope {self.scope_level})"


class SymbolTable:
    """Symbol table for managing variable declarations and scopes"""

    def __init__(self):
        self.scopes: List[Dict[str, SymbolInfo]] = [{}]  # Stack of scopes
        self.current_scope = 0
        self.all_symbols: List[SymbolInfo] = []  # All symbols ever declared

    def enter_scope(self):
        """Enter a new scope (e.g., entering an if-then-else block)"""
        self.current_scope += 1
        self.scopes.append({})

    def exit_scope(self):
        """Exit the current scope"""
        if self.current_scope > 0:
            self.scopes.pop()
            self.current_scope -= 1

    def declare(self, name: str, var_type: str, line: int = 0) -> bool:
        """
        Declare a variable in the current scope.
        Returns True if successful, False if already declared in current scope.
        """
        current_scope_table = self.scopes[self.current_scope]

        if name in current_scope_table:
            return False  # Already declared in this scope

        symbol = SymbolInfo(name, var_type, self.current_scope, line)
        current_scope_table[name] = symbol
        self.all_symbols.append(symbol)
        return True

    def lookup(self, name: str) -> Optional[SymbolInfo]:
        """
        Look up a variable in the current scope and all parent scopes.
        Returns SymbolInfo if found, None otherwise.
        """
        # Search from current scope up to global scope
        for scope_level in range(self.current_scope, -1, -1):
            if name in self.scopes[scope_level]:
                return self.scopes[scope_level][name]
        return None

    def is_declared(self, name: str) -> bool:
        """Check if a variable is declared in any accessible scope"""
        return self.lookup(name) is not None

    def get_type(self, name: str) -> Optional[str]:
        """Get the type of a variable"""
        symbol = self.lookup(name)
        return symbol.var_type if symbol else None

    def __str__(self):
        """String representation of the symbol table"""
        result = "Symbol Table:\n"
        result += "=" * 50 + "\n"
        for scope_level, scope in enumerate(self.scopes):
            result += f"Scope {scope_level}:\n"
            if scope:
                for name, info in scope.items():
                    result += f"  {info}\n"
            else:
                result += "  (empty)\n"
        return result


class SemanticError:
    """Represents a semantic error found during analysis"""

    def __init__(self, message: str, node: Optional[ASTNode] = None):
        self.message = message
        self.node = node

    def __str__(self):
        return f"Semantic Error: {self.message}"


class SemanticAnalyzer:
    """
    Semantic analyzer that performs:
    - Type checking
    - Scope resolution
    - Variable declaration checking
    - Expression type validation
    """

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors: List[SemanticError] = []
        self.warnings: List[str] = []

    def add_error(self, message: str, node: Optional[ASTNode] = None):
        """Add a semantic error"""
        self.errors.append(SemanticError(message, node))

    def add_warning(self, message: str):
        """Add a warning message"""
        self.warnings.append(message)

    def analyze(self, ast: Program) -> bool:
        """
        Analyze the AST for semantic errors.
        Returns True if no errors found, False otherwise.
        """
        self.errors = []
        self.warnings = []

        # Analyze the program
        self.analyze_program(ast)

        return len(self.errors) == 0

    def analyze_program(self, program: Program):
        """Analyze the entire program"""
        for statement in program.statements:
            self.analyze_statement(statement)

    def analyze_statement(self, stmt: ASTNode):
        """Analyze a single statement"""
        if isinstance(stmt, DeclarationStmt):
            self.analyze_declaration(stmt)
        elif isinstance(stmt, AssignStmt):
            self.analyze_assignment(stmt)
        elif isinstance(stmt, IfStmt):
            self.analyze_if_stmt(stmt)
        else:
            self.add_error(f"Unknown statement type: {type(stmt).__name__}", stmt)

    def analyze_declaration(self, decl: DeclarationStmt):
        """Analyze a variable declaration"""
        # Check if type is valid
        if decl.var_type not in ['int', 'string']:
            self.add_error(
                f"Invalid type '{decl.var_type}'. Valid types are: int, string",
                decl
            )

        # Check if variable is already declared in current scope
        if not self.symbol_table.declare(decl.identifier, decl.var_type):
            self.add_error(
                f"Variable '{decl.identifier}' is already declared in the current scope",
                decl
            )

    def analyze_assignment(self, assign: AssignStmt):
        """Analyze an assignment statement"""
        # Check if variable is declared
        if not self.symbol_table.is_declared(assign.identifier):
            self.add_error(
                f"Variable '{assign.identifier}' is used before declaration",
                assign
            )
            return

        # Get the variable's declared type
        var_type = self.symbol_table.get_type(assign.identifier)

        # Get the expression's type
        expr_type = self.infer_expression_type(assign.expression)

        if expr_type is None:
            return  # Error already reported in expression analysis

        # Check type compatibility
        if var_type != expr_type:
            self.add_error(
                f"Type mismatch: Cannot assign {expr_type} to variable '{assign.identifier}' of type {var_type}",
                assign
            )

    def analyze_if_stmt(self, if_stmt: IfStmt):
        """Analyze an if-then-else statement"""
        # Analyze the condition
        self.analyze_condition(if_stmt.condition)

        # Enter new scope for then body
        self.symbol_table.enter_scope()
        for stmt in if_stmt.body:
            self.analyze_statement(stmt)
        self.symbol_table.exit_scope()

        # Enter new scope for else body if it exists
        if if_stmt.else_body:
            self.symbol_table.enter_scope()
            for stmt in if_stmt.else_body:
                self.analyze_statement(stmt)
            self.symbol_table.exit_scope()

    def analyze_condition(self, condition: Condition):
        """Analyze a condition in an if statement"""
        # Get types of left and right expressions
        left_type = self.infer_expression_type(condition.left)
        right_type = self.infer_expression_type(condition.right)

        if left_type is None or right_type is None:
            return  # Error already reported

        # Check that both sides have compatible types
        if left_type != right_type:
            self.add_error(
                f"Type mismatch in condition: comparing {left_type} with {right_type}",
                condition
            )

        # Check that the operator is valid for the types
        valid_ops = {
            'int': ['>', '<', '==', '!=', '>=', '<='],
            'string': ['==', '!=']
        }

        if condition.operator not in valid_ops.get(left_type, []):
            self.add_error(
                f"Invalid operator '{condition.operator}' for type {left_type}",
                condition
            )

    def infer_expression_type(self, expr: Expression) -> Optional[str]:
        """
        Infer the type of an expression.
        Returns 'int', 'string', or None if type cannot be determined.
        """
        if isinstance(expr, Number):
            return 'int'

        elif isinstance(expr, StringLiteral):
            return 'string'

        elif isinstance(expr, Identifier):
            # Look up the variable's type
            if not self.symbol_table.is_declared(expr.name):
                self.add_error(
                    f"Variable '{expr.name}' is used before declaration",
                    expr
                )
                return None
            return self.symbol_table.get_type(expr.name)

        elif isinstance(expr, BinaryOp):
            return self.analyze_binary_op(expr)

        else:
            self.add_error(f"Unknown expression type: {type(expr).__name__}", expr)
            return None

    def analyze_binary_op(self, binop: BinaryOp) -> Optional[str]:
        """Analyze a binary operation and return its result type"""
        # Get types of operands
        left_type = self.infer_expression_type(binop.left)
        right_type = self.infer_expression_type(binop.right)

        if left_type is None or right_type is None:
            return None  # Error already reported

        # Check type compatibility for the operation
        if binop.op in ['+', '-', '*', '/']:
            # Arithmetic operations
            if binop.op == '+':
                # Addition can work on both int and string (concatenation)
                if left_type == right_type:
                    return left_type
                else:
                    self.add_error(
                        f"Type mismatch in binary operation: cannot perform '{binop.op}' on {left_type} and {right_type}",
                        binop
                    )
                    return None
            else:
                # Subtraction, multiplication, division only work on int
                if left_type == 'int' and right_type == 'int':
                    return 'int'
                else:
                    self.add_error(
                        f"Invalid operation: '{binop.op}' requires int operands, got {left_type} and {right_type}",
                        binop
                    )
                    return None
        else:
            self.add_error(f"Unknown binary operator: {binop.op}", binop)
            return None

    def get_report(self) -> str:
        """Generate a detailed analysis report"""
        report = []
        report.append("=" * 60)
        report.append("SEMANTIC ANALYSIS REPORT")
        report.append("=" * 60)

        # Symbol table
        report.append("\n" + str(self.symbol_table))

        # Errors
        if self.errors:
            report.append("\nERRORS FOUND:")
            report.append("-" * 60)
            for i, error in enumerate(self.errors, 1):
                report.append(f"{i}. {error}")
        else:
            report.append("\n✓ No semantic errors found!")

        # Warnings
        if self.warnings:
            report.append("\nWARNINGS:")
            report.append("-" * 60)
            for i, warning in enumerate(self.warnings, 1):
                report.append(f"{i}. {warning}")

        report.append("\n" + "=" * 60)
        report.append(f"Summary: {len(self.errors)} error(s), {len(self.warnings)} warning(s)")
        report.append("=" * 60)

        return "\n".join(report)
