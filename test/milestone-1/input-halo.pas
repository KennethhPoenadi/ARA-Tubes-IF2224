program Complex;

var
  a, b: integer;
  msg: string;

function Multiply(x, y: integer): integer;
begin
  Multiply := x * y;
end;

begin
  a := 4;
  b := -64.4E+2 - 80;
  msg := 'Product is ''halooooo'' ';
  writeln(msg, Multiply(a, b));
end.
