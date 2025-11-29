# Laporan Semantic Analysis - Pascal-S Compiler

**Nama**: Kenneth Poenadi  
**Program Studi**: Teknik Informatika  
**Mata Kuliah**: Teori Bahasa Formal dan Otomata (TBFO)  
**Tanggal**: 29 November 2025

---

## 1. Penjelasan Konsep Semantic Analysis (20 poin)

### 1.1 Pengertian Semantic Analysis

Semantic analysis merupakan tahap ketiga dalam proses kompilasi setelah lexical analysis dan syntax analysis. Jika syntax analysis hanya menjamin bahwa program sesuai dengan aturan grammar, maka semantic analysis memastikan bahwa program tersebut bermakna secara logis. Tahap ini memeriksa apakah setiap operasi, deklarasi, pemanggilan fungsi, penggunaan variabel, dan ekspresi dalam program sesuai dengan aturan semantik bahasa Pascal-S. Contoh kesalahan yang hanya dapat ditemukan pada tahap ini adalah penggunaan variabel sebelum deklarasi, operasi yang melibatkan tipe data yang tidak kompatibel, atau pemanggilan prosedur dengan jumlah parameter yang keliru. Dengan demikian, semantic analysis berfungsi sebagai penghubung antara struktur kode sumber dengan arti sebenarnya dari program, sehingga compiler dapat menghasilkan keluaran yang benar pada tahap berikutnya.

### 1.3 Attributed Grammar

**Attributed Grammar (Tata Bahasa Beratribut)** adalah landasan formal untuk Analisis Semantik. Ini adalah perpanjangan dari Context-Free Grammar (CFG) yang digunakan oleh parser dengan menambahkan dua komponen utama:

**Komponen Attributed Grammar:**

1. **Atribut**: Nilai tambahan yang diasosiasikan dengan simbol grammar untuk menyimpan informasi semantik
2. **Aturan Semantik**: Fungsi yang mendefinisikan bagaimana atribut dihitung berdasarkan atribut lain

**Jenis Atribut:**

- **Synthesized Attributes**: Atribut yang nilainya dihitung dari atribut children nodes (bottom-up). Contoh: tipe hasil ekspresi dihitung dari tipe operand-nya
- **Inherited Attributes**: Atribut yang nilainya diturunkan dari parent atau sibling nodes (top-down). Contoh: informasi tipe yang dibutuhkan untuk type checking parameter

Dalam implementasi ini, kami menggunakan **synthesized attributes**:

```python
# Contoh synthesized attributes pada AST nodes
node.computed_type = DataType.INTEGER  # Tipe hasil dari expression
node.tab_index = 5                     # Index di symbol table
node.scope_level = 1                   # Level scope saat ini
```

**Contoh Aturan Semantik untuk Operasi Biner (Penjumlahan):**

```
Produksi: E → E₁ + E₂

### 1.3 Abstract Syntax Tree (AST) Teranotasi

**Abstract Syntax Tree (AST)** merupakan representasi hierarkis program yang lebih ringkas dibandingkan Parse Tree. Pembentukannya menggunakan **Syntax-Directed Translation Scheme (SDTS)**, di mana setiap production rule memiliki semantic action yang terkait. Tindakan semantik ini dijalankan pada node Parse Tree untuk membentuk node baru pada AST. AST fokus pada struktur logis program dan menghilangkan node yang bersifat seremonial, seperti tanda kurung dan titik koma, untuk menyederhanakan proses analisis semantik berikutnya.

**Anotasi pada AST (Decorated AST):**

Setelah AST terbentuk, proses **Pengecekan Tipe & Lingkup** dilakukan dengan menelusuri setiap node AST secara Depth First. Selama penelusuran ini, AST akan dianotasi atau didekorasi dengan informasi semantik yang relevan. Node pada Decorated AST minimal harus memiliki informasi penting berikut:

- **Tipe Ekspresi** (e.g., integer, boolean)
- **Referensi ke Symbol Table** (indeks ke entri Symbol Table)
- **Informasi Lingkup** (Scope)

### 1.4 Symbol Table

**Symbol Table** adalah struktur data penting yang minimal menyimpan informasi nama identifier, tipe datanya, dan scope-nya. Dalam konteks kompilasi, Symbol Table menggunakan struktur data stack untuk manajemen lingkup.

**Fungsi dan Mekanisme Lingkup (Scope):**

Saat identifier digunakan dalam program (misalnya, dalam sebuah ekspresi), compiler akan melakukan **lookup** pada Symbol Table. Proses lookup ini akan memeriksa scope saat ini, kemudian mundur ke scope luar (berdasarkan lexical level) sampai identifier ditemukan.

**Struktur Tabel dalam Pascal-S:**

Sesuai dengan spesifikasi Pascal-S yang digunakan, terdapat tiga tabel simbol yang saling terkait:

1. **tab (Identifier Table)**: Digunakan untuk menyimpan informasi mengenai setiap identifier (konstanta, variabel, prosedur, fungsi). Atribut utamanya meliputi identifiers, link (ke identifier sebelumnya dalam scope), obj (kelas objek: variabel, tipe, dll.), type (tipe dasar), lev (tingkat lexical level), dan adr (offset alamat)

2. **btab (Block Table)**: Menyimpan informasi blok prosedur, fungsi, atau definisi tipe record. Atributnya mencakup last (identifier terakhir dalam blok), lpar (parameter terakhir), psze (ukuran parameter), dan vsze (ukuran variabel lokal)

3. **atab (Array Table)**: Menyimpan informasi spesifik untuk tipe array, seperti xtyp (tipe indeks), eltyp (tipe elemen), low dan high (batas indeks), dan size (total ukuran)
    left_type = self.visit(node.left)
    
    # Hitung tipe operand kanan (T2)
    right_type = self.visit(node.right)
    
    # Terapkan aturan semantik untuk menghitung tipe hasil
    result_type = self._compute_binop_type(
        node.operator, 
        left_type, 
        right_type, 
        node
    )
    
    # Simpan tipe hasil ke node (synthesized attribute)
    node.computed_type = result_type
    return result_type
```

Aturan semantik penjumlahan pada fungsi `_compute_binop_type(...)`:

```python
def _compute_binop_type(self, operator, left_type, right_type, node):
    if op in ['+', '-', '*']:
        # Cek apakah operand numerik
        if left_type in [INTEGER, REAL] and right_type in [INTEGER, REAL]:
            
            # ATURAN: Jika salah satu REAL, hasil REAL
            if left_type == REAL or right_type == REAL:
                return DataType.REAL  # INTEGER + REAL → REAL
            
            # ATURAN: Jika keduanya INTEGER, hasil INTEGER
            return DataType.INTEGER  # INTEGER + INTEGER → INTEGER
        
        # String concatenation dengan +
        if op == '+' and (left_type == STRING or right_type == STRING):
            return DataType.STRING
        
        # TYPE MISMATCH: operand bukan numerik
        self.add_error(f"Invalid operand types for '{operator}'", node)
        return None  # ERROR
```

Dalam konteks Analisis Semantik, Attributed Grammar digunakan untuk secara formal mendefinisikan dan memvalidasi makna dari sebuah program. Aturan semantik inilah yang diimplementasikan di dalam fungsi `visit` pada AST.

### 1.4 Symbol Table

### 1.6 Abstract Syntax Tree (AST) Teranotasi

**Abstract Syntax Tree (AST)** merupakan representasi hierarkis program yang lebih ringkas dibandingkan Parse Tree. Pembentukannya menggunakan **Syntax-Directed Translation Scheme (SDTS)**, di mana setiap production rule memiliki semantic action yang terkait. Tindakan semantik ini dijalankan pada node Parse Tree untuk membentuk node baru pada AST. AST fokus pada struktur logis program dan menghilangkan node yang bersifat seremonial, seperti tanda kurung dan titik koma, untuk menyederhanakan proses analisis semantik berikutnya.

**Anotasi pada AST (Decorated AST):**

Setelah AST terbentuk, proses **Pengecekan Tipe & Lingkup** dilakukan dengan menelusuri setiap node AST secara Depth First. Selama penelusuran ini, AST akan dianotasi atau didekorasi dengan informasi semantik yang relevan. Node pada Decorated AST minimal harus memiliki informasi penting berikut:

- **Tipe Ekspresi** (e.g., INTEGER, BOOLEAN, REAL)
- **Referensi ke Symbol Table** (indeks ke entri Symbol Table)
- **Informasi Lingkup** (Scope level)

### 1.7 Visitor Pattern

Implementasi menggunakan **Visitor Pattern** untuk traverse AST. Untuk menelusuri AST dan menjalankan aturan semantik, digunakan pola desain Visitor.

**Mekanisme Traversal:**

```python
def visit(self, node: ASTNode) -> Optional[DataType]:
    method_name = f"visit_{node.__class__.__name__}"
    visitor_method = getattr(self, method_name, self.generic_visit)
    return visitor_method(node)
```

Setiap node type memiliki visitor method khusus (contoh: `visit_BinOpNode`, `visit_AssignmentNode`) yang melakukan semantic checking spesifik untuk node tersebut.

**Contoh Traversal untuk ProgramNode:**

```python
def visit_ProgramNode(self, node: ProgramNode) -> None:
    """visit program node - entry point untuk analysis"""
    # Aksi 1: Akses Symbol Table - masukkan program name
    self.symbol_table.enter_program(node.name)
    
    # Aksi 2: Mengunjungi Anak - visit declarations
    if node.declarations:
        self.visit(node.declarations)
    
    # Aksi 3: Mengunjungi Anak - visit program body
    if node.body:
        self.visit(node.body)
```

**Contoh Traversal untuk AssignmentNode:**
### 1.6 Semantic Actions

Di dalam setiap fungsi `visit`, dilakukan **empat aksi utama**:

1. **Mengunjungi Anak**: Fungsi visit memanggil fungsi visit untuk node anak-anaknya
2. **Akses Symbol Table**: Melakukan lookup untuk identifier yang digunakan atau memasukkan identifier yang dideklarasikan ke dalam Symbol Table
3. **Kalkulasi Atribut**: Menghitung atribut/tipe semantik dari node saat ini (misalnya, menentukan tipe ekspresi hasil operasi aritmatika)
4. **Anotasi Node**: Menambahkan informasi yang dikalkulasi ke node AST (dekorasi)
    value_type = self.visit(node.value)
### 1.7 Error Handling Semantik

Meskipun Parser menjamin sintaks yang benar, **Semantic Analyzer harus mampu mendeteksi dan melaporkan kesalahan semantik**. Error handling yang baik akan menghasilkan pesan galat yang informatif.

#### 1.7.1 Type Mismatch Errors

Ini adalah error yang paling umum, terjadi ketika tipe data tidak cocok dalam operasi. Misalnya saat assignment, sistem akan memeriksa apakah tipe data yang di-assign kompatibel dengan tipe data variabel target. Begitu juga dengan operasi biner seperti penjumlahan atau perbandingan, sistem akan memastikan kedua operand memiliki tipe yang kompatibel. Ada juga pemeriksaan khusus untuk operasi integer seperti `bagi` dan `mod` yang hanya menerima operand integer, serta operasi boolean seperti `dan` dan `atau` yang hanya bisa digunakan dengan operand boolean.

**Contoh Type Mismatch:**

```python
def visit_AssignmentNode(self, node: AssignmentNode) -> None:
    target_type = self.visit(node.target)
    value_type = self.visit(node.value)
    
    # Error: tidak bisa assign tipe berbeda
    if not self._types_compatible(target_type, value_type):
        self.add_error(
            f"Type mismatch in assignment: cannot assign {value_type.value} to {target_type.value}",
            node
        )


def _compute_binop_type(self, operator, left_type, right_type, node):
    if op in ['+', '-', '*']:
        if left_type in [INTEGER, REAL] and right_type in [INTEGER, REAL]:
            # OK: numeric types
            return ...
        # Error: invalid operand types
        self.add_error(f"Invalid operand types for '{operator}'", node)
        return None
```

#### 1.7.2 Undeclared Identifier Errors

Kategori ini menangkap semua kasus dimana kode mencoba menggunakan identifier yang belum dideklarasikan. Ini berlaku untuk variabel, array, fungsi, prosedur, bahkan tipe custom. Setiap kali ada referensi ke identifier, sistem akan melakukan lookup di symbol table. Kalau tidak ketemu, langsung dilaporkan sebagai error. Ini penting untuk mencegah penggunaan identifier yang salah atau typo.

**Contoh Undeclared Error:**

```python
def visit_VarNode(self, node: VarNode):
    entry, tab_index = self.symbol_table.lookup_with_index(node.name)
    
    if not entry:
        self.add_error(f"Undeclared variable '{node.name}'", node)
        return None
```

#### 1.7.3 Duplicate Declaration Errors

Error ini terjadi ketika mencoba mendeklarasikan identifier yang sudah ada di scope yang sama. Sistem memeriksa ini untuk semua jenis deklarasi: konstanta, tipe, variabel, parameter, prosedur, dan fungsi. Sebelum menambahkan entry baru ke symbol table, sistem selalu cek dulu apakah nama tersebut sudah ada di current scope. Ini memastikan setiap identifier di scope tertentu memiliki makna yang unik.

**Contoh Duplicate Error:**

```python
def visit_ConstDeclNode(self, node: ConstDeclNode):
    existing = self.symbol_table.lookup_in_current_scope(node.name)
    if existing:
        self.add_error(f"Duplicate declaration of constant '{node.name}'", node)
```

#### 1.7.4 Type Constraint Errors

Ini adalah error yang spesifik untuk constraint tipe tertentu dalam struktur bahasa Pascal-S. Contohnya, variabel loop dalam statement `for` harus bertipe integer, bound values di loop `for` juga harus integer, index array harus integer, dan range bounds harus integer. Constraint ini memastikan konstruksi bahasa digunakan sesuai dengan spesifikasi Pascal-S.

**Contoh Type Constraint Error:**

```python
def visit_ArrayAccessNode(self, node: ArrayAccessNode):
    if index_type and index_type != DataType.INTEGER:
        self.add_error("Array index must be integer", node)
```

#### 1.7.5 Control Flow Errors

Error ini berkaitan dengan statement kontrol seperti `if`, `while`, dan `repeat`. Yang paling penting adalah memastikan kondisi di statement-statement ini selalu menghasilkan nilai boolean. Misalnya, kondisi di statement `if` atau `while` tidak boleh berupa ekspresi numerik atau tipe lainnya, harus boolean. Ini memastikan logika program berjalan dengan benar.

**Contoh Control Flow Error:**

```python
def visit_IfStatementNode(self, node: IfStatementNode):
    if condition_type and condition_type != DataType.BOOLEAN:
        self.add_error("If condition must be a boolean expression", node)
```

#### 1.7.6 Operator-Specific Errors

Kategori terakhir ini menangani error yang spesifik untuk operator tertentu. Misalnya unary operator `+` dan `-` hanya bisa digunakan dengan operand numerik (integer atau real), operator `tidak` (not) hanya untuk boolean, dan operator `bagi` serta `mod` hanya untuk integer. Setiap operator memiliki aturan tipenya sendiri yang harus dipatuhi.

**Contoh Operator-Specific Error:**

```python
if op == '/':
    if left_type in [INTEGER, REAL] and right_type in [INTEGER, REAL]:
        return DataType.REAL
    self.add_error(f"Invalid operand types for '/'", node)
```

---

## 2. Perancangan Program (5 poin)ported
    
    # Aksi 3: Kalkulasi Atribut - cek type compatibility
    if not self._types_compatible(target_type, value_type):
        self.add_error(
            f"Type mismatch in assignment: cannot assign {value_type.value} to {target_type.value}",
            node
        )
    
    # Aksi 4: Anotasi Node - decorate dengan computed type
    node.computed_type = target_type
```

**Urutan Traversal AST:**

Analisis Semantik dilakukan dengan menelusuri (traversing) AST secara rekursif, biasanya secara **Top-Down** dengan urutan **Depth First**:

```
ProgramNode (visit_ProgramNode)
    ↓
    ├─ DeclarationPartNode
    │   ├─ ConstDeclNode (visit children bottom-up)
    │   ├─ VarDeclNode
    │   └─ ProcedureDeclNode
    │
    └─ CompoundStatementNode (body)
        └─ AssignmentNode (visit_AssignmentNode)
            ├─ VarNode (target) ← visit dulu (depth-first)
            └─ BinOpNode (value) ← baru visit ini
                ├─ left expression
                └─ right expression
```

### 1.5 Type System

Type system dalam Pascal-S compiler mencakup:

**Tipe Primitif:**
- INTEGER: Bilangan bulat
- REAL: Bilangan riil (floating point)
- BOOLEAN: Nilai true/false
- CHAR: Karakter tunggal
- STRING: String karakter

**Tipe Kompleks:**
- ARRAY: Array dengan index range dan element type

**Type Compatibility:**
- INTEGER ↔ REAL: Compatible dengan implicit conversion
- CHAR ↔ STRING: Compatible untuk assignment
- Tipe lain: Harus exact match

### 1.6 Visitor Pattern

Implementasi menggunakan **Visitor Pattern** untuk traverse AST:

```python
def visit(self, node: ASTNode) -> Optional[DataType]:
    method_name = f"visit_{node.__class__.__name__}"
    visitor_method = getattr(self, method_name, self.generic_visit)
    return visitor_method(node)
```

Setiap node type memiliki visitor method khusus (contoh: `visit_BinOpNode`, `visit_AssignmentNode`) yang melakukan semantic checking spesifik untuk node tersebut.

### 1.7 Semantic Actions

Setiap visitor method melakukan 4 semantic actions utama:

1. **Visit Children**: Rekursif mengunjungi child nodes untuk mendapat informasi tipe
2. **Symbol Table Access**: Lookup atau insert identifier di symbol table
3. **Attribute Calculation**: Menghitung atribut semantik (tipe, compatibility)
4. **Node Decoration**: Menambahkan atribut semantik ke AST node untuk fase selanjutnya

---

## 2. Perancangan Program (5 poin)

### 2.1 Teknologi yang Digunakan

**Bahasa Pemrograman**: Python 3.x

**Alasan Pemilihan:**
- Type hints untuk dokumentasi yang jelas
- Dynamic typing memudahkan prototyping
- Rich standard library (enum, typing, dataclasses)
- Mudah untuk pattern matching dan reflection (getattr untuk visitor dispatch)

**Library/Module:**
- `typing`: Type hints (Optional, List, Union)
- `enum`: Enum untuk DataType dan ObjectType
- `sys`, `os`: Path management untuk imports

### 2.2 Struktur Program

```
src/
├── semantic_analyzer.py    # Main semantic analysis module
├── symbol_table.py         # Symbol table implementation
├── ast_nodes.py           # AST node definitions
├── ast_builder.py         # Parse tree to AST transformation
├── parser.py              # Syntax parser
└── lexer.py               # Lexical analyzer
```

**Dependency Flow:**
```
semantic_analyzer.py
    ↓ imports
    ├── symbol_table.py (SymbolTable, DataType, ObjectType)
    └── ast_nodes.py (All AST node classes)
```

### 2.3 Kelas/Fungsi Utama

#### 2.3.1 SemanticVisitor Class

**Tanggung Jawab**: Main class untuk semantic analysis

**Atribut Utama:**
```python
self.symbol_table: SymbolTable        # Symbol table instance
self.errors: List[SemanticError]      # Collected semantic errors
self.warnings: List[str]              # Collected warnings
self.current_function: Optional[str]  # Track current function context
```

**Method Utama:**
- `visit(node)`: Dispatcher method untuk routing ke visitor yang tepat
- `visit_*Node(node)`: Specific visitor untuk setiap AST node type
- `add_error()`: Menambahkan semantic error
- `_compute_binop_type()`: Menghitung result type dari binary operation
- `_types_compatible()`: Mengecek type compatibility

#### 2.3.2 SymbolTable Class (dari symbol_table.py)

**Tanggung Jawab**: Manage identifiers dan scope

**Method Utama:**
- `enter_variable()`: Menambah variable declaration
- `enter_procedure()`: Menambah procedure/function dan create new scope
- `lookup()`: Mencari identifier di scope hierarchy
- `enter_scope()` / `exit_scope()`: Scope management

#### 2.3.3 SemanticError Class

**Tanggung Jawab**: Exception untuk semantic errors

**Atribut:**
```python
self.message: str               # Error message
self.line: Optional[int]        # Line number
self.column: Optional[int]      # Column number
```

### 2.4 Alur Kerja Program

```
┌─────────────────┐
│  Source Code    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Lexer          │ (Tokenization)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Parser         │ (Syntax Analysis)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AST Builder    │ (Parse Tree → AST)
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│         Semantic Analyzer                   │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │ 1. Visit ProgramNode                 │  │
│  │    - Enter program to symbol table   │  │
│  └──────────────┬───────────────────────┘  │
│                 │                           │
│  ┌──────────────▼───────────────────────┐  │
│  │ 2. Visit Declarations                │  │
│  │    - Process constants               │  │
│  │    - Process types                   │  │
│  │    - Process variables               │  │
│  │    - Process procedures/functions    │  │
│  │    - Build symbol table              │  │
│  └──────────────┬───────────────────────┘  │
│                 │                           │
│  ┌──────────────▼───────────────────────┐  │
│  │ 3. Visit Statements                  │  │
│  │    - Type check assignments          │  │
│  │    - Validate control flow           │  │
│  │    - Check function/procedure calls  │  │
│  └──────────────┬───────────────────────┘  │
│                 │                           │
│  ┌──────────────▼───────────────────────┐  │
│  │ 4. Visit Expressions                 │  │
│  │    - Compute expression types        │  │
│  │    - Check operator compatibility    │  │
│  │    - Validate operand types          │  │
│  └──────────────┬───────────────────────┘  │
│                 │                           │
│  ┌──────────────▼───────────────────────┐  │
│  │ 5. Decorate AST                      │  │
│  │    - Add computed_type attributes    │  │
│  │    - Add tab_index references        │  │
│  │    - Add scope_level information     │  │
│  └──────────────────────────────────────┘  │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Output:                        │
│  - Decorated AST                │
│  - Complete Symbol Table        │
│  - List of Semantic Errors      │
│  - List of Warnings             │
└─────────────────────────────────┘
```

### 2.5 Justifikasi Pilihan Implementasi

#### 2.5.1 Visitor Pattern

**Pilihan**: Menggunakan Visitor Pattern dengan dynamic dispatch

**Justifikasi:**
- **Separation of Concerns**: Semantic logic terpisah dari AST node definitions
- **Extensibility**: Mudah menambah visitor baru tanpa mengubah AST nodes
- **Type Safety**: Setiap node type punya visitor method yang spesifik
- **Maintainability**: Logic untuk setiap node type terlokalisir dalam satu method

**Alternatif yang Tidak Dipilih:**
- **Method di AST Nodes**: Akan membuat AST nodes terlalu complex dan coupling tinggi
- **Switch/If-else**: Tidak scalable dan sulit maintain untuk 20+ node types

#### 2.5.2 Symbol Table dengan Scope Chaining

**Pilihan**: Hierarchical symbol table dengan dynamic scope management

**Justifikasi:**
- **Lexical Scoping**: Mendukung nested scopes (functions dalam functions)
- **Efficient Lookup**: O(k) dimana k = depth of scope nesting (typically small)
- **Memory Efficient**: Scope di-pop setelah keluar dari function/procedure

**Alternatif yang Tidak Dipilih:**
- **Flat Symbol Table**: Tidak bisa handle name shadowing dan nested scopes
- **Persistent Scopes**: Memory overhead tinggi untuk deep nesting

#### 2.5.3 Error Collection vs Exception

**Pilihan**: Collect all errors dalam list, tidak throw exception

**Justifikasi:**
- **User Experience**: User melihat semua errors sekaligus, tidak hanya error pertama
- **Robustness**: Analysis berlanjut meskipun ada error, detect lebih banyak issues
- **IDE Integration**: Cocok untuk language server yang perlu report multiple diagnostics

**Alternatif yang Tidak Dipilih:**
- **Throw Exception on First Error**: User harus fix error satu-satu, slow iteration

#### 2.5.4 AST Decoration

**Pilihan**: Menambahkan atribut semantik ke AST nodes (in-place modification)

**Justifikasi:**
- **Simplicity**: Tidak perlu struktur data terpisah untuk mapping node → attributes
- **Performance**: Direct access ke attributes tanpa lookup
- **Code Generation Ready**: Fase selanjutnya (code generation) bisa langsung akses tipe info

**Alternatif yang Tidak Dipilih:**
- **Separate Attribute Table**: Extra indirection, complexity dalam mapping

#### 2.5.5 Type Compatibility dengan Implicit Conversion

**Pilihan**: Allow INTEGER ↔ REAL dan CHAR ↔ STRING compatibility

**Justifikasi:**
- **Pascal Semantics**: Sesuai dengan spesifikasi bahasa Pascal
- **User Friendliness**: Mengurangi explicit type casting yang verbose
- **Common Pattern**: Umum dalam bahasa statically-typed modern

---

## 3. Hasil Implementasi (2 poin)

### 3.1 Struktur Kode Utama

**File**: `src/semantic_analyzer.py` (892 lines)

**Komponen Utama:**

1. **SemanticError Class** (lines 49-60)
   - Exception class untuk semantic errors
   - Menyimpan message, line, dan column information

2. **SemanticVisitor Class** (lines 63-795)
   - Main semantic analyzer dengan 30+ visitor methods
   - Symbol table integration
   - Error collection system

3. **Helper Functions** (lines 717-780)
   - `_compute_binop_type()`: Binary operation type inference
   - `_types_compatible()`: Type compatibility checking
   - `_process_array_type()`: Array type processing

4. **Integration Function** (lines 798-808)
   - `analyze(ast)`: Entry point untuk semantic analysis

### 3.2 Error Detection Capabilities

Implementasi mampu mendeteksi 30+ jenis semantic errors yang dikategorikan dalam 6 kategori:

| Kategori | Jumlah Error Types | Contoh |
|----------|-------------------|--------|
| Type Mismatch | 8 | "Cannot assign REAL to INTEGER" |
| Undeclared Identifier | 7 | "Undeclared variable 'x'" |
| Duplicate Declaration | 6 | "Duplicate declaration of variable 'y'" |
| Type Constraint | 4 | "Loop variable must be integer" |
| Control Flow | 5 | "If condition must be boolean" |
| Operator-Specific | 4 | "'bagi' requires integer operands" |

### 3.3 Symbol Table Output

Symbol table dapat di-print untuk debugging:

```
=== SYMBOL TABLE ===
TAB [Name Table]:
  Index | Name        | Object    | Type      | Level | Address | Ref
  ------|-------------|-----------|-----------|-------|---------|-----
  0     | SemanticTest| PROGRAM   | VOID      | 0     | 0       | -1
  1     | x           | VARIABLE  | INTEGER   | 1     | 0       | -1
  2     | y           | VARIABLE  | INTEGER   | 1     | 1       | -1
  3     | z           | VARIABLE  | REAL      | 1     | 2       | -1
  4     | flag        | VARIABLE  | BOOLEAN   | 1     | 3       | -1
```

### 3.4 AST Decoration

Setelah semantic analysis, AST nodes didekorasi dengan atribut:

```python
# Contoh decorated BinOpNode (x + y)
BinOpNode(
    operator='+',
    left=VarNode(name='x', tab_index=1, computed_type=INTEGER, scope_level=1),
    right=VarNode(name='y', tab_index=2, computed_type=INTEGER, scope_level=1),
    tab_index=-1,           # Binary op tidak masuk symbol table
    computed_type=INTEGER,  # Result type dari operasi
    scope_level=1           # Computed di scope level 1
)
```

### 3.5 Integration dengan Compiler Pipeline

```python
# Complete compiler pipeline
from lexer import tokenize_from_text
from parser import Parser
from ast_builder import ASTBuilder
from semantic_analyzer import analyze

# 1. Tokenize
tokens = tokenize_from_text(source_code, 'rules/dfa_rules_final.json')

# 2. Parse
parser = Parser(tokens)
parse_tree = parser.parse()

# 3. Build AST
builder = ASTBuilder()
ast = builder.build(parse_tree)

# 4. Semantic Analysis
visitor = analyze(ast)

# Check results
if visitor.has_errors():
    visitor.print_errors()
else:
    print("✓ No semantic errors!")

visitor.print_symbol_table()
```

---

## 4. Test Cases (3 poin)

### Test Case 1: Type Mismatch dalam Assignment

**Deskripsi**: Menguji deteksi type mismatch saat assignment

**Input** (`test/milestone-3/input/test_type_mismatch.pas`):
```pascal
program TypeMismatchTest;

variabel
    x: integer;
    y: boolean;
    z: real;

mulai
    x := 10;           { OK: integer := integer }
    y := true;         { OK: boolean := boolean }
    z := 3.14;         { OK: real := real }
    
    x := true;         { ERROR: cannot assign boolean to integer }
    y := 100;          { ERROR: cannot assign integer to boolean }
    z := 'hello';      { ERROR: cannot assign string to real }
selesai.
```

**Expected Output**:
```
ERROR: Type mismatch in assignment: cannot assign BOOLEAN to INTEGER
ERROR: Type mismatch in assignment: cannot assign INTEGER to BOOLEAN
ERROR: Type mismatch in assignment: cannot assign STRING to REAL

Total Errors: 3
```

**Hasil**: ✅ PASS - Semua type mismatch terdeteksi dengan benar

---

### Test Case 2: Undeclared Variables

**Deskripsi**: Menguji deteksi penggunaan variabel yang belum dideklarasikan

**Input** (`test/milestone-3/input/test_undeclared.pas`):
```pascal
program UndeclaredTest;

variabel
    x, y: integer;

mulai
    x := 5;
    y := x + 10;       { OK: x dan y sudah dideklarasi }
    
    z := x + y;        { ERROR: z tidak dideklarasi }
    
    writeln(x, y, w);  { ERROR: w tidak dideklarasi }
    
    jika flag maka     { ERROR: flag tidak dideklarasi }
        x := 100;
selesai.
```

**Expected Output**:
```
ERROR: Undeclared variable 'z'
ERROR: Undeclared variable 'w'
ERROR: Undeclared variable 'flag'

Total Errors: 3
```

**Hasil**: ✅ PASS - Semua undeclared variables terdeteksi

---

### Test Case 3: Duplicate Declarations

**Deskripsi**: Menguji deteksi deklarasi ganda dalam scope yang sama

**Input** (`test/milestone-3/input/test_duplicate.pas`):
```pascal
program DuplicateTest;

konstanta
    MAX = 100;
    MAX = 200;         { ERROR: duplicate constant }

variabel
    x: integer;
    y: real;
    x: boolean;        { ERROR: duplicate variable }

prosedur Test(a: integer; b: integer; a: real);  { ERROR: duplicate parameter }
mulai
    writeln(a, b);
selesai;

mulai
    x := 10;
    y := 3.14;
selesai.
```

**Expected Output**:
```
ERROR: Duplicate declaration of constant 'MAX'
ERROR: Duplicate declaration of variable 'x'
ERROR: Duplicate parameter 'a'

Total Errors: 3
```

**Hasil**: ✅ PASS - Semua duplicate declarations terdeteksi

---

### Test Case 4: Type Compatibility dan Implicit Conversion

**Deskripsi**: Menguji type compatibility rules (INTEGER ↔ REAL, CHAR ↔ STRING)

**Input** (`test/milestone-3/input/test_compatibility.pas`):
```pascal
program CompatibilityTest;

variabel
    i: integer;
    r: real;
    c: char;
    s: string;
    b: boolean;

mulai
    { INTEGER dan REAL compatible }
    i := 10;
    r := i;            { OK: integer → real }
    r := 3.14;
    i := r;            { OK: real → integer (implicit truncation) }
    
    { CHAR dan STRING compatible }
    c := 'A';
    s := c;            { OK: char → string }
    s := 'hello';
    c := s;            { OK: string → char (take first char) }
    
    { BOOLEAN tidak compatible dengan numerik }
    b := true;
    i := b;            { ERROR: boolean tidak compatible dengan integer }
    b := i;            { ERROR: integer tidak compatible dengan boolean }
    
    { Mixed arithmetic }
    r := i + 3.14;     { OK: hasil REAL }
    i := i + 5;        { OK: hasil INTEGER }
selesai.
```

**Expected Output**:
```
ERROR: Type mismatch in assignment: cannot assign BOOLEAN to INTEGER
ERROR: Type mismatch in assignment: cannot assign INTEGER to BOOLEAN

Total Errors: 2
```

**Hasil**: ✅ PASS - Type compatibility rules diterapkan dengan benar

---

### Test Case 5: Control Flow Type Checking

**Deskripsi**: Menguji type checking untuk kondisi dalam control statements

**Input** (`test/milestone-3/input/test_control_flow.pas`):
```pascal
program ControlFlowTest;

variabel
    x, y: integer;
    flag: boolean;

mulai
    x := 10;
    y := 20;
    flag := true;
    
    { OK: kondisi boolean }
    jika flag maka
        x := 100;
    
    jika x > y maka    { OK: comparison menghasilkan boolean }
        writeln('x lebih besar');
    
    { ERROR: kondisi bukan boolean }
    jika x maka        { ERROR: x adalah integer, bukan boolean }
        y := 50;
    
    { ERROR: while condition bukan boolean }
    selama x lakukan   { ERROR: x adalah integer }
        x := x - 1;
    
    { OK: while condition boolean }
    selama x > 0 lakukan
        x := x - 1;
    
    { ERROR: repeat condition bukan boolean }
    ulangi
        y := y + 1;
    sampai y;          { ERROR: y adalah integer }
selesai.
```

**Expected Output**:
```
ERROR: If condition must be a boolean expression
ERROR: While condition must be a boolean expression
ERROR: Repeat-until condition must be a boolean expression

Total Errors: 3
```

**Hasil**: ✅ PASS - Semua control flow type errors terdeteksi

---

### Test Case 6: Binary Operation Type Inference

**Deskripsi**: Menguji type inference untuk berbagai operasi biner

**Input** (`test/milestone-3/input/test_binop.pas`):
```pascal
program BinOpTest;

variabel
    i1, i2: integer;
    r1, r2: real;
    b1, b2: boolean;
    s1, s2: string;

mulai
    i1 := 10;
    i2 := 20;
    r1 := 3.14;
    r2 := 2.71;
    b1 := true;
    b2 := false;
    s1 := 'hello';
    s2 := 'world';
    
    { Arithmetic operations }
    i1 := i1 + i2;     { OK: INTEGER + INTEGER → INTEGER }
    r1 := r1 + r2;     { OK: REAL + REAL → REAL }
    r1 := i1 + r1;     { OK: INTEGER + REAL → REAL }
    r1 := r1 / i1;     { OK: Division selalu REAL }
    
    i1 := i1 bagi i2;  { OK: INTEGER bagi INTEGER → INTEGER }
    i1 := i1 mod i2;   { OK: INTEGER mod INTEGER → INTEGER }
    
    { Logical operations }
    b1 := b1 dan b2;   { OK: BOOLEAN dan BOOLEAN → BOOLEAN }
    b1 := b1 atau b2;  { OK: BOOLEAN atau BOOLEAN → BOOLEAN }
    
    { Comparison operations }
    b1 := i1 > i2;     { OK: Comparison → BOOLEAN }
    b1 := r1 < r2;     { OK: Comparison → BOOLEAN }
    
    { String concatenation }
    s1 := s1 + s2;     { OK: STRING + STRING → STRING }
    
    { ERROR cases }
    i1 := b1 + b2;     { ERROR: tidak bisa add boolean }
    b1 := i1 dan i2;   { ERROR: dan requires boolean }
    i1 := r1 bagi r2;  { ERROR: bagi requires integer }
    r1 := i1 mod r2;   { ERROR: mod requires integer }
selesai.
```

**Expected Output**:
```
ERROR: Invalid operand types for '+'
ERROR: 'dan' requires boolean operands
ERROR: 'bagi' requires integer operands
ERROR: 'mod' requires integer operands

Total Errors: 4
```

**Hasil**: ✅ PASS - Type inference dan error detection bekerja dengan benar

---

### Test Case 7: Array Type Checking

**Deskripsi**: Menguji type checking untuk array declarations dan access

**Input** (`test/milestone-3/input/test_arrays.pas`):
```pascal
program ArrayTest;

tipe
    Larik1D = larik [1..10] dari integer;

variabel
    arr: Larik1D;
    i: integer;
    r: real;
    b: boolean;

mulai
    i := 5;
    
    { OK: array access dengan integer index }
    arr[1] := 100;
    arr[i] := 200;
    i := arr[5];
    
    { ERROR: array index bukan integer }
    arr[r] := 300;     { ERROR: r adalah real }
    arr[b] := 400;     { ERROR: b adalah boolean }
    
    { ERROR: bukan array }
    i[5] := 100;       { ERROR: i bukan array }
    
    { OK: array element dalam expression }
    i := arr[1] + arr[2];
    arr[3] := arr[4] * 2;
selesai.
```

**Expected Output**:
```
ERROR: Array index must be integer
ERROR: Array index must be integer
ERROR: 'i' is not an array

Total Errors: 3
```

**Hasil**: ✅ PASS - Array type checking bekerja dengan benar

---

### Test Case 8: Function dan Procedure Call Checking

**Deskripsi**: Menguji type checking untuk function/procedure calls

**Input** (`test/milestone-3/input/test_functions.pas`):
```pascal
program FunctionTest;

variabel
    x, y: integer;
    z: real;

fungsi Add(a, b: integer): integer;
mulai
    Add := a + b;
selesai;

prosedur Print(msg: string);
mulai
    writeln(msg);
selesai;

mulai
    { OK: function call dengan correct types }
    x := Add(5, 10);
    y := Add(x, y);
    
    { OK: procedure call }
    Print('Hello');
    
    { ERROR: undefined function }
    x := Subtract(10, 5);  { ERROR: Subtract tidak dideklarasi }
    
    { ERROR: menggunakan procedure sebagai function }
    x := Print('test');    { ERROR: Print adalah procedure }
    
    { ERROR: menggunakan function sebagai procedure }
    Add(5, 10);            { WARNING/OK: function result diabaikan }
    
    { ERROR: menggunakan variable sebagai function }
    x := y(10);            { ERROR: y adalah variable, bukan function }
selesai.
```

**Expected Output**:
```
ERROR: Undeclared function 'Subtract'
ERROR: 'Print' is not a function
ERROR: 'y' is not a function

Total Errors: 3
```

**Hasil**: ✅ PASS - Function/procedure call validation bekerja

---

### Test Case 9: Nested Scopes dan Name Shadowing

**Deskripsi**: Menguji scope management dan symbol lookup hierarchy

**Input** (`test/milestone-3/input/test_scopes.pas`):
```pascal
program ScopeTest;

variabel
    x: integer;        { Global x }

prosedur Outer;
variabel
    x: real;           { Outer's x (shadows global) }
    y: integer;

    prosedur Inner;
    variabel
        x: boolean;    { Inner's x (shadows Outer's) }
    mulai
        x := true;     { Inner's x }
        y := 10;       { Outer's y (accessible) }
    selesai;

mulai
    x := 3.14;         { Outer's x }
    y := 20;
    Inner;
selesai;

mulai
    x := 100;          { Global x }
    Outer;
    y := 50;           { ERROR: y tidak accessible di global scope }
selesai.
```

**Expected Output**:
```
ERROR: Undeclared variable 'y'

Total Errors: 1
```

**Hasil**: ✅ PASS - Scope management dan name shadowing bekerja dengan benar

---

### Test Case 10: Complex Expression Type Inference

**Deskripsi**: Menguji type inference untuk ekspresi kompleks dengan multiple operators

**Input** (`test/milestone-3/input/test_complex_expr.pas`):
```pascal
program ComplexExprTest;

variabel
    i1, i2, i3: integer;
    r1, r2: real;
    b1, b2, b3: boolean;

mulai
    i1 := 10;
    i2 := 20;
    i3 := 30;
    r1 := 3.14;
    r2 := 2.71;
    b1 := true;
    b2 := false;
    
    { Complex arithmetic }
    r1 := (i1 + i2) * r1 / i3;        { OK: Result is REAL }
    i1 := (i1 + i2) * (i3 - 5);       { OK: Result is INTEGER }
    r2 := i1 * r1 + i2 / i3;          { OK: Result is REAL }
    
    { Complex boolean }
    b3 := (i1 > i2) dan (r1 < r2);    { OK: Result is BOOLEAN }
    b3 := (i1 = i2) atau (b1 dan b2); { OK: Result is BOOLEAN }
    b3 := tidak (i1 > i2);             { OK: Result is BOOLEAN }
    
    { Nested expressions }
    b3 := ((i1 + 5) > (i2 - 3)) dan ((r1 * 2.0) < (r2 + 1.0));  { OK }
    
    { ERROR: mixed incompatible types }
    i1 := (i1 + i2) dan b1;           { ERROR: cannot 'dan' with integer }
    b3 := (i1 + i2) > b1;             { ERROR: cannot compare integer with boolean }
    r1 := i1 + 'string';              { ERROR: cannot add integer and string }
selesai.
```

**Expected Output**:
```
ERROR: 'dan' requires boolean operands
ERROR: Cannot compare INTEGER with BOOLEAN
ERROR: Invalid operand types for '+'

Total Errors: 3
```

**Hasil**: ✅ PASS - Complex expression type inference bekerja dengan benar

---

### Rangkuman Test Cases

| Test Case | Kategori | Status | Errors Detected |
|-----------|----------|--------|-----------------|
| TC1 | Type Mismatch | ✅ PASS | 3/3 |
| TC2 | Undeclared Variables | ✅ PASS | 3/3 |
| TC3 | Duplicate Declarations | ✅ PASS | 3/3 |
| TC4 | Type Compatibility | ✅ PASS | 2/2 |
| TC5 | Control Flow | ✅ PASS | 3/3 |
| TC6 | Binary Operations | ✅ PASS | 4/4 |
| TC7 | Arrays | ✅ PASS | 3/3 |
| TC8 | Functions/Procedures | ✅ PASS | 3/3 |
| TC9 | Scopes | ✅ PASS | 1/1 |
| TC10 | Complex Expressions | ✅ PASS | 3/3 |

**Total**: 10 test cases, 28 distinct errors detected correctly

---

## 5. Kesimpulan

Implementasi semantic analysis untuk Pascal-S compiler telah berhasil diselesaikan dengan fitur-fitur utama:

1. **Complete Type System**: Mendukung semua tipe primitif dan array types
2. **Robust Error Detection**: 30+ jenis semantic errors dapat terdeteksi
3. **Symbol Table Management**: Hierarchical symbol table dengan scope support
4. **AST Decoration**: AST nodes didekorasi dengan informasi semantik untuk code generation
5. **Comprehensive Testing**: 10 test cases mencakup berbagai skenario error

Implementasi mengikuti prinsip-prinsip compiler design yang baik:
- **Separation of Concerns** melalui Visitor Pattern
- **Robustness** melalui error collection
- **Extensibility** melalui modular design
- **Efficiency** melalui single-pass analysis

Program siap untuk fase berikutnya: **Code Generation**.

---

**Referensi:**
- Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers: Principles, Techniques, and Tools* (2nd ed.)
- Wirth, N. (1996). *Compiler Construction*
- Fischer, C. N., Cytron, R. K., & LeBlanc, R. J. (2009). *Crafting a Compiler*
