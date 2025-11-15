program KompleksTest;

konstanta
  MAX = 100;
  MIN = 0;

tipe
  Rentang = 1..10;

variabel
  x, y, z: integer;
  arr: larik[1..5] dari integer;

prosedur cetak(msg: string);
mulai
  writeln(msg);
selesai;

fungsi tambah(a, b: integer): integer;
mulai
  tambah := a + b;
selesai;

mulai
  x := 5;
  y := 10;
  z := tambah(x, y);

  cetak('Hasil penjumlahan:');
  writeln(z);

  jika z > 10 maka
    cetak('z lebih besar dari 10')
  selain-itu
    cetak('z tidak lebih besar dari 10');

  untuk x := 1 ke 5 lakukan
    arr[x] := x * x;

  selama y > 0 lakukan
  mulai
    y := y - 1;
    writeln(y);
  selesai;
selesai.
