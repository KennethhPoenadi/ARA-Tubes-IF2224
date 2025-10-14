program Variables;

var
  x, y, z: integer;
  message: string;

begin
  x := 10;
  y := 20;
  z := x + y;
  message := 'Sum is ';
  writeln(message, z);
end.
