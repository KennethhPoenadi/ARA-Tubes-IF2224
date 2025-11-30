# PASCAL-S Compiler

## Identitas Kelompok

**Kelompok AutoRejectAtas**
- Muhammad Syarafi Akmal (13522076)
- Kenneth Poenadi (13523040)
- Bob Kunanda (13523086)
- M. Zahran Ramadhan Ardiana (13523104)

## Deskripsi Program

Compiler untuk bahasa PASCAL-S (subset dari Pascal) dengan kata kunci dalam Bahasa Indonesia. Compiler ini mengimplementasikan tahapan kompilasi dari source code hingga parse tree analysis.

### Milestone 1: Lexical Analysis (Lexer)
Lexer memproses source code Pascal-S dan menghasilkan stream of tokens berdasarkan aturan DFA (Deterministic Finite Automaton).

**Fitur:**
- Tokenisasi berdasarkan DFA rules
- Support keyword Bahasa Indonesia (program, variabel, mulai, selesai, dll)
- Penanganan multi-line comment (`{...}` dan `(*...*)`)
- Deteksi string literal, char literal, dan number
- Penggabungan compound keywords (selain-itu, turun-ke)
- Error handling untuk unclosed comment dan invalid tokens

### Milestone 2: Syntax Analysis (Parser)
Parser menganalisis urutan token dan membangun Parse Tree menggunakan algoritma Recursive Descent berdasarkan grammar PASCAL-S.

**Fitur:**
- 31 fungsi parsing untuk semua konstruksi PASCAL-S
- Validasi struktur sintaks sesuai Context-Free Grammar
- Error handling dengan pesan informatif (posisi token dan expected token)
- Visualisasi Parse Tree dengan ASCII art formatting
- Support lengkap untuk:
  - Program structure (header, declarations, statements)
  - Deklarasi konstanta, tipe, dan variabel
  - Deklarasi prosedur dan fungsi
  - Array types dan range types
  - Control structures (if-then-else, while, for, repeat-until)
  - Assignment statements
  - Expressions dengan operator precedence (relational, arithmetic, logical)
  - Procedure/function calls dengan parameter list

### Milestone 3: Semantic Analysis
Semantic Analyzer memverifikasi makna (semantics) dari parse tree yang sudah dihasilkan, membangun AST (Abstract Syntax Tree), dan melakukan type checking serta scope management.

**Fitur:**
- **AST (Abstract Syntax Tree) Generation:** Mengkonversi parse tree menjadi AST yang lebih ringkas menggunakan Syntax-Directed Translation
- **Symbol Table Management:**
  - `tab` (identifier table): Menyimpan variabel, konstanta, prosedur, fungsi, dan tipe
  - `btab` (block table): Menyimpan informasi block/scope (procedure, function)
  - `atab` (array table): Menyimpan informasi array (bounds, element type, size)
  - Reserved words handling (32 reserved words untuk Bahasa Indonesia)
- **Type Checking:**
  - Primitive types: integer, real, boolean, char, string
  - Array types dengan bounds checking
  - Custom types (user-defined types)
  - Type compatibility checking
  - Implicit conversion (integer ↔ real, char ↔ string)
  - Operator type validation (arithmetic, logical, comparison)
- **Scope Management:**
  - Lexical scoping dengan display stack
  - Nested scope support untuk procedure/function
  - Variable visibility checking
  - Duplicate declaration detection
- **Semantic Validation:**
  - Undeclared identifier detection
  - Type mismatch detection (assignment, operations, function calls)
  - Control flow validation (condition must be boolean)
  - Loop variable validation (must be integer for FOR loop)
- **Decorated AST:**
  - Setiap node memiliki anotasi: `tab_index`, `computed_type`, `scope_level`
  - Referensi ke symbol table untuk code generation
- **Error Reporting:**
  - Semantic error messages dengan line/column info
  - Warning messages untuk suspicious code

## Requirements

- Python 3.8 atau lebih baru
- Tidak ada library eksternal yang diperlukan (pure Python standard library)

## Cara Instalasi dan Penggunaan

### Instalasi

1. Clone repository:
   ```bash
   git clone https://github.com/KennethhPoenadi/ARA-Tubes-IF2224.git
   cd ARA-Tubes-IF2224/Tubes
   ```

2. Tidak ada dependency tambahan yang perlu diinstall (menggunakan Python standard library)

### Penggunaan Compiler (Milestone 1 & 2)

**Format:**
```bash
Jalankan dari root folder

python3 src/compiler.py <input_file>
```

**Input yang didukung:**
- File source code `.pas` (akan di-tokenize otomatis oleh lexer)
- File token list `.txt` (hasil tokenisasi manual atau dari lexer sebelumnya)

**Contoh penggunaan:**

1. Compile dari source code Pascal-S:
   ```bash
   Jalankan dari root folder

   python3 src/compiler.py test/milestone-2/input/test1.pas
   ```

2. Parse dari file token:
   ```bash
   python3 src/compiler.py test/milestone-2/input/test1_tokens.txt
   ```

**Output:**
Parse Tree ditampilkan di terminal dengan format ASCII art. Contoh:
```
<program>
├── <program-header>
│   ├── KEYWORD(program)
│   ├── IDENTIFIER(Hello)
│   └── SEMICOLON(;)
├── <declaration-part>
│   └── <var-declaration>
...
```

Output juga disimpan ke file di `test/milestone-2/output/output<nama_file>.txt`

### Penggunaan Semantic Analyzer (Milestone 3)

**Format:**
```bash
python3 src/ast_printer.py <source_file.pas>
```

**Contoh penggunaan:**

1. Analyze file Pascal-S dengan semantic checking:
   ```bash
   python3 src/ast_printer.py test/milestone-3/input/test1.pas
   ```

2. Test dengan berbagai test case:
   ```bash
   python3 src/ast_printer.py test/milestone-3/input/test2.pas
   python3 src/ast_printer.py test/milestone-3/input/test_brutal.pas
   ```

**Output:**
Program akan menampilkan di terminal:
- ✓ Status tokenization, parsing, AST building, dan semantic analysis
- AST (Abstract Syntax Tree) tanpa anotasi
- Decorated AST dengan anotasi semantic

Output lengkap disimpan ke `test/milestone-3/output/output_<nama_file>.txt` berisi:

1. **Symbol Table (tab):**
   ```
   idx  id                  obj         typ   ref   nrm  lev  adr  link
   ---------------------------------------------------------------------
   0-31 (reserved words)
   32   Hello               program     0     -1    1    0    0    -1
   33   a                   variable    1     -1    1    0    0    32
   34   b                   variable    1     -1    1    0    1    33
   ```

2. **Block Table (btab):**
   ```
   idx  last   lpar   psze   vsze
   ---------------------------------
   0    34     -1     0      2
   ```

3. **Array Table (atab):**
   ```
   atab: (kosong karena tidak ada array)
   ```
   Atau jika ada array:
   ```
   idx  xtyp  etyp  eref   low   high   elsz   size
   -------------------------------------------------
   0    1     1     -1     1     10     1      10
   ```

4. **Decorated AST:**
   ```
   ProgramNode(name: 'Hello')
    ├─ Declarations
    │  ├─ VarDecl('a', type: 'integer') → tab_index:33, type:integer, lev:0
    │  └─ VarDecl('b', type: 'integer') → tab_index:34, type:integer, lev:0
    └─ Block
       ├─ Assign('a' := 5) → type:integer
       ├─ Assign('b' := a+10) → type:integer
       └─ writeln(...) → predefined
   ```

5. **Semantic Errors (jika ada):**
   ```
   SEMANTIC ERRORS:
     - Semantic Error at line 5: Undeclared variable 'x'
     - Semantic Error at line 7: Type mismatch in assignment
   ```

### Penggunaan Lexer Saja (Milestone 1)

Jika ingin menjalankan lexer secara terpisah:

Jalankan dari root folder

```bash
Jalankan dari root folder

python3 src/Lexer_final.py rules/dfa_rules_final.json <source_file.pas>
```

Contoh:
```bash
Jalankan dari root folder

python3 src/Lexer_final.py rules/dfa_rules_final.json test/milestone-1/input/input1.pas
```

Output berupa list of tokens dalam format `TYPE(value)`

## Struktur File

```
Tubes/
├── src/
│   ├── compiler.py         # Main compiler (Milestone 1 & 2: lexer + parser)
│   ├── lexer.py            # Lexer module dengan Indonesian keywords
│   ├── parser.py           # Parser dengan Recursive Descent (31 fungsi)
│   ├── tree_printer.py     # Parse tree printer dengan ASCII art
│   ├── ast_printer.py      # AST printer + Semantic analyzer runner (Milestone 3)
│   ├── ast_builder.py      # AST builder - convert parse tree → AST
│   ├── ast_nodes.py        # AST node class definitions
│   ├── semantic_analyzer.py # Semantic visitor - type & scope checking
│   ├── symbol_table.py     # Symbol table (tab, btab, atab)
│   ├── Lexer_final.py      # Standalone lexer (Milestone 1)
│   └── tokenizer.py        # Token parser untuk .txt files
├── rules/
│   └── dfa_rules_final.json # DFA configuration untuk lexer
├── test/
│   ├── milestone-1/
│   │   ├── input/          # Test source files (.pas)
│   │   └── output/         # Hasil tokenisasi
│   ├── milestone-2/
│   │   ├── input/          # Test files (.pas dan .txt)
│   │   └── output/         # Parse tree results
│   └── milestone-3/
│       ├── input/          # Test files untuk semantic analysis
│       └── output/         # AST + Symbol table results
├── doc/
│   ├── Laporan-1-AutoRejectAtas.pdf  # Laporan Milestone 1
│   ├── Laporan-2-AutoRejectAtas.pdf  # Laporan Milestone 2
│   └── Laporan-3-AutoRejectAtas.pdf  # Laporan Milestone 3
└── running.txt             # Cara menjalankan compiler
```

## Contoh Program Pascal-S

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

## Grammar PASCAL-S

Parser menggunakan Context-Free Grammar untuk PASCAL-S dengan notasi EBNF. Grammar lengkap tersedia di dokumentasi laporan. Beberapa aturan utama:

```ebnf
<program> ::= <program-header> <declaration-part> <compound-statement> "."
<program-header> ::= "program" <identifier> ";"
<declaration-part> ::= { <const-declaration> | <type-declaration> | <var-declaration> | <subprogram-declaration> }
<compound-statement> ::= "mulai" <statement-list> "selesai"
<expression> ::= <simple-expression> [ <relational-operator> <simple-expression> ]
...
```

## Fitur Error Handling

Parser dapat mendeteksi berbagai syntax error dengan pesan yang informatif:

- Missing semicolon
- Unexpected token
- Unclosed comment
- Invalid expression structure
- Type mismatch in declarations

Contoh error message:
```
Syntax error at position 7: unexpected token KEYWORD(mulai), expected SEMICOLON(;)
```

## Testing

### Milestone 2 - Parser Tests
Program telah diuji dengan berbagai test case:
- **test1.pas** - Program sederhana dengan assignment
- **test2.pas** - Fungsi faktorial dengan loop
- **test3.pas** - Array operations dan nested loops
- **test4.pas** - Conditional statements
- **test5.pas** - Kombinasi konstanta, prosedur, fungsi, dan control structures
- **test_brutal.pas** - Comprehensive test case
- **test_error.pas** - Syntax error detection

### Milestone 3 - Semantic Analyzer Tests
Program telah diuji dengan berbagai test case semantic:
- **test1.pas** - Program sederhana dengan assignment dan arithmetic operations
- **test2.pas** - Fungsi faktorial dengan for loop dan type checking
- **test3.pas** - Array operations dengan for dan while loop
- **test4.pas** - Conditional statements (if-then-else)
- **test5.pas** - Program kompleks dengan konstanta, tipe custom, prosedur, fungsi, array, dan control structures
- **test_brutal.pas** - Comprehensive test dengan nested procedures, scoping, dan kombinasi semua fitur
- **test_semantic_error.pas** - Error detection untuk undeclared variables dan type mismatch
- **test_comments.pas** - Testing comment handling dengan semantic analysis

## Pembagian Tugas

### Milestone 1
| Nama                     | NIM      | Tugas                          |
|--------------------------|----------|--------------------------------|
| Muhammad Syarafi Akmal  | 13522076 | DFA Rules, Lexer Implementation, Test Case |
| Kenneth Poenadi         | 13523040 | DFA Rules, Diagram DFA, Laporan |
| M. Zahran Ramadhan      | 13523104 | DFA Rules, Lexer Implementation, Test Case |
| Bob Kunanda             | 13523086 | DFA Rules, Diagram DFA, Laporan |

### Milestone 2
| Nama                     | NIM      | Tugas                          |
|--------------------------|----------|--------------------------------|
| Muhammad Syarafi Akmal  | 13522076 | Parser Implementation, Grammar Design, Test Case |
| Kenneth Poenadi         | 13523040 | Parser Implementation, Tree Printer, Laporan |
| M. Zahran Ramadhan      | 13523104 | Lexer Modification, Error Handling, Test Case |
| Bob Kunanda             | 13523086 | Grammar Design, Integration, Laporan |

### Milestone 3
| Nama                     | NIM      | Tugas                          |
|--------------------------|----------|--------------------------------|
| Muhammad Syarafi Akmal  | 13522076 | AST Builder, Semantic Visitor, Test Case |
| Kenneth Poenadi         | 13523040 | Symbol Table, AST Nodes, Laporan |
| M. Zahran Ramadhan      | 13523104 | Type Checking, Error Handling, Test Case |
| Bob Kunanda             | 13523086 | Scope Checking, AST Printer, Laporan |

## License

This project is created for educational purposes as part of IF2224 - Formal Languages and Automata Theory course at ITB.
