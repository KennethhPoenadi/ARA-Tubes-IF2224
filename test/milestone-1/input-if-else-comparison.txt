program ConditionTest;

var
  a, b: integer;

begin
  a := 15;
  b := 20;

  if a < b then
    writeln('a is less than b')
  else
    writeln('a is greater or equal to b');
end.
