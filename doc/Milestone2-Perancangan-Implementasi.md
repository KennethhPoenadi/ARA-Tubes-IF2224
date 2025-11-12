# Perancangan & Implementasi Milestone 2
## Parser untuk Bahasa Pascal-S

---

## 1. Pendahuluan

Milestone 2 dari proyek compiler Pascal-S ini berfokus pada implementasi **Syntax Analyzer (Parser)** yang menggunakan teknik **Recursive Descent Parsing**. Parser ini menerima input berupa token stream dari lexer (Milestone 1) dan menghasilkan **Parse Tree** yang merepresentasikan struktur sintaksis dari program Pascal-S.

### 1.1 Tujuan
- Memvalidasi urutan token sesuai dengan grammar bahasa Pascal-S
- Membangun representasi hierarkis (parse tree) dari struktur program
- Mendeteksi dan melaporkan kesalahan sintaksis dengan pesan yang informatif

### 1.2 Arsitektur Sistem

```
┌─────────────────┐
│  Source Code    │
│  (.pas file)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     LEXER       │ ◄── DFA Rules (dfa_rules_final.json)
│  (Milestone 1)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Token Stream   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     PARSER      │ ◄── Grammar (hardcoded dalam parser.py)
│  (Milestone 2)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Parse Tree    │
└─────────────────┘
```

---

## 2. Spesifikasi Grammar Pascal-S

Grammar yang diimplementasikan dalam parser ini didefinisikan menggunakan notasi **Extended Backus-Naur Form (EBNF)**. Berikut adalah grammar lengkap untuk bahasa Pascal-S dengan keyword Bahasa Indonesia:

### 2.1 Program Structure

```ebnf
<program> ::= <program-header> <declaration-part> <compound-statement> "."

<program-header> ::= "program" IDENTIFIER ";"

<declaration-part> ::= {<const-declaration>}
                       {<type-declaration>}
                       {<var-declaration>}
                       {<subprogram-declaration>}
```

### 2.2 Declarations

#### Constant Declaration
```ebnf
<const-declaration> ::= "konstanta" <const-assignment> {";" <const-assignment>} ";"

<const-assignment> ::= IDENTIFIER "=" <constant-value>

<constant-value> ::= NUMBER | CHAR_LITERAL | STRING_LITERAL | IDENTIFIER
```

#### Type Declaration
```ebnf
<type-declaration> ::= "tipe" <type-assignment> {";" <type-assignment>} ";"

<type-assignment> ::= IDENTIFIER "=" <type>

<type> ::= <simple-type> | <array-type> | IDENTIFIER

<simple-type> ::= "integer" | "real" | "boolean" | "char" | "string"

<array-type> ::= "larik" "[" <range> "]" "dari" <type>

<range> ::= <expression> ".." <expression>
```

#### Variable Declaration
```ebnf
<var-declaration> ::= "variabel" <var-group> {";" <var-group>} ";"

<var-group> ::= <identifier-list> ":" <type>

<identifier-list> ::= IDENTIFIER {"," IDENTIFIER}
```

### 2.3 Subprogram Declarations

```ebnf
<subprogram-declaration> ::= <procedure-declaration> | <function-declaration>

<procedure-declaration> ::= "prosedur" IDENTIFIER [<formal-parameter-list>] ";"
                            <block> ";"

<function-declaration> ::= "fungsi" IDENTIFIER [<formal-parameter-list>] ":" <type> ";"
                           <block> ";"

<formal-parameter-list> ::= "(" <parameter-group> {";" <parameter-group>} ")"

<parameter-group> ::= <identifier-list> ":" <type>

<block> ::= <declaration-part> <compound-statement>
```

### 2.4 Statements

```ebnf
<compound-statement> ::= "mulai" <statement-list> "selesai"

<statement-list> ::= <statement> {";" <statement>}

<statement> ::= <assignment-statement>
              | <procedure-call>
              | <compound-statement>
              | <if-statement>
              | <while-statement>
              | <for-statement>
              | <repeat-statement>
              | <empty>

<assignment-statement> ::= IDENTIFIER ["[" <expression> "]"] ":=" <expression>

<procedure-call> ::= (IDENTIFIER | <builtin-procedure>) ["(" <parameter-list> ")"]

<builtin-procedure> ::= "writeln" | "write" | "readln" | "read"

<parameter-list> ::= <expression> {"," <expression>}
```

### 2.5 Control Structures

```ebnf
<if-statement> ::= "jika" <expression> "maka" <statement>
                   ["selain-itu" <statement>]

<while-statement> ::= "selama" <expression> "lakukan" <statement>

<for-statement> ::= "untuk" IDENTIFIER ":=" <expression>
                    ("ke" | "turun-ke") <expression>
                    "lakukan" <statement>

<repeat-statement> ::= "ulangi" <statement-list> "sampai" <expression>
```

### 2.6 Expressions

```ebnf
<expression> ::= <simple-expression> [<relational-operator> <simple-expression>]

<simple-expression> ::= ["+" | "-"] <term> {("+" | "-" | "atau") <term>}

<term> ::= <factor> {("*" | "/" | "bagi" | "mod" | "dan") <factor>}

<factor> ::= IDENTIFIER ["[" <expression> "]" | "(" <parameter-list> ")"]
           | NUMBER
           | CHAR_LITERAL
           | STRING_LITERAL
           | "(" <expression> ")"
           | "tidak" <factor>

<relational-operator> ::= "=" | "<>" | "<" | "<=" | ">" | ">="
```

### 2.7 Lexical Elements

```ebnf
IDENTIFIER ::= LETTER {LETTER | DIGIT | "_"}

NUMBER ::= DIGIT {DIGIT} ["." DIGIT {DIGIT}]

CHAR_LITERAL ::= "'" CHARACTER "'"

STRING_LITERAL ::= "'" {CHARACTER} "'"

LETTER ::= "a".."z" | "A".."Z"

DIGIT ::= "0".."9"
```

---

## 3. Implementasi Recursive Descent Parser

### 3.1 Struktur Kelas Parser

Parser diimplementasikan dalam file `src/parser.py` dengan struktur sebagai berikut:

```python
class Token:
    def __init__(self, token_type, value):
        self.type = token_type
        self.value = value

class Parser:
    def __init__(self, tokens):
        self.tokens = [Token(t[0], t[1]) for t in tokens]
        self.pos = 0
        self.current_token = self.tokens[0] if self.tokens else None
```

**Atribut:**
- `tokens`: List dari objek Token hasil lexical analysis
- `pos`: Posisi current token dalam stream
- `current_token`: Token yang sedang diproses

### 3.2 Fungsi Utility

#### 3.2.1 `peek(offset=0)`
Melihat token di posisi tertentu tanpa mengubah posisi parser.
```python
def peek(self, offset=0):
    index = self.pos + offset
    if index < len(self.tokens):
        return self.tokens[index]
    return None
```

#### 3.2.2 `advance()`
Memindahkan posisi parser ke token berikutnya.
```python
def advance(self):
    if self.pos < len(self.tokens):
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None
    return self.current_token
```

#### 3.2.3 `match(token_type, value=None)`
Mengecek apakah current token sesuai dengan tipe dan nilai yang diharapkan.
```python
def match(self, token_type, value=None):
    if not self.current_token:
        return False
    if self.current_token.type != token_type:
        return False
    if value and self.current_token.value.lower() != value.lower():
        return False
    return True
```

#### 3.2.4 `expect(token_type, value=None)`
Memastikan current token sesuai dengan yang diharapkan, jika tidak akan throw error.
```python
def expect(self, token_type, value=None):
    if not self.current_token:
        self.error(f"Expected {token_type}, but reached end of input")
    if self.current_token.type != token_type:
        expected_str = f"{token_type}({self.get_expected_value(token_type)})"
        self.error(f"unexpected token {self.current_token.type}({self.current_token.value}), expected {expected_str}")
    if value and self.current_token.value.lower() != value.lower():
        self.error(f"unexpected token {self.current_token.value}, expected {value}")
    token = self.current_token
    self.advance()
    return token
```

### 3.3 Fungsi Parsing untuk Setiap Non-Terminal

Setiap non-terminal dalam grammar diimplementasikan sebagai fungsi parsing terpisah. Berikut adalah contoh-contoh implementasinya:

#### 3.3.1 Program Structure

**`parse_program()`** - Entry point parsing
```python
def parse_program(self):
    node = {"type": "<program>", "children": []}
    node["children"].append(self.parse_program_header())
    node["children"].append(self.parse_declaration_part())
    node["children"].append(self.parse_compound_statement())
    node["children"].append(self.expect("DOT"))
    return node
```

**`parse_program_header()`**
```python
def parse_program_header(self):
    node = {"type": "<program-header>", "children": []}
    node["children"].append(self.expect("KEYWORD", "program"))
    node["children"].append(self.expect("IDENTIFIER"))
    node["children"].append(self.expect("SEMICOLON"))
    return node
```

#### 3.3.2 Declaration Part

**`parse_declaration_part()`**
```python
def parse_declaration_part(self):
    node = {"type": "<declaration-part>", "children": []}

    while self.match("KEYWORD", "konstanta"):
        node["children"].append(self.parse_const_declaration())

    while self.match("KEYWORD", "tipe"):
        node["children"].append(self.parse_type_declaration())

    while self.match("KEYWORD", "variabel"):
        node["children"].append(self.parse_var_declaration())

    while self.match("KEYWORD", "prosedur") or self.match("KEYWORD", "fungsi"):
        node["children"].append(self.parse_subprogram_declaration())

    return node
```

**`parse_var_declaration()`**
```python
def parse_var_declaration(self):
    node = {"type": "<var-declaration>", "children": []}
    node["children"].append(self.expect("KEYWORD", "variabel"))

    while True:
        node["children"].append(self.parse_identifier_list())
        node["children"].append(self.expect("COLON"))
        node["children"].append(self.parse_type())
        node["children"].append(self.expect("SEMICOLON"))

        if not self.match("IDENTIFIER"):
            break

    return node
```

#### 3.3.3 Statements

**`parse_statement()`** - Menentukan jenis statement berdasarkan lookahead
```python
def parse_statement(self):
    if self.match("KEYWORD", "mulai"):
        return self.parse_compound_statement()
    elif self.match("KEYWORD", "jika"):
        return self.parse_if_statement()
    elif self.match("KEYWORD", "selama"):
        return self.parse_while_statement()
    elif self.match("KEYWORD", "untuk"):
        return self.parse_for_statement()
    elif self.match("KEYWORD", "ulangi"):
        return self.parse_repeat_statement()
    elif self.match("IDENTIFIER"):
        peek = self.peek(1)
        if peek and (peek.type == "ASSIGN_OPERATOR" or peek.type == "LBRACKET"):
            return self.parse_assignment_statement()
        else:
            return self.parse_procedure_call()
    elif self.match("KEYWORD") and self.current_token.value.lower() in ["writeln", "write", "readln", "read"]:
        return self.parse_procedure_call()
    else:
        return {"type": "<empty-statement>", "children": []}
```

**`parse_if_statement()`**
```python
def parse_if_statement(self):
    node = {"type": "<if-statement>", "children": []}
    node["children"].append(self.expect("KEYWORD", "jika"))
    node["children"].append(self.parse_expression())
    node["children"].append(self.expect("KEYWORD", "maka"))
    node["children"].append(self.parse_statement())

    if self.match("KEYWORD", "selain-itu"):
        node["children"].append(self.expect("KEYWORD", "selain-itu"))
        node["children"].append(self.parse_statement())

    return node
```

**`parse_for_statement()`**
```python
def parse_for_statement(self):
    node = {"type": "<for-statement>", "children": []}
    node["children"].append(self.expect("KEYWORD", "untuk"))
    node["children"].append(self.expect("IDENTIFIER"))
    node["children"].append(self.expect("ASSIGN_OPERATOR"))
    node["children"].append(self.parse_expression())

    if self.match("KEYWORD", "ke"):
        node["children"].append(self.expect("KEYWORD", "ke"))
    elif self.match("KEYWORD", "turun-ke"):
        node["children"].append(self.expect("KEYWORD", "turun-ke"))
    else:
        self.error("Expected 'ke' or 'turun-ke'")

    node["children"].append(self.parse_expression())
    node["children"].append(self.expect("KEYWORD", "lakukan"))
    node["children"].append(self.parse_statement())
    return node
```

#### 3.3.4 Expressions

**`parse_expression()`**
```python
def parse_expression(self):
    node = {"type": "<expression>", "children": []}
    node["children"].append(self.parse_simple_expression())

    if self.match("RELATIONAL_OPERATOR"):
        node["children"].append(self.current_token)
        self.advance()
        node["children"].append(self.parse_simple_expression())

    return node
```

**`parse_simple_expression()`**
```python
def parse_simple_expression(self):
    node = {"type": "<simple-expression>", "children": []}

    # Unary + atau -
    if self.match("ARITHMETIC_OPERATOR") and self.current_token.value in ["+", "-"]:
        node["children"].append(self.current_token)
        self.advance()

    node["children"].append(self.parse_term())

    # Binary + atau - atau "atau"
    while (self.match("ARITHMETIC_OPERATOR") and self.current_token.value in ["+", "-"]) or self.match("LOGICAL_OPERATOR", "atau"):
        node["children"].append(self.current_token)
        self.advance()
        node["children"].append(self.parse_term())

    return node
```

**`parse_term()`**
```python
def parse_term(self):
    node = {"type": "<term>", "children": []}
    node["children"].append(self.parse_factor())

    while (self.match("ARITHMETIC_OPERATOR") and self.current_token.value in ["*", "/"]) or \
          self.match("ARITHMETIC_OPERATOR", "bagi") or \
          self.match("ARITHMETIC_OPERATOR", "mod") or \
          self.match("LOGICAL_OPERATOR", "dan"):
        node["children"].append(self.current_token)
        self.advance()
        node["children"].append(self.parse_factor())

    return node
```

**`parse_factor()`** - Level terendah dari expression
```python
def parse_factor(self):
    node = {"type": "<factor>", "children": []}

    if self.match("IDENTIFIER"):
        peek = self.peek(1)
        if peek and peek.type == "LPARENTHESIS":
            node["children"].append(self.parse_function_call())
        elif peek and peek.type == "LBRACKET":
            node["children"].append(self.expect("IDENTIFIER"))
            node["children"].append(self.expect("LBRACKET"))
            node["children"].append(self.parse_expression())
            node["children"].append(self.expect("RBRACKET"))
        else:
            node["children"].append(self.expect("IDENTIFIER"))
    elif self.match("NUMBER"):
        node["children"].append(self.expect("NUMBER"))
    elif self.match("CHAR_LITERAL"):
        node["children"].append(self.expect("CHAR_LITERAL"))
    elif self.match("STRING_LITERAL"):
        node["children"].append(self.expect("STRING_LITERAL"))
    elif self.match("LPARENTHESIS"):
        node["children"].append(self.expect("LPARENTHESIS"))
        node["children"].append(self.parse_expression())
        node["children"].append(self.expect("RPARENTHESIS"))
    elif self.match("LOGICAL_OPERATOR", "tidak"):
        node["children"].append(self.expect("LOGICAL_OPERATOR", "tidak"))
        node["children"].append(self.parse_factor())
    else:
        self.error(f"Unexpected token in factor: {self.current_token}")

    return node
```

---

## 4. Representasi Parse Tree

Parse tree direpresentasikan sebagai nested dictionary dengan struktur:
```python
{
    "type": "<non-terminal>",
    "children": [child1, child2, ...]
}
```

- **Non-terminal nodes**: Dictionary dengan key `"type"` dan `"children"`
- **Terminal nodes (tokens)**: Objek Token dengan atribut `type` dan `value`

### 4.1 Tree Printer

Untuk visualisasi parse tree, digunakan `tree_printer.py` yang menghasilkan output ASCII tree:

```python
def print_tree(node, indent="", is_last=True):
    if node is None:
        return

    connector = "└── " if is_last else "├── "

    if isinstance(node, dict):
        if "type" in node:
            print(indent + connector + node["type"])
            children = node.get("children", [])
            new_indent = indent + ("    " if is_last else "│   ")

            for i, child in enumerate(children):
                print_tree(child, new_indent, i == len(children) - 1)
    else:
        token_str = f"{node.type}({node.value})"
        print(indent + connector + token_str)
```

---

## 5. Contoh Parsing

### 5.1 Input Program

File: `test/milestone-2/test1.pas`
```pascal
program Hello;

variabel
  a, b: integer;

mulai
  a := 5;
  b := a + 10;
  writeln('Result = ', b);
selesai.
```

### 5.2 Token Stream (dari Lexer)

```
KEYWORD(program)
IDENTIFIER(Hello)
SEMICOLON(;)
KEYWORD(variabel)
IDENTIFIER(a)
COMMA(,)
IDENTIFIER(b)
COLON(:)
KEYWORD(integer)
SEMICOLON(;)
KEYWORD(mulai)
IDENTIFIER(a)
ASSIGN_OPERATOR(:=)
NUMBER(5)
SEMICOLON(;)
IDENTIFIER(b)
ASSIGN_OPERATOR(:=)
IDENTIFIER(a)
ARITHMETIC_OPERATOR(+)
NUMBER(10)
SEMICOLON(;)
KEYWORD(writeln)
LPARENTHESIS(()
STRING_LITERAL(Result = )
COMMA(,)
IDENTIFIER(b)
RPARENTHESIS())
SEMICOLON(;)
KEYWORD(selesai)
DOT(.)
```

### 5.3 Parse Tree Output

```
└── <program>
    ├── <program-header>
    │   ├── KEYWORD(program)
    │   ├── IDENTIFIER(Hello)
    │   └── SEMICOLON(;)
    ├── <declaration-part>
    │   └── <var-declaration>
    │       ├── KEYWORD(variabel)
    │       ├── <identifier-list>
    │       │   ├── IDENTIFIER(a)
    │       │   ├── COMMA(,)
    │       │   └── IDENTIFIER(b)
    │       ├── COLON(:)
    │       ├── <type>
    │       │   └── KEYWORD(integer)
    │       └── SEMICOLON(;)
    ├── <compound-statement>
    │   ├── KEYWORD(mulai)
    │   ├── <statement-list>
    │   │   ├── <assignment-statement>
    │   │   │   ├── IDENTIFIER(a)
    │   │   │   ├── ASSIGN_OPERATOR(:=)
    │   │   │   └── <expression>
    │   │   │       └── <simple-expression>
    │   │   │           └── <term>
    │   │   │               └── <factor>
    │   │   │                   └── NUMBER(5)
    │   │   ├── SEMICOLON(;)
    │   │   ├── <assignment-statement>
    │   │   │   ├── IDENTIFIER(b)
    │   │   │   ├── ASSIGN_OPERATOR(:=)
    │   │   │   └── <expression>
    │   │   │       └── <simple-expression>
    │   │   │           ├── <term>
    │   │   │           │   └── <factor>
    │   │   │           │       └── IDENTIFIER(a)
    │   │   │           ├── ARITHMETIC_OPERATOR(+)
    │   │   │           └── <term>
    │   │   │               └── <factor>
    │   │   │                   └── NUMBER(10)
    │   │   ├── SEMICOLON(;)
    │   │   └── <procedure/function-call>
    │   │       ├── KEYWORD(writeln)
    │   │       ├── LPARENTHESIS(()
    │   │       ├── <parameter-list>
    │   │       │   ├── <expression>
    │   │       │   │   └── <simple-expression>
    │   │       │   │       └── <term>
    │   │       │   │           └── <factor>
    │   │       │   │               └── STRING_LITERAL(Result = )
    │   │       │   ├── COMMA(,)
    │   │       │   └── <expression>
    │   │       │       └── <simple-expression>
    │   │       │           └── <term>
    │   │       │               └── <factor>
    │   │       │                   └── IDENTIFIER(b)
    │   │       └── RPARENTHESIS())
    │   ├── SEMICOLON(;)
    │   └── KEYWORD(selesai)
    └── DOT(.)
```

---

## 6. Error Handling

Parser memiliki mekanisme error handling yang informatif:

### 6.1 Unexpected Token Error

Ketika token tidak sesuai dengan yang diharapkan:
```
Syntax error at position 15: unexpected token IDENTIFIER(mulai), expected SEMICOLON(;)
```

### 6.2 Premature End of Input

Ketika token habis sebelum parsing selesai:
```
Syntax error at position 42: Expected KEYWORD, but reached end of input
```

### 6.3 Invalid Syntax

Ketika struktur sintaksis tidak valid:
```
Syntax error at position 23: Expected 'ke' or 'turun-ke'
```

---

## 7. Flow Eksekusi Program

### 7.1 Main Compiler (`compiler.py`)

```python
def main():
    # 1. Read source file
    source_file = sys.argv[1]

    # 2. Lexical Analysis
    if file_ext == '.pas':
        tokens = tokenize_from_file(dfa_rules, source_file)

    # 3. Syntax Analysis
    parser = Parser(tokens)
    parse_tree = parser.parse()

    # 4. Print Parse Tree
    print_tree(parse_tree)
```

### 7.2 Diagram Alir Parsing

```
┌─────────────────────────┐
│   Initialization        │
│   - Load tokens         │
│   - Set pos = 0         │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   parse_program()       │
│   (Entry Point)         │
└───────────┬─────────────┘
            │
            ├──────────────────────────┐
            │                          │
            ▼                          ▼
┌───────────────────────┐  ┌──────────────────────┐
│ parse_program_header()│  │ parse_declaration_   │
│ - expect "program"    │  │ part()               │
│ - expect IDENTIFIER   │  │ - const declarations │
│ - expect ";"          │  │ - type declarations  │
└───────────────────────┘  │ - var declarations   │
                           │ - subprogram decl    │
                           └──────────┬───────────┘
                                      │
                                      ▼
                           ┌──────────────────────┐
                           │ parse_compound_      │
                           │ statement()          │
                           │ - statement list     │
                           └──────────┬───────────┘
                                      │
                                      ▼
                           ┌──────────────────────┐
                           │ expect "."           │
                           └──────────────────────┘
```

---

## 8. Fitur-Fitur Utama Parser

### 8.1 Lookahead Mechanism

Parser menggunakan `peek()` untuk melihat token berikutnya tanpa mengubah state:
```python
peek = self.peek(1)
if peek and peek.type == "LPARENTHESIS":
    # Function call
else:
    # Variable reference
```

### 8.2 Left Recursion Elimination

Grammar dirancang tanpa left recursion. Contoh untuk expression:
```
Original (left-recursive):
<expression> ::= <expression> "+" <term> | <term>

Transformed:
<expression> ::= <term> {"+" <term>}
```

Implementasi:
```python
def parse_simple_expression(self):
    node["children"].append(self.parse_term())
    while self.match("ARITHMETIC_OPERATOR", "+"):
        node["children"].append(self.current_token)
        self.advance()
        node["children"].append(self.parse_term())
```

### 8.3 Operator Precedence

Hierarki expression parsing mengikuti precedence operator:
1. **Factor** (tertinggi): literals, identifiers, parenthesis, unary operators
2. **Term**: *, /, mod, bagi, dan
3. **Simple Expression**: +, -, atau
4. **Expression** (terendah): relational operators (=, <>, <, >, <=, >=)

### 8.4 Support untuk Keyword Bahasa Indonesia

Parser mendukung keyword dalam Bahasa Indonesia:
- `program` → program
- `variabel` → variable declaration
- `konstanta` → constant declaration
- `tipe` → type declaration
- `prosedur` → procedure
- `fungsi` → function
- `mulai` → begin
- `selesai` → end
- `jika`, `maka`, `selain-itu` → if, then, else
- `selama`, `lakukan` → while, do
- `untuk`, `ke`, `turun-ke` → for, to, downto
- `ulangi`, `sampai` → repeat, until
- `larik`, `dari` → array, of
- `dan`, `atau`, `tidak` → and, or, not

---

## 9. Testing

### 9.1 Test Cases

Beberapa test case yang telah diuji:

1. **test1.pas** - Simple variable assignment
2. **test2.pas** - Function declaration dengan recursive call
3. **test3.pas** - Array operations
4. **test4.pas** - Control structures (if, while, for)
5. **test5.pas** - Nested procedures
6. **test_error.pas** - Error handling test

### 9.2 Cara Menjalankan Test

```bash
# Test individual file
python3 compiler.py test/milestone-2/test1.pas

# Test dengan token file
python3 compiler.py test/tokens.txt
```

### 9.3 Expected Output

Setiap test case harus menghasilkan:
- ✅ Parse tree yang valid (jika input benar)
- ❌ Error message yang informatif (jika input salah)

---

## 10. Perbandingan dengan Milestone 1

| Aspek | Milestone 1 (Lexer) | Milestone 2 (Parser) |
|-------|---------------------|----------------------|
| **Input** | Source code (.pas) | Token stream |
| **Output** | Token stream | Parse tree |
| **Fokus** | Lexical analysis | Syntax analysis |
| **Teknik** | DFA (Finite Automaton) | Recursive Descent |
| **Error** | Lexical errors | Syntax errors |
| **Representasi** | Linear (sequence) | Hierarkis (tree) |

---

## 11. Kesimpulan

Parser yang telah diimplementasikan memiliki karakteristik:

### 11.1 Kelebihan
- ✅ **Mudah dipahami**: Setiap production rule → satu fungsi
- ✅ **Modular**: Fungsi parsing terpisah untuk setiap non-terminal
- ✅ **Error handling yang baik**: Pesan error informatif dengan posisi
- ✅ **Extensible**: Mudah menambahkan fitur baru
- ✅ **Support Indonesian keywords**: Sesuai dengan spesifikasi Pascal-S

### 11.2 Keterbatasan
- ⚠️ **Tidak mendukung left-recursive grammar** (sudah diatasi dengan transformasi)
- ⚠️ **Membutuhkan lookahead**: Beberapa kasus perlu `peek()` untuk disambiguasi
- ⚠️ **Performance**: O(n) untuk input yang valid, bisa lebih lambat untuk error recovery

### 11.3 Pengembangan Selanjutnya (Future Work)
- Semantic analysis (type checking, scope checking)
- Intermediate code generation
- Optimization
- Code generation (target assembly/machine code)

---

## 12. Referensi Implementasi

### 12.1 File-File Utama

- **[compiler.py](../compiler.py)** - Main program untuk compile
- **[src/parser.py](../src/parser.py)** - Implementasi Recursive Descent Parser
- **[src/lexer.py](../src/lexer.py)** - Lexer dari Milestone 1
- **[src/tree_printer.py](../src/tree_printer.py)** - Visualisasi parse tree
- **[rules/dfa_rules_final.json](../rules/dfa_rules_final.json)** - DFA rules untuk lexer

### 12.2 Test Files

- **test/milestone-2/*** - Test cases untuk parser
- **test/milestone-1/*** - Test cases untuk lexer

---

## Lampiran A: Daftar Fungsi Parsing Lengkap

| Fungsi | Non-Terminal | Lokasi |
|--------|--------------|--------|
| `parse_program()` | `<program>` | parser.py:68 |
| `parse_program_header()` | `<program-header>` | parser.py:76 |
| `parse_declaration_part()` | `<declaration-part>` | parser.py:83 |
| `parse_const_declaration()` | `<const-declaration>` | parser.py:101 |
| `parse_type_declaration()` | `<type-declaration>` | parser.py:124 |
| `parse_var_declaration()` | `<var-declaration>` | parser.py:139 |
| `parse_identifier_list()` | `<identifier-list>` | parser.py:154 |
| `parse_type()` | `<type>` | parser.py:164 |
| `parse_array_type()` | `<array-type>` | parser.py:184 |
| `parse_range()` | `<range>` | parser.py:194 |
| `parse_subprogram_declaration()` | `<subprogram-declaration>` | parser.py:201 |
| `parse_procedure_declaration()` | `<procedure-declaration>` | parser.py:209 |
| `parse_function_declaration()` | `<function-declaration>` | parser.py:222 |
| `parse_formal_parameter_list()` | `<formal-parameter-list>` | parser.py:237 |
| `parse_parameter_group()` | `<parameter-group>` | parser.py:250 |
| `parse_block()` | `<block>` | parser.py:257 |
| `parse_compound_statement()` | `<compound-statement>` | parser.py:263 |
| `parse_statement_list()` | `<statement-list>` | parser.py:270 |
| `parse_statement()` | `<statement>` | parser.py:281 |
| `parse_assignment_statement()` | `<assignment-statement>` | parser.py:303 |
| `parse_if_statement()` | `<if-statement>` | parser.py:316 |
| `parse_while_statement()` | `<while-statement>` | parser.py:329 |
| `parse_for_statement()` | `<for-statement>` | parser.py:337 |
| `parse_repeat_statement()` | `<repeat-statement>` | parser.py:356 |
| `parse_procedure_call()` | `<procedure/function-call>` | parser.py:364 |
| `parse_parameter_list()` | `<parameter-list>` | parser.py:381 |
| `parse_expression()` | `<expression>` | parser.py:391 |
| `parse_simple_expression()` | `<simple-expression>` | parser.py:402 |
| `parse_term()` | `<term>` | parser.py:418 |
| `parse_factor()` | `<factor>` | parser.py:429 |
| `parse_function_call()` | `<function-call>` | parser.py:461 |

---

**Dokumen ini menjelaskan perancangan dan implementasi lengkap dari Parser untuk bahasa Pascal-S dengan teknik Recursive Descent Parsing.**
