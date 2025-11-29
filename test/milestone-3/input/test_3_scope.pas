{ Test 3: Scope Shadowing }
{ This program tests variable scope and shadowing behavior }
{ Global variables can be shadowed by local variables with the same name }

program TestScopeShadowing;

konstanta
    GLOBAL_CONST = 100;

variabel
    x: integer;         { Global x - level 0 }
    y: integer;         { Global y - level 0 }
    total: integer;     { Global total - level 0 }

{ Prosedur dengan variabel lokal yang shadow variabel global }
prosedur prosesShadow(dummy: integer);
variabel
    x: integer;         { Local x - level 1, shadows global x }
    temp: integer;      { Local only - level 1 }
mulai
    { x di sini adalah local x, bukan global }
    x := 50;
    temp := x + 10;
    
    { y di sini adalah global y karena tidak ada local y }
    y := temp;
    
    { total adalah global }
    total := x + y
selesai;

{ Fungsi dengan parameter yang shadow variabel global }
fungsi hitungNilai(x: integer): integer;   { Parameter x shadows global x }
variabel
    result: integer;
mulai
    { x di sini adalah parameter x }
    result := x * 2;
    
    { y masih mengacu ke global y }
    result := result + y
selesai;

{ Test akses variabel dari scope yang berbeda }
prosedur testAkses(nilai: integer);
variabel
    lokal: integer;
mulai
    lokal := nilai;
    x := lokal;         { Ini adalah global x }
    y := GLOBAL_CONST;  { Akses konstanta global }
    total := x + y + lokal
selesai;

mulai
    { Inisialisasi global }
    x := 1;
    y := 2;
    total := 0;
    
    { Call procedure yang akan shadow x }
    prosesShadow(0);
    
    { Setelah prosesShadow: x global tidak berubah (karena yg diubah adalah local x) }
    { tapi y dan total global sudah berubah }
    
    { Call function dengan shadowing via parameter }
    total := hitungNilai(25);
    
    { Call procedure untuk test akses scope }
    testAkses(42)
selesai.
