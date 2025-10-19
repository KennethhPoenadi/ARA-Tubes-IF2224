
var = "ALL EXCEPT \', \\, a, b, c, \n"
var_except = var[len("ALL EXCEPT "):].split(", ")

for i in var_except:
    print(i)
print(var_except)