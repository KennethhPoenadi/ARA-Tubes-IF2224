{ Test 1: Fully Valid Program }
{ This program demonstrates a complete, valid Pascal-S program }
{ with procedures, functions, variables, and mathematical operations }

program ProgramValid;

konstanta
    MAX_NILAI = 100;
    PI = 3;
    NAMA_PROGRAM = 'Semantic Analyzer Test';

variabel
    x, y, z: integer;
    hasil: real;
    selesaiFlag: boolean;
    karakter: char;

{ Fungsi untuk menghitung kuadrat }
fungsi kuadrat(n: integer): integer;
variabel
    temp: integer;
mulai
    temp := n * n
selesai;

{ Fungsi untuk menghitung faktorial }
fungsi faktorial(num: integer): integer;
variabel
    result: integer;
    i: integer;
mulai
    result := 1;
    untuk i := 1 ke num lakukan
        result := result * i
selesai;

{ Prosedur untuk menampilkan nilai }
prosedur tampilkan(nilai: integer; pesan: char);
mulai
    x := nilai;
    karakter := pesan
selesai;

{ Prosedur dengan banyak parameter }
prosedur hitungTotal(a, b, c: integer; flag: boolean);
variabel
    total: integer;
mulai
    total := a + b + c;
    jika flag maka
        x := total
    selain-itu
        y := total
selesai;

mulai
    { Inisialisasi variabel }
    x := 10;
    y := 20;
    z := MAX_NILAI;
    selesaiFlag := x > 0;
    karakter := 'A';
    
    { Operasi matematika }
    z := x + y * 2;
    z := (x + y) * 2;
    z := x / 2;
    z := y mod 3;
    
    { Panggil fungsi }
    x := kuadrat(5);
    y := faktorial(6);
    
    { Panggil prosedur }
    tampilkan(42, 'B');
    hitungTotal(1, 2, 3, x > 0);
    
    { Struktur kontrol if }
    jika x > y maka
        z := x - y
    selain-itu
        z := y - x;
    
    { Struktur kontrol while }
    selama x > 0 lakukan
    mulai
        x := x - 1;
        y := y + 1
    selesai;
    
    { Struktur kontrol for }
    untuk z := 1 ke 10 lakukan
        x := x + z;
    
    { Struktur kontrol repeat-until }
    ulangi
        y := y - 1
    sampai y = 0;
    
    { Operasi boolean }
    selesaiFlag := (x > 0) dan (y < 100);
    selesaiFlag := tidak selesaiFlag;
    selesaiFlag := selesaiFlag atau (x = 0);
    writeln()
selesai.
