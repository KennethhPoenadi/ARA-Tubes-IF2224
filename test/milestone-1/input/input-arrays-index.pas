program Arrays;
var
  nums: array[1..5] of integer;
  i: integer;

begin
  for i := 1 to 5 do
    nums[i] := i * 2;

  writeln('Fourth element = ', nums[4]);
end.
