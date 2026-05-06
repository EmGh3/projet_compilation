# 📚 DOCUMENTATION TECHNIQUE COMPLÈTE - COMPILATEUR

## Table des Matières
1. [Vue d'ensemble](#vue-densemble)
2. [Grammaire formelle](#grammaire-formelle)
3. [Phase 1 : Analyse Lexicale](#phase-1--analyse-lexicale)
4. [Phase 2 : Analyse Syntaxique](#phase-2--analyse-syntaxique)
5. [Phase 3 : Analyse Sémantique](#phase-3--analyse-sémantique)
6. [Flux complet du compilateur](#flux-complet-du-compilateur)
7. [Exemples détaillés](#exemples-détaillés)

---

## Vue d'ensemble

Ce compilateur traite un langage de programmation simple à travers **trois phases distinctes** :

```
Code Source
    ↓
    └─→ [Phase 1: Lexical Analysis]    → Tokens
        ↓
        └─→ [Phase 2: Syntax Analysis]      → AST (Abstract Syntax Tree)
            ↓
            └─→ [Phase 3: Semantic Analysis] → Validation
                ↓
                └─→ Rapport Final
```

### Caractéristiques du langage supporté
- **Types de données** : `int`, `string`, `bool`
- **Littéraux booléens** : `true`, `false`
- **Structures de contrôle** : `if-then-else`, `while`
- **Opérateurs** : Arithmétiques (`+`, `-`, `*`, `/`), Relationnels (`>`, `<`, `==`, `!=`, `>=`, `<=`)
- **Commentaires** : `// ...` (ligne) et `/* ... */` (bloc)

---

## Grammaire Formelle

### Notation BNF (Backus-Naur Form)

```bnf
<program>        ::= <statement_list>

<statement_list> ::= <statement> <statement_list>
                   | ε  (empty)

<statement>      ::= <declaration>
                   | <assignment>
                   | <if_statement>
                   | <while_statement>

<declaration>    ::= <type> <identifier> [ '=' <expression> ] ';'

<assignment>     ::= <identifier> '=' <expression> ';'

<if_statement>   ::= 'if' '(' <condition> ')' 'then' '{' <statement_list> '}'
                     [ 'else' '{' <statement_list> '}' ]

<while_statement> ::= 'while' '(' <condition> ')' '{' <statement_list> '}'

<condition>      ::= <expression> <relational_op> <expression>
                   | <expression>  (implicite : == true)

<expression>     ::= <term> { <binary_op> <term> }*

<term>           ::= <identifier>
                   | <number>
                   | <string>
                   | <boolean>
                   | '(' <expression> ')'
                   | '-' <number>

<type>           ::= 'int' | 'string' | 'bool'

<relational_op>  ::= '>' | '<' | '==' | '!=' | '>=' | '<='

<binary_op>      ::= '+' | '-' | '*' | '/'

<identifier>     ::= [a-zA-Z_][a-zA-Z0-9_]*

<number>         ::= [0-9]+

<string>         ::= '"' [^"]* '"'

<boolean>        ::= 'true' | 'false'
```

### Propriétés grammaticales

| Propriété | Valeur |
|-----------|--------|
| Type | Context-Free Grammar (CFG) |
| Analyseur | Recursive Descent Parser |
| Associativité | Gauche (left-associative) |
| Priorité des opérateurs | `* /` > `+ -` |
| Récupération d'erreurs | Synchronisation sur `;` et `}` |

---

## Phase 1 : Analyse Lexicale

### Objectif
Transformer le code source brut en une suite de **tokens** (éléments lexicaux).

### Architecture

#### 1.1 Classes de Tokens

```python
class Token
    ├── Keyword(value: str)           # if, then, else, while, int, string, bool
    ├── Identifier(name: str)          # x, sum, data_value
    ├── Number(value: int)             # 5, 42, 123
    ├── Operator(symbol: str)          # +, -, =, >=, etc.
    ├── StringLiteral(value: str)      # "hello", "world"
    ├── BoolLiteral(value: bool)       # true, false
    └── Métadonnées pour chaque token
        ├── line: int                  # Numéro de ligne
        └── col: int                   # Numéro de colonne
```

#### 1.2 Patterns de Reconnaissance

| Pattern | Expression Régulière | Type | Exemple |
|---------|----------------------|------|---------|
| Bloc de commentaire | `/\*.*?\*/` | BLOCK_COMMENT | `/* ceci est un commentaire */` |
| Commentaire de ligne | `//[^\n]*` | LINE_COMMENT | `// commentaire` |
| Chaîne de caractères | `"[^"]*"` | STRING | `"Hello World"` |
| Nombre entier | `\d+` | NUMBER | `42`, `123` |
| Opérateur | `>=\|<=\|==\|!=\|[+\-*/=><{};,!]` | OPERATOR | `+`, `>=`, `{` |
| Mot/Identifiant | `[a-zA-Z_][a-zA-Z0-9_]*` | WORD | `x`, `count`, `_var` |
| Nouvelle ligne | `\n` | NEWLINE | |
| Espace blanc | `[ \t\r]+` | WHITESPACE | |
| Caractère inconnu | `.` | UNKNOWN | Lève LexicalError |

#### 1.3 Algorithme de Tokenisation

```
1. Initialiser :
   - line = 1, col = 1
   - tokens = []
   - line_start = 0

2. Pour chaque match dans source_code (via regex):
   a. Déterminer le type de pattern (kind)
   b. Récalculer la colonne : col = position - line_start + 1
   
   c. Si kind = NEWLINE :
      - Incrémenter line
      - Mettre à jour line_start
      
   d. Si kind = WHITESPACE ou LINE_COMMENT :
      - Ignorer
      
   e. Si kind = BLOCK_COMMENT :
      - Compter les sauts de ligne à l'intérieur
      - Mettre à jour line et line_start
      
   f. Si kind = UNKNOWN :
      - Lever LexicalError(caractère, line, col)
      
   g. Sinon :
      - Créer le token approprié
      - Ajouter à tokens avec (line, col)

3. Retourner tokens
```

#### 1.4 Exemple Détaillé

**Code source :**
```python
int x = 5;
```

**Exécution :**

| Étape | Pattern | Valeur | Type | Line | Col | Action |
|-------|---------|--------|------|------|-----|--------|
| 1 | WORD | `int` | Keyword | 1 | 1 | Créer `Keyword('int', 1, 1)` |
| 2 | WHITESPACE | ` ` | - | 1 | 4 | Ignorer |
| 3 | WORD | `x` | Identifier | 1 | 5 | Créer `Identifier('x', 1, 5)` |
| 4 | WHITESPACE | ` ` | - | 1 | 6 | Ignorer |
| 5 | OPERATOR | `=` | Operator | 1 | 7 | Créer `Operator('=', 1, 7)` |
| 6 | WHITESPACE | ` ` | - | 1 | 8 | Ignorer |
| 7 | NUMBER | `5` | Number | 1 | 9 | Créer `Number(5, 1, 9)` |
| 8 | OPERATOR | `;` | Operator | 1 | 10 | Créer `Operator(';', 1, 10)` |

**Output :**
```
[KW('int'), ID('x'), '=', NUM(5), ';']
```

#### 1.5 Gestion des Erreurs Lexicales

Lève `LexicalError` avec message formaté :

```
Erreur lexicale à la ligne 3, col 8 : Caractère inconnu '@'
```

**Cas d'erreur** :
- Caractère non reconnu : `@`, `$`, `#`, etc.
- Chaîne de caractères non fermée
- Commentaires mal formés

---

## Phase 2 : Analyse Syntaxique

### Objectif
Valider la **structure grammaticale** du code source et construire un **Abstract Syntax Tree (AST)**.

### Architecture

#### 2.1 Types de Nœuds AST

```
ASTNode (classe de base)
├── Program([statements])
├── DeclarationStmt(var_type, identifier, init_expr?)
├── AssignStmt(identifier, expression)
├── IfStmt(condition, body, else_body?)
├── WhileStmt(condition, body)
├── Condition(left, operator, right)
├── BinaryOp(op, left, right)
├── UnaryOp(op, operand)
├── Identifier(name)
├── Number(value)
├── StringLiteral(value)
└── BoolLiteralNode(value)
```

#### 2.2 Parser Récursif Descendant

**Technique** : Chaque règle grammaticale correspond à une fonction de parsing.

```python
class RecursiveDescentParser:
    
    def parse():                    # Point d'entrée → Program
        └─→ _parse_statement_list()
        
    def _parse_statement_list():    # Boucle sur les statements
        └─→ _parse_statement() (répété)
        
    def _parse_statement():         # Dispatch selon token courant
        ├─→ _parse_declaration()    (si type keyword)
        ├─→ _parse_if_stmt()        (si 'if')
        ├─→ _parse_while_stmt()     (si 'while')
        └─→ _parse_assignment()     (si identifier)
        
    def _parse_declaration():       # <type> <id> [ = <expr> ] ;
        └─→ _parse_expression() (optionnel)
        
    def _parse_assignment():        # <id> = <expr> ;
        └─→ _parse_expression()
        
    def _parse_if_stmt():           # if ( <cond> ) then { ... }
        └─→ _parse_condition()
        └─→ _parse_statement_list()
        
    def _parse_while_stmt():        # while ( <cond> ) { ... }
        └─→ _parse_condition()
        └─→ _parse_statement_list()
        
    def _parse_condition():         # <expr> <relop> <expr>
        └─→ _parse_expression() (×2)
        
    def _parse_expression():        # <term> { <binop> <term> }*
        └─→ _parse_term() (× plusieurs)
        └─→ BinaryOp (construction itérative)
        
    def _parse_term():              # id | num | string | bool | (...) | -num
        ├─→ Identifier
        ├─→ Number
        ├─→ StringLiteral
        ├─→ BoolLiteralNode
        ├─→ _parse_expression() (si parenthésé)
        └─→ UnaryOp (si négatif)
```

#### 2.3 Fonctions Auxiliaires

```python
# Navigation dans les tokens
_cur()              # Token courant
_peek_next()        # Token suivant
_advance()          # Avancer d'un token
_at_end()           # Fin du fichier?

# Vérifications (sans conversion textuelle)
_is_keyword(value)
_is_type_keyword()
_is_operator(symbol)
_is_relop()         # Opérateur relationnel?
_is_binop()         # Opérateur binaire?

# Consommation avec vérification
_consume_keyword(value)      → bool
_consume_operator(symbol)    → bool
_consume_identifier()        → str?

# Position et erreurs
_pos_info()         → (line, col)
_error(msg)         → Ajoute ParseError
_synchronize()      → Récupération après erreur
```

#### 2.4 Synchronisation et Récupération d'Erreurs

**Stratégie** : Après une erreur, avancer jusqu'au token de synchronisation.

```python
def _synchronize():
    # Avancer jusqu'à ';' (fin de statement)
    # ou '}' (fin de bloc)
    # ou fin du fichier
```

**Cas d'erreur** :
- Mot-clé manquant
- Opérateur attendu non trouvé
- Identifiant manquant
- Parenthèse/accolade non fermée

#### 2.5 Exemple d'Arbre de Parsing

**Code source :**
```python
int x = 5;
if (x > 0) then {
    x = x + 1;
}
```

**AST généré :**
```
Program
├── DeclarationStmt(int, x, Number(5))
└── IfStmt
    ├── Condition
    │   ├── Identifier(x)
    │   ├── Operator(>)
    │   └── Number(0)
    └── body: [
        AssignStmt(x, BinaryOp(+, Identifier(x), Number(1)))
    ]
```

#### 2.6 Complexité de Parsing

| Entrée | Sortie | Complexité |
|--------|--------|-----------|
| Nombres de tokens : n | Profondeur AST : O(n) | Temps : O(n) |
| | Nœuds AST : O(n) | Espace : O(n) |

---

## Phase 3 : Analyse Sémantique

### Objectif
Valider la **sémantique** du code :
- Vérification des types
- Déclaration avant utilisation
- Cohérence de scope
- Initialisation des variables

### Architecture

#### 3.1 Table des Symboles (Symbol Table)

**Structure hiérarchique (pile de scopes)** :

```python
class SymbolTable:
    scopes: List[Dict[str, SymbolInfo]]
    ├── scopes[0]        # Scope global
    ├── scopes[1]        # Scope if_statement
    ├── scopes[2]        # Scope nested_if
    └── ...
    
class SymbolInfo:
    name: str            # Nom de la variable
    var_type: str        # 'int', 'string', ou 'bool'
    scope_level: int     # Niveau de portée
    initialized: bool    # Initialisée?
    used: bool           # Utilisée?
```

#### 3.2 Gestion des Scopes

```python
# Entrée dans un bloc (if, while)
symbol_table.enter_scope()

# Déclaration dans le scope courant
symbol_table.declare(name, type, initialized=False)

# Recherche en remontant vers le scope global
symbol_table.lookup(name) → SymbolInfo?

# Marquer comme initialisée
symbol_table.mark_initialized(name)

# Marquer comme utilisée
symbol_table.mark_used(name)

# Sortie du scope courant
symbol_table.exit_scope() → [SymbolInfo]
```

#### 3.3 Règles de Type

**Opérations valides par type** :

| Opérateur | int | string | bool | Résultat |
|-----------|-----|--------|------|----------|
| `+` | ✓ `int+int` | ✓ `str+str` (concat) | ✗ | int / string |
| `-` | ✓ `int-int` | ✗ | ✗ | int |
| `*` | ✓ `int*int` | ✗ | ✗ | int |
| `/` | ✓ `int/int` | ✗ | ✗ | int |
| `>`, `<` | ✓ | ✗ | ✗ | bool (implicite) |
| `==`, `!=` | ✓ | ✓ | ✓ | bool (implicite) |
| `>=`, `<=` | ✓ | ✗ | ✗ | bool (implicite) |

#### 3.4 Inférence de Type (Type Inference)

**Algorithme** :

```python
def _infer_type(expr: Expression) → str | None:
    
    if isinstance(expr, Number):
        return 'int'
    
    if isinstance(expr, StringLiteral):
        return 'string'
    
    if isinstance(expr, BoolLiteralNode):
        return 'bool'
    
    if isinstance(expr, Identifier):
        info = symbol_table.lookup(expr.name)
        if not info:
            ERROR: Variable non déclarée
        if not info.initialized:
            WARNING: Variable non initialisée
        return info.var_type
    
    if isinstance(expr, BinaryOp):
        left_type = _infer_type(expr.left)
        right_type = _infer_type(expr.right)
        
        if expr.op == '+':
            if left_type == right_type and left_type in ('int', 'string'):
                return left_type
            else:
                ERROR: Incompatibilité de types
        
        if expr.op in ('-', '*', '/'):
            if left_type == 'int' and right_type == 'int':
                return 'int'
            else:
                ERROR: Requiert deux int
    
    if isinstance(expr, UnaryOp):
        operand_type = _infer_type(expr.operand)
        if expr.op == '-':
            if operand_type == 'int':
                return 'int'
            else:
                ERROR: Négatif requiert int
```

#### 3.5 Vérifications Sémantiques

**A. Analyse de Déclaration :**
```python
def _analyze_declaration(decl: DeclarationStmt):
    # Vérifier le type
    if decl.var_type not in VALID_TYPES:
        ERROR
    
    # Vérifier l'initialisation (si présente)
    if decl.init_expr:
        expr_type = _infer_type(decl.init_expr)
        if expr_type != decl.var_type:
            ERROR: Incompatibilité
        initialized = True
    
    # Ajouter à la table des symboles
    if not symbol_table.declare(decl.identifier, decl.var_type, initialized):
        ERROR: Redéclaration
```

**B. Analyse d'Assignation :**
```python
def _analyze_assignment(assign: AssignStmt):
    # Vérifier que la variable est déclarée
    info = symbol_table.lookup(assign.identifier)
    if not info:
        ERROR: Variable utilisée avant déclaration
    
    # Vérifier la compatibilité de type
    expr_type = _infer_type(assign.expression)
    if info.var_type != expr_type:
        ERROR: Incompatibilité de types
    
    # Marquer comme initialisée
    symbol_table.mark_initialized(assign.identifier)
```

**C. Analyse de Condition :**
```python
def _analyze_condition(cond: Condition):
    left_type = _infer_type(cond.left)
    right_type = _infer_type(cond.right)
    
    # Les deux côtés doivent être du même type
    if left_type != right_type:
        ERROR: Incompatibilité dans la condition
    
    # L'opérateur doit être valide pour ce type
    valid_ops = VALID_RELOPS[left_type]
    if cond.operator not in valid_ops:
        ERROR: Opérateur invalide pour ce type
```

**D. Analyse de Portée (Scopes) :**
```python
# If statement crée un nouveau scope
if stmt:
    symbol_table.enter_scope()
    analyze_statements(stmt.body)
    symbol_table.exit_scope()

# While statement crée un nouveau scope
while stmt:
    symbol_table.enter_scope()
    analyze_statements(stmt.body)
    symbol_table.exit_scope()
```

#### 3.6 Types d'Erreurs et d'Avertissements

**Erreurs** :
1. **Variable non déclarée** : `x = 5;` (x n'existe pas)
2. **Redéclaration** : `int x; int x;` (même scope)
3. **Incompatibilité de type** : `int x; x = "hello";`
4. **Opérateur invalide** : `string s = "hello"; int n = s - 1;`
5. **Condition invalide** : `if ("hello" > 5) then { ... }`

**Avertissements** :
1. **Variable non initialisée** : `int x; x = x + 1;` (x utilisée avant assignation)
2. **Variable non utilisée** : `int x; x = 5;` (déclaré mais jamais lu)

#### 3.7 Rapport d'Analyse Sémantique

**Format** :
```
==============================================================
RAPPORT D'ANALYSE SÉMANTIQUE
==============================================================

Table des symboles :
====================================================
Portée 0 :
  x: int (portée 0, initialisée)
  y: int (portée 0, NON initialisée)
  s: string (portée 0, initialisée)
Portée 1 :
  temp: int (portée 1, initialisée)

ERREURS :
─────────────────────────────────────────────────
  1. Variable 'z' utilisée avant déclaration

AVERTISSEMENTS :
─────────────────────────────────────────────────
  1. Variable 'y' utilisée avant d'avoir été initialisée

==============================================================
Résumé : 1 erreur(s), 1 avertissement(s)
==============================================================
```

---

## Flux Complet du Compilateur

### Diagramme de Flux

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CODE SOURCE BRUT                                         │
│ ────────────────────────────────────────────────────────────│
│ int x = 5;                                                  │
│ if (x > 0) then { x = x + 1; }                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
                [PHASE 1: LEXICAL ANALYSIS]
                 (lexical_analyzer.py)
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. TOKENS (Séquence d'éléments lexicaux)                   │
│ ────────────────────────────────────────────────────────────│
│ [                                                           │
│   KW('int', line=1, col=1),                                │
│   ID('x', line=1, col=5),                                  │
│   '='(line=1, col=7),                                      │
│   NUM(5, line=1, col=9),                                   │
│   ';'(line=1, col=10),                                     │
│   KW('if', line=2, col=1),                                 │
│   '('(line=2, col=4),                                      │
│   ID('x', line=2, col=5),                                  │
│   '>'(line=2, col=7),                                      │
│   NUM(0, line=2, col=9),                                   │
│   ')'(line=2, col=10),                                     │
│   KW('then', line=2, col=12),                              │
│   '{'(line=2, col=17),                                     │
│   ID('x', line=2, col=19),                                 │
│   '='(line=2, col=21),                                     │
│   ID('x', line=2, col=23),                                 │
│   '+'(line=2, col=25),                                     │
│   NUM(1, line=2, col=27),                                  │
│   ';'(line=2, col=28),                                     │
│   '}'(line=2, col=30)                                      │
│ ]                                                           │
└─────────────────────────────────────────────────────────────┘
                          ↓
                [PHASE 2: SYNTAX ANALYSIS]
                 (syntax_analyzer.py)
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. ABSTRACT SYNTAX TREE (AST)                              │
│ ────────────────────────────────────────────────────────────│
│ Program                                                     │
│   ├─ DeclarationStmt                                       │
│   │   ├─ var_type: 'int'                                  │
│   │   ├─ identifier: 'x'                                  │
│   │   └─ init_expr: Number(5)                             │
│   └─ IfStmt                                                │
│       ├─ condition: Condition(                             │
│       │   ├─ left: Identifier('x')                        │
│       │   ├─ operator: '>'                                │
│       │   └─ right: Number(0)                             │
│       │ )                                                  │
│       └─ body: [                                           │
│           AssignStmt(                                      │
│             identifier: 'x',                               │
│             expression: BinaryOp(                          │
│               op: '+',                                     │
│               left: Identifier('x'),                       │
│               right: Number(1)                             │
│             )                                              │
│           )                                                │
│         ]                                                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
                [PHASE 3: SEMANTIC ANALYSIS]
                 (semantic_analyzer.py)
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. RÉSULTATS DE VALIDATION SÉMANTIQUE                       │
│ ────────────────────────────────────────────────────────────│
│ ✓ Analyse réussie - Aucune erreur                          │
│                                                             │
│ Table des symboles :                                       │
│ ┌─ Portée 0 (global):                                     │
│ │  • x: int (initialisée, utilisée)                       │
│ │                                                          │
│ └─ Portée 1 (if_statement):                               │
│    (variables locales)                                     │
│                                                             │
│ Résumé : 0 erreur(s), 0 avertissement(s)                  │
└─────────────────────────────────────────────────────────────┘
```

### Pseudo-Code du Pipeline Complet

```python
def compile(source_code: str) → CompilationResult:
    """
    Exécute les trois phases du compilateur.
    """
    
    # ========== PHASE 1 : ANALYSE LEXICALE ==========
    print("Phase 1 : Analyse Lexicale...")
    lexer = Lexer()
    try:
        tokens = lexer.tokenize(source_code)
        print(f"✓ {len(tokens)} tokens générés")
    except LexicalError as e:
        print(f"✗ Erreur lexicale : {e}")
        return CompilationResult(success=False, error=e)
    
    # ========== PHASE 2 : ANALYSE SYNTAXIQUE ==========
    print("\nPhase 2 : Analyse Syntaxique...")
    parser = RecursiveDescentParser(tokens)
    ast = parser.parse()
    
    if ast is None or parser.errors:
        print(f"✗ {len(parser.errors)} erreur(s) de parsing")
        for err in parser.errors:
            print(f"  → {err}")
        return CompilationResult(success=False, errors=parser.errors)
    
    print(f"✓ AST généré avec succès")
    print(f"  Nœuds racines : {len(ast.statements)}")
    
    # ========== PHASE 3 : ANALYSE SÉMANTIQUE ==========
    print("\nPhase 3 : Analyse Sémantique...")
    semantic_analyzer = SemanticAnalyzer()
    success = semantic_analyzer.analyze(ast)
    
    report = semantic_analyzer.get_report()
    print(report)
    
    if success:
        print("✓ Compilation réussie!")
        return CompilationResult(
            success=True,
            ast=ast,
            symbol_table=semantic_analyzer.symbol_table
        )
    else:
        print("✗ Erreurs sémantiques détectées")
        return CompilationResult(
            success=False,
            errors=semantic_analyzer.errors,
            warnings=semantic_analyzer.warnings
        )
```

---

## Exemples Détaillés

### Exemple 1 : Programme Simple (Succès)

#### Code Source
```python
int x;
x = 10;
string greeting;
greeting = "Hello";
```

#### Phase 1 : Tokenisation

**Lexer.tokenize()** produit :
```
[
  KW('int', 1, 1),
  ID('x', 1, 5),
  ';' (1, 6),
  ID('x', 2, 1),
  '=' (2, 3),
  NUM(10, 2, 5),
  ';' (2, 7),
  KW('string', 3, 1),
  ID('greeting', 3, 9),
  ';' (3, 17),
  ID('greeting', 4, 1),
  '=' (4, 11),
  STRING("Hello", 4, 13),
  ';' (4, 20)
]
```

#### Phase 2 : Parsing

**Parser.parse()** construit l'AST :

```
Program
├── DeclarationStmt(var_type='int', identifier='x', init_expr=None)
├── AssignStmt(identifier='x', expression=Number(10))
├── DeclarationStmt(var_type='string', identifier='greeting', init_expr=None)
└── AssignStmt(identifier='greeting', expression=StringLiteral("Hello"))
```

**Étapes du parsing** :

```
1. _parse_statement_list()
   a. _parse_statement() → _parse_declaration()
      - Consomme KW('int')
      - Consomme ID('x')
      - Voit ';' → pas d'initialisation
      - Crée DeclarationStmt(int, x, None)
   
   b. _parse_statement() → _parse_assignment()
      - Consomme ID('x')
      - Consomme '='
      - _parse_expression() → _parse_term() → Number(10)
      - Crée AssignStmt(x, Number(10))
   
   [... et ainsi de suite ...]
```

#### Phase 3 : Analyse Sémantique

**SymbolTable après analyse** :

```
Portée 0:
├── x: int (initialisée=False, utilisée=True)
└── greeting: string (initialisée=False, utilisée=True)
```

**Vérifications** :
```
1. DeclarationStmt(int, x, None)
   → symbol_table.declare('x', 'int', False) ✓

2. AssignStmt(x, Number(10))
   → Cherche 'x' : trouvé ✓
   → Type de expression : 'int' ✓
   → Types compatibles : int == int ✓
   → mark_initialized('x') ✓

3. [Idem pour string]

Résultat : ✓ Succès
```

---

### Exemple 2 : Condition avec If-Then-Else

#### Code Source
```python
int score;
score = 85;
string grade;
if (score >= 60) then {
    grade = "Pass";
} else {
    grade = "Fail";
}
```

#### Phase 2 : AST Structuré

```
Program
├── DeclarationStmt(int, score)
├── AssignStmt(score, Number(85))
├── DeclarationStmt(string, grade)
└── IfStmt(
    ├─ condition: Condition(
    │  ├─ left: Identifier(score)
    │  ├─ operator: '>='
    │  └─ right: Number(60)
    │ )
    ├─ body: [
    │  AssignStmt(grade, StringLiteral("Pass"))
    │ ]
    └─ else_body: [
       AssignStmt(grade, StringLiteral("Fail"))
      ]
)
```

#### Phase 3 : Analyse Sémantique

**Table des symboles** :

```
Portée 0 (global):
├── score: int (initialisée, utilisée)
└── grade: string (initialisée, utilisée)

Portée 1 (if block):
└── (grade assignée depuis global)

Portée 2 (else block):
└── (grade assignée depuis global)
```

**Vérifications** :
```
Condition(Identifier(score), '>=', Number(60)):
├─ Type de score : 'int' ✓
├─ Type de 60 : 'int' ✓
├─ Opérateur '>=' valide pour int ✓
└─ Condition valide ✓

AssignStmt(grade, StringLiteral("Pass")):
├─ grade trouvée en scope parent ✓
├─ Type de StringLiteral("Pass") : 'string' ✓
├─ string == string ✓
└─ mark_initialized(grade) ✓
```

**Résultat** : ✓ Succès

---

### Exemple 3 : Erreur - Variable Non Initialisée

#### Code Source
```python
int x;
int y;
y = x + 1;
```

#### Phase 1 & 2 : ✓ Réussi

L'analyse lexicale et syntaxique ne détectent pas de problème.

#### Phase 3 : Analyse Sémantique

**Analyse de `AssignStmt(y, BinaryOp(+, Identifier(x), Number(1)))` :**

```
_infer_type(BinaryOp(+, Identifier(x), Number(1))):
├─ _infer_type(Identifier(x)):
│  ├─ symbol_table.lookup('x') → SymbolInfo(x, int, initialized=False)
│  ├─ WARNING: "Variable 'x' utilisée avant d'avoir été initialisée"
│  └─ return 'int'
├─ _infer_type(Number(1)) → return 'int'
├─ Op '+' avec (int, int) → return 'int' ✓
└─ Type final : 'int'
```

**Résultat** :
```
✓ Syntaxe valide
✗ 1 avertissement : Variable 'x' utilisée avant d'avoir été initialisée
```

---

### Exemple 4 : Erreur - Incompatibilité de Type

#### Code Source
```python
int x;
string s;
x = s + 5;
```

#### Phase 3 : Analyse Sémantique

**Analyse de `AssignStmt(x, BinaryOp(+, Identifier(s), Number(5)))` :**

```
1. Chercher 'x' : trouvé, type='int' ✓

2. _infer_type(BinaryOp(+, Identifier(s), Number(5))):
   ├─ _infer_type(Identifier(s)) → 'string'
   ├─ _infer_type(Number(5)) → 'int'
   ├─ Op '+' avec (string, int)
   ├─ Vérifie : string == int ?
   │   NON
   └─ Op '+' valide pour ('string', 'int') ?
       NON (seulement int+int ou string+string)

3. ERROR: "L'opérateur '+' ne peut pas être appliqué à string et int.
          Combinaisons valides : int+int, string+string"

4. _infer_type() retourne None

5. Type expression = None ≠ int (type de x)
   └─ Pas de vérification finale puisque expression invalide
```

**Résultat** :
```
✗ Erreur : L'opérateur '+' ne peut pas être appliqué à string et int
```

---

### Exemple 5 : Boucle While avec Condition

#### Code Source
```python
int counter;
counter = 0;
while (counter < 10) {
    counter = counter + 1;
}
```

#### Phase 2 : AST

```
Program
├── DeclarationStmt(int, counter)
├── AssignStmt(counter, Number(0))
└── WhileStmt(
    ├─ condition: Condition(
    │  ├─ left: Identifier(counter)
    │  ├─ operator: '<'
    │  └─ right: Number(10)
    │ )
    └─ body: [
       AssignStmt(counter, BinaryOp(+, Identifier(counter), Number(1)))
      ]
)
```

#### Phase 3 : Table des Symboles

```
Portée 0 (global):
├── counter: int (initialisée, utilisée)

Portée 1 (while body):
└── (counter accédée depuis global)
```

**Vérifications** :
```
Condition(Identifier(counter), '<', Number(10)):
├─ counter type : 'int' ✓
├─ 10 type : 'int' ✓
├─ Opérateur '<' valide pour int ✓
└─ Condition valide ✓

Scope 1 (while body):
├─ symbol_table.enter_scope()
├─ AssignStmt(counter, BinaryOp(...)) :
│  └─ counter trouvé en scope parent ✓
└─ symbol_table.exit_scope()
```

**Résultat** : ✓ Succès

---

## Tableaux de Référence

### Tableau 1 : Tokens et Représentation

| Type | Classe | Exemple | Représentation |
|------|--------|---------|-----------------|
| Keyword | `Keyword` | `int` | `KW('int')` |
| Identifier | `Identifier` | `myVar` | `ID('myVar')` |
| Number | `Number` | `42` | `NUM(42)` |
| String | `StringLiteral` | `"hi"` | `STRING("hi")` |
| Boolean | `BoolLiteral` | `true` | `BOOL(true)` |
| Operator | `Operator` | `+` | `'+'` |
| Delimiter | `Operator` | `{` | `'{'` |

### Tableau 2 : Mots-clés Réservés

| Catégorie | Mots-clés |
|-----------|-----------|
| Types | `int`, `string`, `bool` |
| Contrôle | `if`, `then`, `else`, `while` |
| Booléens | `true`, `false` |

### Tableau 3 : Opérateurs par Priorité (descendante)

| Priorité | Opérateurs | Type | Associativité |
|----------|-----------|------|----------------|
| 1 (Haute) | `*`, `/` | Multiplicatif | Gauche |
| 2 | `+`, `-` | Additif | Gauche |
| 3 (Basse) | `>`, `<`, `==`, `!=`, `>=`, `<=` | Relationnel | Gauche |

### Tableau 4 : Correspondance Phases → Fichiers

| Phase | Fichier | Classe Principale | Entrée | Sortie |
|-------|---------|------------------|--------|--------|
| 1 | `lexical_analyzer.py` | `Lexer` | `str` (code) | `List[Token]` |
| 2 | `syntax_analyzer.py` | `RecursiveDescentParser` | `List[Token]` | `Program` (AST) |
| 3 | `semantic_analyzer.py` | `SemanticAnalyzer` | `Program` (AST) | `bool` + Rapport |

---

## Conclusion

Ce compilateur illustre les trois phases fondamentales de tout compilateur :

1. **Analyse Lexicale** : Découpe le code en tokens
2. **Analyse Syntaxique** : Organise les tokens en structure arborescente (AST)
3. **Analyse Sémantique** : Valide la cohérence et la correctness du code

Chaque phase s'appuie sur la précédente et ajoute des informations de validation supplémentaires. Les erreurs à chaque phase sont rapportées avec précision (ligne, colonne) pour faciliter le débogage.

---

**Document généré automatiquement**  
*Dernière mise à jour : 2026-05-06*
