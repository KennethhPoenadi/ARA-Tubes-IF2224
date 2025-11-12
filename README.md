# AutoRejectAtas

## Identitas Kelompok

**Kelompok X**
- Muhammad Syarafi Akmal		13522076
- Kenneth Poenadi 			13523040
- Bob Kunanda 				13523086
- M. Zahran Ramadhan Ardiana 	13523104 	

## Deskripsi Program

Program ini adalah compiler untuk bahasa Pascal-S (subset dari Pascal) dengan kata kunci dalam Bahasa Indonesia. Compiler ini terdiri dari dua tahap utama:

### Milestone 1: Lexical Analysis (Lexer)
Lexer memproses source code dan menghasilkan token sesuai dengan aturan DFA (Deterministic Finite Automaton). Fitur:
- Penanganan komentar
- Identifikasi token primitif
- Penanganan string dan karakter literal
- Deteksi kesalahan leksikal
- Support untuk keywords Bahasa Indonesia

### Milestone 2: Syntax Analysis (Parser)
Parser menganalisis token dan membangun Parse Tree menggunakan algoritma Recursive Descent. Fitur:
- Parsing struktur program Pascal-S
- Validasi sintaks
- Error handling dengan pesan informatif
- Generate Parse Tree visual
- Support untuk:
  - Variable declarations
  - Function dan procedure declarations
  - Array types
  - Control structures (if, while, for, repeat)
  - Expressions dan operators

## Requirements

- Python 3.8 atau lebih baru
- Library tambahan (jika ada, misalnya `numpy`, `pandas`, dll.)

## Cara Instalasi dan Penggunaan Program

1. Clone repository ini:
   ```bash
   git clone https://github.com/KennethhPoenadi/ARA-Tubes-IF2224.git
   ```
2. Masuk ke direktori proyek:
   ```bash
   cd ARA-Tubes-IF2224/Tubes
   ```

### Menggunakan Compiler (Milestone 2)

Compile program Pascal-S dan generate parse tree:
```bash
python3 compiler.py <source_file.pas>
```

Contoh:
```bash
python3 compiler.py test/milestone-2/test1.pas
```

Output akan berupa parse tree yang ditampilkan di terminal.

### Menggunakan Lexer Saja (Milestone 1)

Jika ingin menjalankan lexer saja:
```bash
python3 src/Lexer_final.py rules/dfa_rules_final.json <source_file.pas>
```

Contoh:
```bash
python3 src/Lexer_final.py rules/dfa_rules_final.json test/milestone-1/input/input1.pas
```

## Struktur File

```
Tubes/
├── compiler.py              # Main compiler program (Milestone 2)
├── src/
│   ├── lexer.py            # Lexer module dengan Indonesian keywords
│   ├── parser.py           # Parser dengan Recursive Descent
│   ├── tree_printer.py     # Parse tree printer
│   ├── Lexer_final.py      # Original lexer (Milestone 1)
│   └── tokenizer.py        # Alternative tokenizer
├── rules/
│   └── dfa_rules_final.json # DFA rules untuk lexer
├── test/
│   ├── milestone-1/        # Test cases untuk lexer
│   └── milestone-2/        # Test cases untuk parser
└── doc/                    # Laporan dan dokumentasi
```

## Pembagian Tugas

| Nama                     | NIM      | Tugas                          |
|--------------------------|----------|--------------------------------|
| Muhammad Syarafi Akmal  | 13522076 | Rules, Lexer, Test Case, Laporan |
| Kenneth Poenadi         | 13523040 | Rules, Diagram DFA, Laporan    |
| M Zahran Ramadhan       | 13523104 | Rules, Lexer, Test Case, Laporan |
| Bob Kunanda             | 13523086 | Rules, Diagram DFA, Laporan    |

