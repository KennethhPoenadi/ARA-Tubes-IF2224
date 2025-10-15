program booleanTest;

var
  flag : boolean;
  x : integer;

begin
  if ( flag = true ) and ( x > 5 ) then
    writeln('Condition met')
  else
    writeln('Condition not met');
end.
