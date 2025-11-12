# Grammar Pascal-S
## Untuk Bagian Laporan Milestone 2

---

## Spesifikasi Grammar Lengkap

Grammar bahasa Pascal-S didefinisikan menggunakan **Extended Backus-Naur Form (EBNF)** dan diimplementasikan dengan teknik **Recursive Descent Parsing**.

### Notasi EBNF yang Digunakan:

- `::=` : didefinisikan sebagai
- `|` : atau (alternatif)
- `[ ]` : opsional (0 atau 1 kali)
- `{ }` : repetisi (0 atau lebih kali)
- `" "` : terminal symbol (token literal)
- `< >` : non-terminal symbol

---

## Grammar Production Rules

### 1. Program Structure

```ebnf
<program> ::= <program-header> <declaration-part> <compound-statement> "."

<program-header> ::= "program" IDENTIFIER ";"

<declaration-part> ::= {<const-declaration>}
                       {<type-declaration>}
                       {<var-declaration>}
                       {<subprogram-declaration>}
```

**Penjelasan:**
- Program Pascal-S terdiri dari header, bagian deklarasi, dan compound statement yang diakhiri dengan titik (`.`)
- Bagian deklarasi dapat berisi 0 atau lebih deklarasi konstanta, tipe, variabel, dan subprogram
- Urutan deklarasi harus: konstanta → tipe → variabel → subprogram

---

### 2. Constant Declaration

```ebnf
<const-declaration> ::= "konstanta" <const-assignment> {";" <const-assignment>} ";"

<const-assignment> ::= IDENTIFIER "=" <constant-value>

<constant-value> ::= NUMBER | CHAR_LITERAL | STRING_LITERAL | IDENTIFIER
```

**Contoh:**
```pascal
konstanta
  PI = 3.14;
  MAX_SIZE = 100;
  GREETING = 'Hello';
```

---

### 3. Type Declaration

```ebnf
<type-declaration> ::= "tipe" <type-assignment> {";" <type-assignment>} ";"

<type-assignment> ::= IDENTIFIER "=" <type>

<type> ::= <simple-type> | <array-type> | IDENTIFIER

<simple-type> ::= "integer" | "real" | "boolean" | "char" | "string"

<array-type> ::= "larik" "[" <range> "]" "dari" <type>

<range> ::= <expression> ".." <expression>
```

**Contoh:**
```pascal
tipe
  Indeks = 1..10;
  Vektor = larik[1..10] dari integer;
  Matriks = larik[1..5] dari Vektor;
```

---

### 4. Variable Declaration

```ebnf
<var-declaration> ::= "variabel" <var-group> {";" <var-group>} ";"

<var-group> ::= <identifier-list> ":" <type>

<identifier-list> ::= IDENTIFIER {"," IDENTIFIER}
```

**Contoh:**
```pascal
variabel
  x, y, z: integer;
  nama: string;
  nilai: larik[1..100] dari real;
```

---

### 5. Subprogram Declaration

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

**Contoh Prosedur:**
```pascal
prosedur Swap(a, b: integer);
variabel
  temp: integer;
mulai
  temp := a;
  a := b;
  b := temp;
selesai;
```

**Contoh Fungsi:**
```pascal
fungsi Faktorial(n: integer): integer;
variabel
  hasil: integer;
mulai
  jika n <= 1 maka
    hasil := 1
  selain-itu
    hasil := n * Faktorial(n - 1);
  Faktorial := hasil;
selesai;
```

---

### 6. Statements

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
```

---

#### 6.1 Assignment Statement

```ebnf
<assignment-statement> ::= IDENTIFIER ["[" <expression> "]"] ":=" <expression>
```

**Contoh:**
```pascal
a := 5;
b := a + 10;
arr[i] := arr[i] * 2;
```

---

#### 6.2 Procedure Call

```ebnf
<procedure-call> ::= (IDENTIFIER | <builtin-procedure>) ["(" <parameter-list> ")"]

<builtin-procedure> ::= "writeln" | "write" | "readln" | "read"

<parameter-list> ::= <expression> {"," <expression>}
```

**Contoh:**
```pascal
writeln('Hello World');
write('Nilai: ', x);
Swap(a, b);
```

---

#### 6.3 If Statement

```ebnf
<if-statement> ::= "jika" <expression> "maka" <statement>
                   ["selain-itu" <statement>]
```

**Contoh:**
```pascal
jika x > 0 maka
  writeln('Positif')
selain-itu
  writeln('Negatif atau Nol');
```

---

#### 6.4 While Statement

```ebnf
<while-statement> ::= "selama" <expression> "lakukan" <statement>
```

**Contoh:**
```pascal
selama i < 10 lakukan
mulai
  writeln(i);
  i := i + 1;
selesai;
```

---

#### 6.5 For Statement

```ebnf
<for-statement> ::= "untuk" IDENTIFIER ":=" <expression>
                    ("ke" | "turun-ke") <expression>
                    "lakukan" <statement>
```

**Contoh:**
```pascal
untuk i := 1 ke 10 lakukan
  writeln(i);

untuk i := 10 turun-ke 1 lakukan
  arr[i] := 0;
```

---

#### 6.6 Repeat Statement

```ebnf
<repeat-statement> ::= "ulangi" <statement-list> "sampai" <expression>
```

**Contoh:**
```pascal
ulangi
  readln(x);
  writeln(x * 2);
sampai x = 0;
```

---

### 7. Expressions

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

**Operator Precedence (dari tertinggi ke terendah):**

1. **Unary operators**: `tidak`, `+`, `-` (unary)
2. **Multiplicative**: `*`, `/`, `bagi`, `mod`, `dan`
3. **Additive**: `+`, `-`, `atau`
4. **Relational**: `=`, `<>`, `<`, `<=`, `>`, `>=`

**Contoh Expression:**
```pascal
x + y * z                    (* = x + (y * z) *)
(x + y) * z
a dan b atau c               (* = (a dan b) atau c *)
tidak (x > 5)
arr[i + 1] * 2
```

---

### 8. Lexical Elements

```ebnf
IDENTIFIER ::= LETTER {LETTER | DIGIT | "_"}

NUMBER ::= DIGIT {DIGIT} ["." DIGIT {DIGIT}]

CHAR_LITERAL ::= "'" CHARACTER "'"

STRING_LITERAL ::= "'" {CHARACTER} "'"

LETTER ::= "a".."z" | "A".."Z"

DIGIT ::= "0".."9"
```

---

## Keyword yang Digunakan

### Keywords Bahasa Indonesia

| Kategori | Keywords |
|----------|----------|
| **Program Structure** | `program`, `mulai`, `selesai` |
| **Declarations** | `konstanta`, `tipe`, `variabel`, `prosedur`, `fungsi` |
| **Data Types** | `integer`, `real`, `boolean`, `char`, `string`, `larik`, `dari` |
| **Control Flow** | `jika`, `maka`, `selain-itu`, `selama`, `lakukan`, `untuk`, `ke`, `turun-ke`, `ulangi`, `sampai` |
| **Logical Operators** | `dan`, `atau`, `tidak` |
| **Arithmetic Operators** | `bagi`, `mod` |
| **Built-in Procedures** | `writeln`, `write`, `readln`, `read` |

---

## Implementasi dalam Parser

Setiap non-terminal grammar diimplementasikan sebagai fungsi terpisah dalam `src/parser.py`:

| Grammar Rule | Fungsi Parser | Line |
|--------------|---------------|------|
| `<program>` | `parse_program()` | 68 |
| `<program-header>` | `parse_program_header()` | 76 |
| `<declaration-part>` | `parse_declaration_part()` | 83 |
| `<const-declaration>` | `parse_const_declaration()` | 101 |
| `<type-declaration>` | `parse_type_declaration()` | 124 |
| `<var-declaration>` | `parse_var_declaration()` | 139 |
| `<compound-statement>` | `parse_compound_statement()` | 263 |
| `<statement>` | `parse_statement()` | 281 |
| `<if-statement>` | `parse_if_statement()` | 316 |
| `<while-statement>` | `parse_while_statement()` | 329 |
| `<for-statement>` | `parse_for_statement()` | 337 |
| `<repeat-statement>` | `parse_repeat_statement()` | 356 |
| `<expression>` | `parse_expression()` | 391 |
| `<simple-expression>` | `parse_simple_expression()` | 402 |
| `<term>` | `parse_term()` | 418 |
| `<factor>` | `parse_factor()` | 429 |

---

## Karakteristik Grammar

### 1. Tidak Ambiguous
- Setiap konstruksi bahasa memiliki satu interpretasi yang jelas
- Operator precedence sudah didefinisikan dengan jelas melalui level expression

### 2. Tidak Left-Recursive
- Grammar sudah ditransformasi untuk menghilangkan left recursion
- Contoh transformasi:
  ```
  Original: E ::= E + T | T
  Transformed: E ::= T {+ T}
  ```

### 3. LL(1) Compatible
- Parser dapat membuat keputusan dengan melihat 1 token lookahead
- Beberapa kasus menggunakan `peek()` untuk disambiguasi (e.g., function call vs variable)

### 4. Structured
- Hierarki yang jelas: Program → Declarations → Statements → Expressions
- Nested structure didukung (nested if, nested loops, nested blocks)

---

## Diagram Parse Tree

Untuk program sederhana:
```pascal
program Test;
variabel
  x: integer;
mulai
  x := 5;
selesai.
```

Parse tree yang dihasilkan:
```
<program>
├── <program-header>
│   ├── "program"
│   ├── "Test"
│   └── ";"
├── <declaration-part>
│   └── <var-declaration>
│       ├── "variabel"
│       ├── <identifier-list>
│       │   └── "x"
│       ├── ":"
│       ├── <type>
│       │   └── "integer"
│       └── ";"
├── <compound-statement>
│   ├── "mulai"
│   ├── <statement-list>
│   │   └── <assignment-statement>
│   │       ├── "x"
│   │       ├── ":="
│   │       └── <expression>
│   │           └── <simple-expression>
│   │               └── <term>
│   │                   └── <factor>
│   │                       └── "5"
│   └── "selesai"
└── "."
```

---

## Kesimpulan

Grammar yang diimplementasikan:
- ✅ Lengkap untuk subset Pascal-S yang dispesifikasikan
- ✅ Mendukung keyword Bahasa Indonesia
- ✅ Menggunakan Recursive Descent Parsing
- ✅ Di-hardcode dalam program (bukan eksternal file)
- ✅ Menghasilkan parse tree yang hierarkis dan terstruktur

