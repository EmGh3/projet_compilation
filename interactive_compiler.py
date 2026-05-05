"""
Interactive Compiler — Frontend interactif du compilateur

Améliorations apportées :
  - Affichage des erreurs avec numéros de ligne et colonne
  - Erreurs lexicales capturées proprement
  - Résumé clair des trois phases
  - Option pour afficher ou masquer les tokens
  - Exemple de programmes intégrés pour démonstration
"""

import sys
from lexical_analyzer import Lexer, LexicalError
from syntax_analyzer import RecursiveDescentParser, Program
from semantic_analyzer import SemanticAnalyzer


# ---------------------------------------------------------------------------
# Exemples intégrés
# ---------------------------------------------------------------------------

EXAMPLES = {
    "1": (
        "Déclarations et arithmétique",
        """\
int x = 10;
int y = 3;
int result = x + y;
""",
    ),
    "2": (
        "If / else avec comparaison de chaînes",
        """\
string nom = "Alice";
string message;
if (nom == "Alice") then {
    message = "Bonjour Alice !";
} else {
    message = "Qui es-tu ?";
}
""",
    ),
    "3": (
        "Boucle while",
        """\
int compteur = 0;
int total = 0;
while (compteur < 5) {
    total = total + compteur;
    compteur = compteur + 1;
}
""",
    ),
    "4": (
        "Variable non initialisée (avertissement)",
        """\
int a;
int b = a + 1;
""",
    ),
    "5": (
        "Erreur de type",
        """\
int x = 5;
string s = "hello";
x = s;
""",
    ),
    "6": (
        "Expressions parenthésées",
        """\
int a = 2;
int b = 3;
int c = (a + b) * (a - b);
""",
    ),
    "7": (
        "Booléens et comparaison",
        """\
bool actif = true;
int score = 42;
if (score > 40) then {
    actif = false;
}
""",
    ),
    "8": (
        "Commentaires dans le code",
        """\
// Calcul du maximum de deux entiers
int a = 10;
int b = 20;
int max = a;

/* Si b est plus grand, on prend b */
if (b > a) then {
    max = b;
}
""",
    ),
}


# ---------------------------------------------------------------------------
# Compilateur interactif
# ---------------------------------------------------------------------------

class InteractiveCompiler:

    def __init__(self):
        self.lexer = Lexer()
        self.show_tokens = True

    # ------------------------------------------------------------------
    def print_banner(self):
        print("=" * 70)
        print(" " * 15 + "COMPILATEUR INTERACTIF — FRONTEND")
        print("=" * 70)
        print("""
Phases d'analyse :
  1. Analyse Lexicale   — Tokenisation du code source
  2. Analyse Syntaxique — Construction de l'AST
  3. Analyse Sémantique — Vérification des types et des portées

Fonctionnalités du langage :
  • Déclarations    : int x;  string s;  bool b;
  • Initialisation  : int x = 5;  string s = "hello";
  • Assignation     : x = x + 1;
  • Arithmétique    : +  -  *  /  (entiers)
  • Concaténation   : +  (chaînes)
  • Comparaisons    : ==  !=  <  >  <=  >=
  • Booléens        : true  false
  • Conditions      : if (cond) then { ... } else { ... }
  • Boucles         : while (cond) { ... }
  • Expressions ()  : (a + b) * c
  • Commentaires    : // ligne   /* bloc */
""")
        print("=" * 70)

    def print_help(self):
        print("""
Commandes disponibles :
  code      — Saisir du code multi-lignes (terminer avec 'run')
  exemple   — Choisir un programme exemple
  tokens    — Activer/désactiver l'affichage des tokens
  aide      — Afficher cette aide
  quitter   — Quitter le programme
""")

    # ------------------------------------------------------------------
    def get_multiline_input(self):
        print("\nSaisissez votre code (tapez 'run' sur une ligne pour exécuter, 'annuler' pour abandonner) :")
        print("-" * 70)
        lines = []
        n = 1
        try:
            while True:
                try:
                    line = input(f"{n:3d} | ")
                except EOFError:
                    break
                if line.strip().lower() == 'run':
                    break
                if line.strip().lower() == 'annuler':
                    print("Saisie annulée.")
                    return None
                lines.append(line)
                n += 1
        except KeyboardInterrupt:
            print("\nSaisie annulée.")
            return None
        code = "\n".join(lines)
        return code if code.strip() else None

    def choose_example(self):
        print("\nExemples disponibles :")
        for key, (title, _) in EXAMPLES.items():
            print(f"  {key}. {title}")
        choice = input("\nNuméro de l'exemple : ").strip()
        if choice in EXAMPLES:
            title, code = EXAMPLES[choice]
            print(f"\n--- {title} ---")
            print(code)
            return code
        print("Exemple inconnu.")
        return None

    # ------------------------------------------------------------------
    def analyze(self, code: str):
        """Lance les trois phases d'analyse et affiche les résultats."""
        print("\n" + "=" * 70)
        print("RÉSULTATS DE LA COMPILATION")
        print("=" * 70)

        # ---- Phase 1 : Analyse Lexicale --------------------------------
        print("\n[PHASE 1 : ANALYSE LEXICALE]")
        print("-" * 70)

        try:
            tokens = self.lexer.tokenize(code)
            print(f"✓ Succès — {len(tokens)} token(s) générés")
            if self.show_tokens:
                print("\nTokens :")
                for i, tok in enumerate(tokens, 1):
                    loc = f"ligne {tok.line}, col {tok.col}"
                    print(f"  {i:3d}. {str(tok):<30}  [{loc}]")
            lexical_ok = True
        except LexicalError as e:
            print(f"✗ Échec — {e}")
            print("\n" + "=" * 70)
            print("❌ COMPILATION ÉCHOUÉE — Phase 1")
            print("=" * 70)
            return

        # ---- Phase 2 : Analyse Syntaxique ------------------------------
        print("\n" + "=" * 70)
        print("[PHASE 2 : ANALYSE SYNTAXIQUE]")
        print("-" * 70)

        parser = RecursiveDescentParser(tokens)
        ast = parser.parse()

        if ast and not parser.errors:
            print("✓ Succès — AST construit")
            print("\nArbre Syntaxique Abstrait (AST) :")
            print(ast)
            syntax_ok = True
        else:
            print("✗ Échec — Erreurs syntaxiques :")
            for err in parser.errors:
                print(f"  • {err}")
            print("\n" + "=" * 70)
            print("❌ COMPILATION ÉCHOUÉE — Phase 2")
            print("=" * 70)
            return

        # ---- Phase 3 : Analyse Sémantique ------------------------------
        print("\n" + "=" * 70)
        print("[PHASE 3 : ANALYSE SÉMANTIQUE]")
        print("-" * 70)

        analyzer = SemanticAnalyzer()
        semantic_ok = analyzer.analyze(ast)

        print(str(analyzer.symbol_table))

        if analyzer.warnings:
            print("\nAVERTISSEMENTS :")
            for i, w in enumerate(analyzer.warnings, 1):
                print(f"  {i}. ⚠  {w}")

        if semantic_ok:
            print("\n✓ Succès — Aucune erreur sémantique")
        else:
            print("\n✗ Échec — Erreurs sémantiques :")
            for i, e in enumerate(analyzer.errors, 1):
                print(f"  {i}. {e}")

        # ---- Résumé final ----------------------------------------------
        print("\n" + "=" * 70)
        if semantic_ok:
            print("✅ COMPILATION RÉUSSIE")
            print("  ✓ Analyse lexicale    — OK")
            print("  ✓ Analyse syntaxique  — OK")
            print("  ✓ Analyse sémantique  — OK")
        else:
            print("❌ COMPILATION ÉCHOUÉE — Phase 3")
            print("  ✓ Analyse lexicale    — OK")
            print("  ✓ Analyse syntaxique  — OK")
            print("  ✗ Analyse sémantique  — ÉCHEC")
        print("=" * 70 + "\n")

    # ------------------------------------------------------------------
    def run(self):
        self.print_banner()

        while True:
            try:
                print("\nOptions : code | exemple | tokens | aide | quitter")
                cmd = input(">>> ").strip()

                # Comparaison des commandes en minuscules, mais la casse
                # du code source est PRÉSERVÉE pour l'analyse
                cmd_lower = cmd.lower()

                if cmd_lower in ('quitter', 'quit', 'exit', 'q'):
                    print("Au revoir !")
                    break

                elif cmd_lower in ('aide', 'help', 'h'):
                    self.print_help()

                elif cmd_lower in ('tokens', 't'):
                    self.show_tokens = not self.show_tokens
                    state = "activé" if self.show_tokens else "désactivé"
                    print(f"Affichage des tokens : {state}")

                elif cmd_lower in ('exemple', 'example', 'e'):
                    code = self.choose_example()
                    if code:
                        self.analyze(code)

                elif cmd_lower in ('code', ''):
                    code = self.get_multiline_input()
                    if code:
                        self.analyze(code)

                else:
                    # Traite la saisie directe comme du code (casse préservée !)
                    if cmd:
                        self.analyze(cmd)

            except KeyboardInterrupt:
                print("\nUtilisez 'quitter' pour sortir.\n")
            except Exception as e:
                print(f"\nErreur inattendue : {e}\n")


def main():
    compiler = InteractiveCompiler()
    compiler.run()


if __name__ == "__main__":
    main()
