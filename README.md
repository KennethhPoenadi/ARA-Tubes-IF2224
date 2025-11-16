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

### Penggunaan Compiler (Milestone 2)

**Format:**
```bash
Jalankan dari root folder:

python3 src/compiler.py <input_file>
```

**Input yang didukung:**
- File source code `.pas` (akan di-tokenize otomatis oleh lexer)
- File token list `.txt` (hasil tokenisasi manual atau dari lexer sebelumnya)

**Contoh penggunaan:**

1. Compile dari source code Pascal-S:
   ```bash
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

### Penggunaan Lexer Saja (Milestone 1)

Jika ingin menjalankan lexer secara terpisah:

```bash
python3 src/Lexer_final.py rules/dfa_rules_final.json <source_file.pas>
```

Contoh:
```bash
python3 src/Lexer_final.py rules/dfa_rules_final.json test/milestone-1/input/input1.pas
```

Output berupa list of tokens dalam format `TYPE(value)`

## Struktur File

```
Tubes/
├── src/
│   ├── compiler.py         # Main compiler program (integrates lexer + parser)
│   ├── lexer.py            # Lexer module dengan Indonesian keywords
│   ├── parser.py           # Parser dengan Recursive Descent (31 fungsi)
│   ├── tree_printer.py     # Parse tree printer dengan ASCII art
│   ├── Lexer_final.py      # Standalone lexer (Milestone 1)
│   └── tokenizer.py        # Token parser untuk .txt files
├── rules/
│   └── dfa_rules_final.json # DFA configuration untuk lexer
├── test/
│   ├── milestone-1/
│   │   ├── input/          # Test source files (.pas)
│   │   └── output/         # Hasil tokenisasi
│   └── milestone-2/
│       ├── input/          # Test files (.pas dan .txt)
│       └── output/         # Parse tree results
└── doc/
    └── Laporan-2-AutoRejectAtas.pdf  # Laporan Milestone 2
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

Program telah diuji dengan berbagai test case:
- **test1.pas** - Program sederhana dengan assignment
- **test2.pas** - Fungsi faktorial dengan loop
- **test3.pas** - Array operations dan nested loops
- **test4.pas** - Conditional statements
- **test5.pas** - Kombinasi konstanta, prosedur, fungsi, dan control structures
- **test_brutal.pas** - Comprehensive test case
- **test_error.pas** - Syntax error detection

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

## Referensi

1. "PASCAL-S: A Subset and its implementation" - http://pascal.hansotten.com/uploads/pascals/PASCAL-S%20A%20subset%20and%20its%20Implementation%20012.pdf
2. N. Wirth, "The Programming Language Pascal (Revised Report)", ETH Zurich, 1973
3. "Recursive Descent Parser" - GeeksforGeeks
4. "Let's Build A Simple Interpreter. Part 7: Abstract Syntax Trees" - Ruslan Spivak

## License

This project is created for educational purposes as part of IF2224 - Formal Languages and Automata Theory course at ITB.
