program ArrayTest;

variabel
  arr: larik[1..5] dari integer;
  i: integer;

mulai
  untuk i := 1 ke 5 lakukan
    arr[i] := i * 2;

  i := 1;
  selama i <= 5 lakukan
  mulai
    writeln('arr[', i, '] = ', arr[i]);
    i := i + 1;
  selesai;
selesai.
