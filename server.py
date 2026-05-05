"""
server.py — Backend Flask pour l'IDE web

Lance avec : python server.py
Puis ouvre  : http://localhost:5000
"""

import json
import sys
import os

from flask import Flask, request, jsonify, send_from_directory

# Ajoute le dossier courant au path pour importer les modules du compilateur
sys.path.insert(0, os.path.dirname(__file__))

from lexical_analyzer import Lexer, LexicalError, Token
from syntax_analyzer import (
    RecursiveDescentParser, Program, DeclarationStmt, AssignStmt,
    IfStmt, WhileStmt, BinaryOp, UnaryOp, Identifier, Number,
    StringLiteral, BoolLiteralNode, Condition,
)
from semantic_analyzer import SemanticAnalyzer

app = Flask(__name__, static_folder="static")
lexer = Lexer()


# ---------------------------------------------------------------------------
# Sérialisation de l'AST en JSON pour le visualiseur
# ---------------------------------------------------------------------------

def ast_to_dict(node) -> dict:
    """Convertit récursivement un nœud AST en dict JSON-sérialisable."""
    if node is None:
        return None

    if isinstance(node, Program):
        return {
            "type": "Program",
            "children": [ast_to_dict(s) for s in node.statements],
        }
    if isinstance(node, DeclarationStmt):
        d = {"type": "Déclaration", "label": f"{node.var_type} {node.identifier}"}
        if node.init_expr:
            d["children"] = [ast_to_dict(node.init_expr)]
        return d
    if isinstance(node, AssignStmt):
        return {
            "type": "Assignation",
            "label": f"{node.identifier} =",
            "children": [ast_to_dict(node.expression)],
        }
    if isinstance(node, IfStmt):
        d = {
            "type": "If",
            "label": "if",
            "children": [
                {"type": "Condition", "label": str(node.condition)},
                {"type": "Bloc then", "label": "then", "children": [ast_to_dict(s) for s in node.body]},
            ],
        }
        if node.else_body:
            d["children"].append({
                "type": "Bloc else",
                "label": "else",
                "children": [ast_to_dict(s) for s in node.else_body],
            })
        return d
    if isinstance(node, WhileStmt):
        return {
            "type": "While",
            "label": "while",
            "children": [
                {"type": "Condition", "label": str(node.condition)},
                {"type": "Corps", "label": "body", "children": [ast_to_dict(s) for s in node.body]},
            ],
        }
    if isinstance(node, BinaryOp):
        return {
            "type": "BinaryOp",
            "label": node.op,
            "children": [ast_to_dict(node.left), ast_to_dict(node.right)],
        }
    if isinstance(node, UnaryOp):
        return {
            "type": "UnaryOp",
            "label": node.op,
            "children": [ast_to_dict(node.operand)],
        }
    if isinstance(node, Identifier):
        return {"type": "Identifiant", "label": node.name}
    if isinstance(node, Number):
        return {"type": "Nombre", "label": str(node.value)}
    if isinstance(node, StringLiteral):
        return {"type": "String", "label": f'"{node.value}"'}
    if isinstance(node, BoolLiteralNode):
        return {"type": "Bool", "label": "true" if node.value else "false"}

    return {"type": type(node).__name__, "label": str(node)}


# ---------------------------------------------------------------------------
# Routes API
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/compile", methods=["POST"])
def compile_code():
    data = request.get_json()
    source = data.get("code", "")

    result = {
        "lexer":    {"ok": False, "tokens": [], "error": None},
        "parser":   {"ok": False, "ast": None, "errors": []},
        "semantic": {"ok": False, "symbols": [], "errors": [], "warnings": []},
    }

    # ---- Phase 1 : Lexer -----------------------------------------------
    try:
        tokens = lexer.tokenize(source)
        result["lexer"]["ok"] = True
        result["lexer"]["tokens"] = [
            {
                "index": i + 1,
                "repr":  str(t),
                "type":  t.token_type,
                "line":  t.line,
                "col":   t.col,
            }
            for i, t in enumerate(tokens)
        ]
    except LexicalError as e:
        result["lexer"]["error"] = str(e)
        return jsonify(result)

    # ---- Phase 2 : Parser ----------------------------------------------
    parser = RecursiveDescentParser(tokens)
    ast = parser.parse()

    if ast and not parser.errors:
        result["parser"]["ok"] = True
        result["parser"]["ast"] = ast_to_dict(ast)
    else:
        result["parser"]["errors"] = [str(e) for e in parser.errors]
        return jsonify(result)

    # ---- Phase 3 : Sémantique ------------------------------------------
    analyzer = SemanticAnalyzer()
    ok = analyzer.analyze(ast)
    result["semantic"]["ok"] = ok
    result["semantic"]["errors"]   = [str(e) for e in analyzer.errors]
    result["semantic"]["warnings"] = analyzer.warnings

    # Table des symboles sérialisée
    for scope_idx, scope in enumerate(analyzer.symbol_table.scopes):
        for info in scope.values():
            result["semantic"]["symbols"].append({
                "name":        info.name,
                "type":        info.var_type,
                "scope":       info.scope_level,
                "initialized": info.initialized,
                "used":        info.used,
            })

    return jsonify(result)


if __name__ == "__main__":
    print("=" * 60)
    print("  IDE Compilateur — http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, port=5000)
