program TestComments;

{ Test case untuk berbagai jenis comment }

variabel
  x, y, z: integer;

mulai
  { Comment valid 1 }
  x := 10;

  (* Comment valid 2 *)
  y := 20;

  {
    Multi-line comment
    yang valid
  }
  z := x + y;

  (*
     Multi-line comment
     dengan style parenthesis-asterisk
  *)
  writeln('Hasil: ', z);

  { Comment dengan brackets tanpa nesting }
  x := x + 1;

  (* Comment dengan special chars !@#$%^& *)
  y := y * 2;

  writeln('Selesai')
selesai.
