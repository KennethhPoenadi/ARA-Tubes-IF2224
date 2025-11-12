# Milestone 2 - Syntax Analyzer (Parser)

## Quick Reference

### Menjalankan Parser

```bash
# Compile program Pascal-S (.pas)
python3 compiler.py test/milestone-2/test1.pas

# Atau dari token file (.txt)
python3 compiler.py test/tokens.txt
```

### Struktur Grammar

Parser menggunakan **Recursive Descent** dengan grammar yang di-hardcode dalam `src/parser.py`.

#### Grammar Utama (Top-Level)

```ebnf
<program> ::= <program-header> <declaration-part> <compound-statement> "."
```

#### Keyword Bahasa Indonesia

| Keyword | Fungsi |
|---------|--------|
| `program` | Program header |
| `variabel` | Deklarasi variabel |
| `konstanta` | Deklarasi konstanta |
| `tipe` | Deklarasi tipe |
| `fungsi` | Deklarasi fungsi |
| `prosedur` | Deklarasi prosedur |
| `mulai` | Begin block |
| `selesai` | End block |
| `jika`, `maka`, `selain-itu` | If-then-else |
| `selama`, `lakukan` | While loop |
| `untuk`, `ke`, `turun-ke` | For loop |
| `ulangi`, `sampai` | Repeat-until |
| `larik`, `dari` | Array type |
| `dan`, `atau`, `tidak` | Logical operators |

### Contoh Program Pascal-S

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

### Output Parse Tree

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
    ...
```

## Dokumentasi Lengkap

Lihat [Milestone2-Perancangan-Implementasi.md](Milestone2-Perancangan-Implementasi.md) untuk:
- Spesifikasi grammar lengkap (EBNF)
- Detail implementasi Recursive Descent Parser
- Penjelasan setiap fungsi parsing
- Contoh-contoh parse tree
- Error handling

## Test Cases

```bash
# Test 1 - Simple program
python3 compiler.py test/milestone-2/test1.pas

# Test 2 - Function dengan for loop
python3 compiler.py test/milestone-2/test2.pas

# Test 3 - Array operations
python3 compiler.py test/milestone-2/test3.pas

# Test 4 - Control structures
python3 compiler.py test/milestone-2/test4.pas

# Test 5 - Nested procedures
python3 compiler.py test/milestone-2/test5.pas

# Test error handling
python3 compiler.py test/milestone-2/test_error.pas
```

## Fitur Parser

- ✅ Recursive Descent Parsing
- ✅ Grammar di-hardcode dalam program
- ✅ Input PASCAL-S → Lexer → Parser
- ✅ Error handling dengan pesan informatif
- ✅ Parse tree visualization
- ✅ Support keyword Bahasa Indonesia
- ✅ Support untuk:
  - Variable, constant, type declarations
  - Function dan procedure declarations
  - Array types
  - Control structures (if, while, for, repeat)
  - Expressions dengan operator precedence
  - Nested blocks

## Arsitektur

```
Source Code (.pas)
        ↓
    LEXER (DFA)
        ↓
   Token Stream
        ↓
   PARSER (Recursive Descent)
        ↓
   Parse Tree
```

## File Penting

- `src/parser.py` - Implementasi parser
- `src/lexer.py` - Lexer dari Milestone 1
- `src/tree_printer.py` - Visualisasi parse tree
- `compiler.py` - Main program
- `rules/dfa_rules_final.json` - DFA rules untuk lexer
