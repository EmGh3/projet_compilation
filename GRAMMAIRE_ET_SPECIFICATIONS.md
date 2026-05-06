# 📋 GRAMMAIRE FORMELLE ET SPÉCIFICATIONS DÉTAILLÉES

## Table des Matières
1. [Grammaire BNF Complète](#grammaire-bnf-complète)
2. [Spécifications Lexicales Détaillées](#spécifications-lexicales-détaillées)
3. [Spécifications Syntaxiques Détaillées](#spécifications-syntaxiques-détaillées)
4. [Spécifications Sémantiques Détaillées](#spécifications-sémantiques-détaillées)
5. [Diagrammes de Transition](#diagrammes-de-transition)

---

## Grammaire BNF Complète

### Notation Utilisée

```
::=     Production (Peut se développer en)
|       Alternation (Ou)
{ }     Répétition zéro ou plus (Kleene star)
[ ]     Optionnel (zéro ou une fois)
( )     Groupement
ε       Production vide (epsilon)
```

### Grammaire Complète

```bnf
/* =====================================================
   NIVEAU 1 : PROGRAMME
   ===================================================== */

<program>                   ::= <statement_list>

<statement_list>            ::= <statement> <statement_list>
                              | ε

<statement>                 ::= <declaration_statement>
                              | <assignment_statement>
                              | <if_statement>
                              | <while_statement>


/* =====================================================
   NIVEAU 2 : TYPES DE STATEMENTS
   ===================================================== */

<declaration_statement>     ::= <type_keyword> <identifier> 
                                [ '=' <expression> ] ';'

<assignment_statement>      ::= <identifier> '=' <expression> ';'

<if_statement>              ::= 'if' '(' <condition> ')' 'then' 
                                '{' <statement_list> '}'
                                [ 'else' '{' <statement_list> '}' ]

<while_statement>           ::= 'while' '(' <condition> ')' 
                                '{' <statement_list> '}'


/* =====================================================
   NIVEAU 3 : CONDITIONS ET EXPRESSIONS
   ===================================================== */

<condition>                 ::= <expression> <relational_operator> <expression>
                              | <expression>

<expression>                ::= <term> { <binary_operator> <term> }

<term>                      ::= <primary>
                              | '-' <primary>

<primary>                   ::= <identifier>
                              | <numeric_literal>
                              | <string_literal>
                              | <boolean_literal>
                              | '(' <expression> ')'


/* =====================================================
   NIVEAU 4 : TOKENS TERMINAUX
   ===================================================== */

<type_keyword>              ::= 'int' | 'string' | 'bool'

<relational_operator>       ::= '>'  | '<'  | '==' | '!=' 
                              | '>=' | '<='

<binary_operator>           ::= '+' | '-' | '*' | '/'

<identifier>                ::= [a-zA-Z_][a-zA-Z0-9_]*

<numeric_literal>           ::= [0-9]+

<string_literal>            ::= '"' [^"]* '"'

<boolean_literal>           ::= 'true' | 'false'
```

### Propriétés Formelles de la Grammaire

| Propriété | Valeur | Justification |
|-----------|--------|---------------|
| **Type de grammaire** | Context-Free Grammar (CFG) | Pas de contexte sur les productions |
| **Ambiguïté** | Non-ambiguë | Chaque construction a une interprétation unique |
| **Hiérarchie de Chomsky** | Type 2 | CFG pure |
| **Récursivité** | Gauche-récursive implicite | Via `statement_list` |
| **Analyseur utilisé** | Recursive Descent | Descendant sans backtracking |

### Analyse de Conflit

**Pas de conflits reduce-reduce** ✓  
**Pas de conflits shift-reduce majeurs** ✓

---

## Spécifications Lexicales Détaillées

### 1. Alphabet et Vocabulaire

#### Alphabets acceptés

| Catégorie | Caractères |
|-----------|-----------|
| **Minuscules** | `a-z` |
| **Majuscules** | `A-Z` |
| **Chiffres** | `0-9` |
| **Symboles spéciaux** | ` ` (espace), `_` (underscore) |
| **Délimiteurs** | `( ) { } ; , "` |
| **Opérateurs** | `+ - * / = > < ! &` |
| **Contrôle** | `\n` (newline), `\t` (tab), `\r` (carriage return) |

#### Alphabets rejetés

| Caractère | Code ASCII | Raison |
|-----------|-----------|--------|
| `@` | 64 | Pas d'usage |
| `#` | 35 | Réservé pour directives |
| `$` | 36 | Pas d'usage |
| `%` | 37 | Opérateur modulo non supporté |
| `&` | 38 | Opérateur logique non supporté |
| `\|` | 124 | Opérateur logique non supporté |
| `` ` `` | 96 | Pas d'usage |

### 2. Patterns de Tokenisation (Ordre Critique)

**L'ordre des patterns est critique** car les regex sont testées dans l'ordre :

```python
_TOKEN_PATTERNS = [
    ('BLOCK_COMMENT', r'/\*.*?\*/'),      # DOIT être avant LINE_COMMENT
    ('LINE_COMMENT',  r'//[^\n]*'),       # Commentaires de ligne
    ('STRING',        r'"[^"]*"'),        # Littéraux string
    ('NUMBER',        r'\d+'),             # Nombres décimaux
    ('OPERATOR',      r'>=|<=|==|!=|[+\-*/=><{}();,!]'),  # Multi-char d'abord
    ('WORD',          r'[a-zA-Z_][a-zA-Z0-9_]*'),         # Identifiants/Keywords
    ('NEWLINE',       r'\n'),              # Suivi
    ('WHITESPACE',    r'[ \t\r]+'),        # Puis whitespace
    ('UNKNOWN',       r'.'),               # Catch-all
]
```

### 3. Détails des Patterns

#### Pattern : Bloc de Commentaire

```regex
/\*.*?\*/
```

| Élément | Sens |
|---------|------|
| `/\*` | Début littéral |
| `.*?` | Contenu quelconque (non-greedy) |
| `\*/` | Fin littéral |

**Exemple** :
```
/* Ceci est un commentaire */
/* Multi-ligne
   est supporté */
```

**Propriété** : Ignorerait les `*/` imbriqués (pas de nesting)

#### Pattern : Commentaire de Ligne

```regex
//[^\n]*
```

| Élément | Sens |
|---------|------|
| `//` | Début littéral |
| `[^\n]*` | Tout sauf newline |

**Exemple** :
```
int x; // Variable
```

#### Pattern : Littéral String

```regex
"[^"]*"
```

| Élément | Sens |
|---------|------|
| `"` | Délimiteur ouvert |
| `[^"]*` | Contenu (pas de `"`) |
| `"` | Délimiteur fermé |

**Exemple** :
```
"Hello World"
"123"
""  (vide)
```

**Restriction** : Pas d'échappement (`\"` non supporté)

#### Pattern : Nombre

```regex
\d+
```

| Élément | Sens |
|---------|------|
| `\d+` | Un ou plusieurs chiffres |

**Propriété** : Uniquement entiers positifs

**Exemples valides** : `0`, `5`, `42`, `99999`  
**Exemples invalides** : `3.14` (flotant), `-5` (unaire)

#### Pattern : Opérateur

```regex
>=|<=|==|!=|[+\-*/=><{}();,!]
```

Cet ordre est critique :
1. `>=` avant `>`
2. `<=` avant `<`
3. `==` avant `=`
4. `!=` avant `!`

**Opérateurs supportés** :

| Catégorie | Symboles |
|-----------|----------|
| **Arithmétique** | `+`, `-`, `*`, `/` |
| **Assignment** | `=` |
| **Comparaison** | `>`, `<`, `>=`, `<=`, `==`, `!=` |
| **Délimiteurs** | `(`, `)`, `{`, `}`, `;`, `,` |
| **Autres** | `!` |

#### Pattern : Mot (Keyword ou Identifier)

```regex
[a-zA-Z_][a-zA-Z0-9_]*
```

| Élément | Sens |
|---------|------|
| `[a-zA-Z_]` | Premier caractère : lettre ou underscore |
| `[a-zA-Z0-9_]*` | Caractères suivants : lettres, chiffres, underscore |

**Exemple de tokens valides** :
- `int` → Keyword
- `myVar` → Identifier
- `_private` → Identifier
- `x1y2z3` → Identifier
- `true` → BoolLiteral
- `false` → BoolLiteral

**Exemple de tokens invalides** :
- `1var` → Commence par chiffre (tokenisé comme NUMBER `1` + WORD `var`)
- `my-var` → Tiret non autorisé (tokenisé comme `my` - `var`)

### 4. Gestion des Positions (Line, Column)

```python
line = 1              # Numéro de ligne (1-indexed)
line_start = 0        # Position du début de ligne dans source_code
col = m.start() - line_start + 1  # Colonne (1-indexed)

# À chaque newline
if kind == 'NEWLINE':
    line += 1
    line_start = m.end()
```

**Exemple** :
```
Ligne 1 : int x = 5;
          123456789...
                    ↑ col=10 (position du `;`)

Ligne 2 : x = x + 1;
          123456789...
```

### 5. Erreurs Lexicales

**Condition** : Caractère non reconnu trouvé

**Message d'erreur** :
```
Erreur lexicale à la ligne 3, col 5 : Caractère inconnu '@'
```

**Classe** : `LexicalError(message: str, line: int, col: int)`

---

## Spécifications Syntaxiques Détaillées

### 1. Technique de Parsing

**Méthode** : Recursive Descent Parser (RDP)  
**Stratégie** : Top-down, sans backtracking  
**Caractère de lookahead** : 1 (LL(1) lookahead)

### 2. Fonctions de Parsing (Correspondance Règles → Fonctions)

```python
Grammar Rule                          Function Parser
─────────────────────────────────────────────────────────────
<program>                          ← parse()
<statement_list>                   ← _parse_statement_list()
<statement>                        ← _parse_statement()
<declaration_statement>            ← _parse_declaration()
<assignment_statement>             ← _parse_assignment()
<if_statement>                     ← _parse_if_stmt()
<while_statement>                  ← _parse_while_stmt()
<condition>                        ← _parse_condition()
<expression>                       ← _parse_expression()
<term>                            ← _parse_term()
<primary>                         ← (partie de _parse_term())
```

### 3. Analyse de Conflit Récursif

#### Récursivité Indirecte (Gauche)

```
<statement_list> ::= <statement> <statement_list>
                      ↑                ↑
                      Peut être vide  Appelle statement_list

Mais début de <statement_list> commence par <statement>,
qui ne commence pas par <statement_list>.

DONC : Pas de conflit left-recursive direct ✓
```

#### Prédiction pour Dispatch

```python
def _parse_statement():
    t = _cur()
    
    if _is_type_keyword():           # int | string | bool
        return _parse_declaration()
    elif _is_keyword('if'):          # if
        return _parse_if_stmt()
    elif _is_keyword('while'):       # while
        return _parse_while_stmt()
    elif isinstance(t, Identifier):  # identifier
        return _parse_assignment()
```

**Propriété** : Les FIRST sets sont disjoints → Pas de conflit

### 4. Opérateurs et Associativité

#### Priorité des Opérateurs (descendante)

```
Niveau 1 (Haute priorité) :  * /    (Multiplicatif)
Niveau 2 :                   + -    (Additif)
Niveau 3 (Basse priorité) :  > < == != >= <=  (Relationnel)
```

#### Construction Left-Associative

```python
def _parse_expression():
    left = _parse_term()           # 1 * 2 * 3
    
    while _is_binop():
        op = _cur().symbol
        _advance()
        right = _parse_term()
        left = BinaryOp(op, left, right)  # Assoc. gauche
    
    return left

# Trace pour "1 * 2 + 3" :
#
# left = 1
# Voir '*' → left = BinaryOp(*, 1, 2)
# Voir '+' → left = BinaryOp(+, BinaryOp(*, 1, 2), 3)
#                          ↑
#                    Associativité gauche
#
# Résultat : (1 * 2) + 3 ✓ (pas 1 * (2 + 3))
```

### 5. Synchronisation et Récupération d'Erreurs

#### Stratégie

Après une erreur, avancer jusqu'à un **token de synchronisation** :

```python
def _synchronize():
    """Avance jusqu'à un token permettant la reprise."""
    while not _at_end():
        if _is_operator(';'):       # Fin de statement
            _advance()
            return
        if _is_operator('}'):       # Fin de bloc
            return
        _advance()
```

#### Exemple de Récupération

**Code erroné** :
```python
int x = ;  // Erreur : expression manquante
x = 5;     // Doit pouvoir être parsé quand même
```

**Trace** :
```
1. _parse_declaration()
2. Voir '=' → _parse_expression()
3. Voir ';' au lieu d'expression
4. ERROR: "Expression attendue"
5. _parse_term() voit ';' → ERROR: "Terme inattendu"
6. _synchronize() avance jusqu'à ';'
7. Retour à _parse_statement_list()
8. Reprend avec 'x = 5;' ✓
```

### 6. Validation des Parenthèses et Accolades

#### Matching Garanti

```python
def _parse_if_stmt():
    self._consume_keyword('if')
    self._consume_operator('(')      # ← Vérifier
    cond = self._parse_condition()
    self._consume_operator(')')      # ← Vérifier
    self._consume_keyword('then')
    self._consume_operator('{')      # ← Vérifier
    body = self._parse_statement_list(stop_on_rbrace=True)
    self._consume_operator('}')      # ← Vérifier
```

---

## Spécifications Sémantiques Détaillées

### 1. Domaines de Type

```
Type ::= int | string | bool

Operations:
─────────────────────────────────
Type × Operator × Type → Type | Error

int × + × int           → int
int × - × int           → int
int × * × int           → int
int × / × int           → int
string × + × string     → string
bool × + × bool         → ERROR
```

### 2. Table des Symboles (Implémentation)

#### Structure Interne

```python
class SymbolTable:
    scopes: List[Dict[str, SymbolInfo]]
    #       ↑                    ↑
    #       Pile de scopes   Variable → Info
    
    current_scope: int          # Index actuel
    all_symbols: List[SymbolInfo]  # Historique complet
```

#### Opérations

```python
# 1. Déclaration (scope courant uniquement)
declare(name: str, type: str, initialized: bool) → bool
    - Cherche dans scopes[current_scope]
    - Si existe → return False (erreur)
    - Sinon → Ajoute, return True

# 2. Recherche (scope courant vers global)
lookup(name: str) → SymbolInfo | None
    - Boucle de scopes[current_scope] à scopes[0]
    - Retourne le premier trouvé

# 3. Modification d'état
mark_initialized(name: str) → None
    - Cherche dans la pile
    - Met initialized = True

mark_used(name: str) → None
    - Cherche dans la pile
    - Met used = True

# 4. Gestion de scope
enter_scope() → None
    - Incrémente current_scope
    - Ajoute nouveau Dict vide

exit_scope() → List[SymbolInfo]
    - Retourne les symboles du scope courant
    - Décrémente current_scope
    - Supprime le scope
```

### 3. Règles de Type Strictes

#### Opérateurs Arithmétiques

```
✓ int + int   → int     (5 + 3 = 8)
✓ int - int   → int     (5 - 3 = 2)
✓ int * int   → int     (5 * 3 = 15)
✓ int / int   → int     (5 / 3 = 1) [Division entière]

✗ string + int          ERROR
✗ bool + int            ERROR
✗ int + int + string    ERROR (left-assoc : (int+int)+string → string+string : OK!)
```

#### Opérateurs de Concaténation

```
✓ string + string       → string    ("hello" + "world")

✗ string + int          ERROR
✗ string - string       ERROR (minus non supporté)
```

#### Opérateurs Relationnels

```
✓ int > int             → bool      (5 > 3)
✓ int < int             → bool
✓ int == int            → bool
✓ int != int            → bool
✓ int >= int            → bool
✓ int <= int            → bool

✓ string == string      → bool      ("a" == "b")
✓ string != string      → bool

✓ bool == bool          → bool      (true == false)
✓ bool != bool          → bool

✗ int > string          ERROR
✗ bool > int            ERROR (comparaison booléenne invalide)
```

### 4. Inférence de Type (Détails d'Implémentation)

#### Algorithme Pseudo-code

```python
function INFER_TYPE(expr):
    switch (type of expr):
        case Number:
            return "int"
        
        case StringLiteral:
            return "string"
        
        case BoolLiteral:
            return "bool"
        
        case Identifier:
            info = lookup(expr.name)
            if info == NULL:
                WARN("Variable non déclarée")
                return NULL
            if not info.initialized:
                WARN("Variable non initialisée")
            mark_used(expr.name)
            return info.var_type
        
        case BinaryOp:
            left_type = INFER_TYPE(expr.left)
            right_type = INFER_TYPE(expr.right)
            
            if left_type == NULL or right_type == NULL:
                return NULL  # Erreur cascade
            
            if expr.op == '+':
                if left_type == right_type and left_type in ["int", "string"]:
                    return left_type
                ERROR("Types incompatibles pour +")
                return NULL
            
            if expr.op in ['-', '*', '/']:
                if left_type == "int" and right_type == "int":
                    return "int"
                ERROR("Opérateurs arithmétiques requièrent int")
                return NULL
        
        case UnaryOp:
            operand_type = INFER_TYPE(expr.operand)
            if expr.op == '-':
                if operand_type == "int":
                    return "int"
                ERROR("Unaire minus requiert int")
                return NULL
        
        default:
            ERROR("Type d'expression inconnu")
            return NULL
```

### 5. Vérification de Condition

```python
def verify_condition(cond: Condition):
    left_type = infer_type(cond.left)
    right_type = infer_type(cond.right)
    
    # Même type requis
    if left_type != right_type:
        ERROR("Types différents dans la condition")
        return
    
    # Vérifier l'opérateur pour ce type
    valid_ops = VALID_RELOPS.get(left_type, set())
    if cond.operator not in valid_ops:
        ERROR(f"Opérateur '{cond.operator}' invalide pour {left_type}")
        return
    
    # OK
    return
```

### 6. Vérification de Portée (Scope Analysis)

#### Exemple Détaillé

**Code** :
```python
int x;                    // Déclaration globale

if (x > 0) then {
    int y;                // Déclaration locale
    y = 10;
    x = y + 1;            // Accès au parent
}

y = 5;                    // ERREUR : y hors scope
```

**Trace** :
```
Phase globale (level=0):
├─ Déclarer x : int, initialized=False ✓
├─ IfStmt
│  └─ Condition : x > 0
│     └─ Chercher x → Trouvé (level 0) ✓
│
│  enter_scope() → level=1
│  ├─ Déclarer y : int, initialized=False ✓
│  ├─ Assignation y = 10
│  │  └─ Chercher y → Trouvé (level 1) ✓
│  │  └─ mark_initialized(y) ✓
│  ├─ Assignation x = y + 1
│  │  ├─ Chercher x → Trouvé (level 0, parent) ✓
│  │  └─ infer_type(y + 1)
│  │     ├─ Chercher y → Trouvé (level 1) ✓
│  │     ├─ Type(y) = int ✓
│  │     └─ int + int → int ✓
│  exit_scope() → level=0
│
├─ Assignation y = 5
│  └─ Chercher y → NOT FOUND (hors scope) ✗
│     ERROR: "Variable 'y' utilisée avant déclaration"
```

---

## Diagrammes de Transition

### 1. Automate Lexical (État Fini)

```
┌──────┐  [a-zA-Z_]  ┌──────────────┐
│START │────────────→│ IDENTIFIER   │◄─ [a-zA-Z0-9_]*
└──────┘             └──────────────┘
  ↓
  │ [0-9]
  ↓
┌──────┐  [0-9]*
│ NUMBER │────→ fin
└──────┘

┌──────┐  '"'  ┌────────┐  [^"]  ┌────────┐  '"'  ┌────┐
│ START ├─────→│ STRING │◄──────→│ CONTENT│──────→│ EOF│
└──────┘       └────────┘        └────────┘       └────┘

┌──────┐  '/'  ┌────────┐  '*'  ┌──────────┐  '*'  ┌────┐  '/'
│ START ├─────→│ CSTART │──────→│ COMMENT  │──────→│ EOF│─────→ FIN
└──────┘       └────────┘       └──────────┘       └────┘
```

### 2. Arbre de Parsing (Exemple: `int x = 5;`)

```
                           Program
                             │
                    DeclarationStmt
                      /    |    \
                    int    x     5
                   (type) (id)  (expr)
```

### 3. Graphe d'Appels du Parser

```
                       parse()
                         │
                    _parse_statement_list()
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   _parse_      _parse_      _parse_       _parse_
declaration   if_stmt      while_stmt    assignment
        │                │                │
   _parse_expression    _parse_condition   │
        │                │              _parse_
        │             _parse_expression  expression
    _parse_term           │               │
        │             _parse_term      _parse_term
        │                │               │
  _parse_primary     _parse_primary   _parse_primary
```

---

## Tableaux de Synthèse

### Tableau: Complexité Algorithmique

| Phase | Composant | Entrée | Sortie | Temps | Espace |
|-------|-----------|--------|--------|-------|--------|
| Lexical | Tokenization | n chars | m tokens (m ≤ n) | O(n) | O(m) |
| Syntax | Parsing | m tokens | AST (k nodes) | O(m) | O(k) |
| Semantic | Analysis | k nodes | Validation | O(k × d) | O(s + d) |
| | | | | d=depth, s=symbols |

### Tableau: Erreurs Détectées par Phase

| Phase | Type d'Erreur | Exemple |
|-------|---------------|---------|
| **Lexical** | Caractère invalide | `@`, `#`, `$` |
| | Chaîne non fermée | `"hello` |
| **Syntax** | Parenthèse manquante | `if (x > 0 then` |
| | Accolade manquante | `if (...) then { ... ` |
| | Déclaration invalide | `int = 5;` |
| | Opérateur manquant | `int x 5;` |
| **Semantic** | Variable non déclarée | `x = 5;` (pas de `int x`) |
| | Redéclaration | `int x; int x;` |
| | Incompatibilité type | `int x = "hello";` |
| | Opérateur invalide | `string s = x + 1;` |
| | Scope violation | Utiliser une variable hors de son scope |

---

**Document généré automatiquement**  
*Fornit à titre de référence technique*
