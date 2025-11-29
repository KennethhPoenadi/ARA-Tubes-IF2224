program TestSemanticError;

variabel
  x, y: integer;
  z: real;

mulai
  x := 10;
  y := x + 5;
  z := x + y;

  { Error: undeclared variable }
  w := 100;

  { Error: type mismatch - assigning string to integer }
  x := 'hello';

  { Error: using variable before declaration }
  a := b + c;

  { Error: wrong type in condition }
  jika x maka
    writeln('This is wrong');

  { Error: undeclared function }
  z := calculate(x, y);
selesai.
