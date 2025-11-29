{ Test 4: Undeclared Variable Errors }
{ This program uses variables and identifiers that have not been declared }
{ Expected errors: undeclared variable, undeclared procedure, undeclared function }

program TestUndeclared;

variabel
    x: integer;
    y: integer;
    flag: boolean;

prosedur prosesNilai(a: integer);
variabel
    temp: integer;
mulai
    temp := a;
    x := temp
selesai;

fungsi kuadrat(n: integer): integer;
mulai
    x := n * n
selesai;

mulai
    { Inisialisasi yang benar }
    x := 10;
    y := 20;
    flag := x > 0;
    
    { ERROR 1: Menggunakan variabel yang belum dideklarasikan }
    z := 100;
    
    { ERROR 2: Menggunakan variabel undeclared di sisi kanan }
    x := tidakAda + 5;
    
    { ERROR 3: Menggunakan variabel undeclared dalam ekspresi }
    y := x + belumDeklarasi * 2;
    
    { ERROR 4: Variabel undeclared dalam kondisi if }
    jika kondisiTidakAda maka
        x := 1;
    
    { ERROR 5: Variabel undeclared dalam loop while }
    selama counterTidakAda > 0 lakukan
        x := x + 1;
    
    { ERROR 6: Variabel undeclared dalam loop for }
    untuk iTidakAda := 1 ke 10 lakukan
        y := y + 1;
    
    { ERROR 7: Memanggil prosedur yang tidak ada }
    prosedurTidakAda(10);
    
    { ERROR 8: Memanggil fungsi yang tidak ada }
    x := fungsiTidakAda(5);
    
    { ERROR 9: Menggunakan konstanta yang belum dideklarasikan }
    x := KONSTANTA_TIDAK_ADA;
    
    { ERROR 10: Akses array yang tidak dideklarasikan }
    x := arrayTidakAda[1];
    
    { ERROR 11: Multiple undeclared dalam satu statement }
    hasil := nilaiA + nilaiB * nilaiC
selesai.
