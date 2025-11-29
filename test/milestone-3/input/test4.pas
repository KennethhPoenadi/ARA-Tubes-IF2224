program Kondisional;

variabel
  x, y: integer;

mulai
  x := 10;
  y := 20;

  jika x < y maka
    writeln('x lebih kecil dari y')
  selain-itu
    writeln('x lebih besar atau sama dengan y');

  jika x > 5 maka
  mulai
    writeln('x lebih besar dari 5');
    x := x * 2;
  selesai;
selesai.
