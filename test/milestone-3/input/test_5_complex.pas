{ Test 5: Complex Program with Arrays and Nested Loops }
{ This program tests complex AST structures with arrays, nested control structures }
{ and multi-level procedure/function calls }

program TestKompleks;

konstanta
    MAX_SIZE = 10;
    MIN_VALUE = 0;
    MULTIPLIER = 2;

variabel
    data: larik[1..10] dari integer;
    hasil: larik[1..10] dari integer;
    matrix: larik[1..5] dari integer;
    i, j, k: integer;
    total, rata: integer;
    selesaiProses: boolean;

{ Fungsi untuk mencari nilai maksimum dalam range }
fungsi cariMax(awalIdx, akhirIdx: integer): integer;
variabel
    maxVal: integer;
    idx: integer;
mulai
    maxVal := data[awalIdx];
    untuk idx := awalIdx ke akhirIdx lakukan
        jika data[idx] > maxVal maka
            maxVal := data[idx]
selesai;

{ Fungsi untuk menghitung jumlah dalam range }
fungsi hitungJumlah(awal, akhir: integer): integer;
variabel
    sum: integer;
    counter: integer;
mulai
    sum := 0;
    counter := awal;
    selama counter <= akhir lakukan
    mulai
        sum := sum + data[counter];
        counter := counter + 1
    selesai
selesai;

{ Prosedur untuk inisialisasi array }
prosedur initArray(dummy: integer);
variabel
    idx: integer;
mulai
    untuk idx := 1 ke MAX_SIZE lakukan
    mulai
        data[idx] := idx * MULTIPLIER;
        hasil[idx] := 0
    selesai
selesai;

{ Prosedur untuk proses nested loop }
prosedur prosesNested(dummy: integer);
variabel
    outer, inner: integer;
    tempSum: integer;
mulai
    { Nested for loops }
    untuk outer := 1 ke 5 lakukan
    mulai
        tempSum := 0;
        untuk inner := 1 ke outer lakukan
            tempSum := tempSum + data[inner];
        matrix[outer] := tempSum
    selesai;
    
    { Nested while dalam for }
    untuk outer := 1 ke MAX_SIZE lakukan
    mulai
        inner := 1;
        selama inner <= outer lakukan
        mulai
            hasil[outer] := hasil[outer] + data[inner];
            inner := inner + 1
        selesai
    selesai
selesai;

{ Prosedur dengan repeat-until dan if nested }
prosedur prosesKondisi(dummy: integer);
variabel
    counter: integer;
    temp: integer;
mulai
    counter := 1;
    ulangi
        { Nested if statements }
        jika data[counter] > 10 maka
            jika data[counter] > 15 maka
                hasil[counter] := data[counter] * 2
            selain-itu
                hasil[counter] := data[counter] + 5
        selain-itu
            jika data[counter] > 5 maka
                hasil[counter] := data[counter] + 2
            selain-itu
                hasil[counter] := data[counter];
        
        counter := counter + 1
    sampai counter > MAX_SIZE
selesai;

{ Prosedur utama yang memanggil semua prosedur lain }
prosedur mainProses(dummy: integer);
variabel
    maxVal: integer;
    sumVal: integer;
mulai
    { Panggil prosedur inisialisasi }
    initArray(0);
    
    { Panggil prosedur nested loop }
    prosesNested(0);
    
    { Panggil prosedur kondisi }
    prosesKondisi(0);
    
    { Panggil fungsi-fungsi }
    maxVal := cariMax(1, MAX_SIZE);
    sumVal := hitungJumlah(1, 5);
    
    { Simpan hasil ke variabel global }
    total := sumVal;
    
    { Kalkulasi rata-rata }
    rata := total / 5;
    
    { Set flag selesai }
    selesaiProses := total > 0
selesai;

mulai
    { Inisialisasi variabel global }
    i := 0;
    j := 0;
    k := 0;
    total := 0;
    rata := 0;
    selesaiProses := total = 0;
    
    { Inisialisasi array secara manual sebagai backup }
    untuk i := 1 ke MAX_SIZE lakukan
        data[i] := i;
    
    { Panggil main proses }
    mainProses(0);
    
    { Proses tambahan dengan nested structures }
    i := 1;
    selama i <= 5 lakukan
    mulai
        j := 1;
        selama j <= 5 lakukan
        mulai
            k := data[i] + data[j];
            
            jika k > 10 maka
                jika k mod 2 = 0 maka
                    total := total + k
                selain-itu
                    total := total + 1
            selain-itu
                total := total;
            
            j := j + 1
        selesai;
        i := i + 1
    selesai;
    
    { Loop downto }
    untuk i := MAX_SIZE turun-ke 1 lakukan
        hasil[i] := hasil[i] + i;
    
    { Final calculation }
    total := hitungJumlah(1, MAX_SIZE);
    rata := total / MAX_SIZE;
    selesaiProses := total > 0
selesai.
