program Loops;

var
  i: integer;

begin
  for i := 1 to 5 do
    writeln('Count: ', i);

  i := 0;
  while i < 3 do
  begin
    writeln('Loop ', i);
    i := i + 1;
  end;

  repeat
    i := i - 1;
  until i = 0;
end.
