program FaktorialProgram;

variabel
  n, hasil: integer;

fungsi faktorial(x: integer): integer;
variabel
  i, temp: integer;
mulai
  temp := 1;
  untuk i := 1 ke x lakukan
    temp := temp * i;
  faktorial := temp;
selesai;

mulai
  n := 5;
  hasil := faktorial(n);
  writeln('Faktorial dari ', n, ' adalah ', hasil);
selesai.
