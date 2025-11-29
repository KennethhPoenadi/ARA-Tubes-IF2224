program TestUnclosedComment;

{ Test case untuk unclosed comment }
{ Ini test case yang seharusnya error karena ada unclosed comment }

variabel
  x, y, z: integer;
  hasil: real;

mulai
  x := 10;
  y := 20;
  z := x + y;

  { Ini comment yang tidak ditutup
  hasil := z * 2.5;
  writeln('Hasil: ', hasil)
selesai.
