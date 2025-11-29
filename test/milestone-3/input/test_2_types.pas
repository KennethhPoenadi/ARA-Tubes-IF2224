{ Test 2: Type Mismatch Errors }
{ This program contains deliberate type errors to test semantic analysis }
{ Expected errors: type mismatch in assignments and operations }

program TestTypeMismatch;

variabel
    angka: integer;
    desimal: real;
    bendera: boolean;
    huruf: char;
    teks: string;

fungsi hitungJumlah(a: integer; b: integer): integer;
mulai
    angka := a + b
selesai;

prosedur prosesData(x: integer; flag: boolean);
mulai
    angka := x
selesai;

mulai
    { Inisialisasi yang benar }
    angka := 10;
    desimal := 3;
    bendera := angka > 0;
    huruf := 'X';
    
    { ERROR 1: Assign boolean ke integer }
    angka := angka > 5;
    
    { ERROR 2: Assign integer ke boolean }
    bendera := 42;
    
    { ERROR 3: Assign string ke integer }
    angka := 'hello';
    
    { ERROR 4: Assign char ke boolean }
    bendera := huruf;
    
    { ERROR 5: Operasi aritmatika dengan boolean }
    angka := angka + bendera;
    
    { ERROR 6: Operasi aritmatika dengan string }
    angka := angka * teks;
    
    { ERROR 7: Operasi boolean dengan integer }
    bendera := bendera dan angka;
    
    { ERROR 8: Perbandingan tipe yang tidak kompatibel }
    bendera := angka < bendera;
    
    { ERROR 9: Argument fungsi dengan tipe salah }
    angka := hitungJumlah(angka > 5, 5);
    
    { ERROR 10: Argument prosedur dengan tipe salah }
    prosesData(teks, 123)
selesai.
