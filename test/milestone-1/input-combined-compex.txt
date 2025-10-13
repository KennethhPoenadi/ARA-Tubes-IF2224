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
  b := 5;
  msg := 'Product is ';
  writeln(msg, Multiply(a, b));
end.
