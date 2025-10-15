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
  Digit = 5..9; 
  (*iki opo 'woy lah su toh*)
  { bener }
  msg := 'Product is ''halooooo'' kiri gua sub string ';
  writeln(msg, Multiply(a, b));
end.
