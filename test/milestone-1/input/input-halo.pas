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
  b := -64.4E2 - 0.5E-3;
  Digit = 5; 
  (*iki opo 'woy lah, itu toh*)
  { bener }
  msg := 'bdfdf''';
  writeln(msg, Multiply(a, b));
end.
