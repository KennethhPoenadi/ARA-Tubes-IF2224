program TestBrutal;

{ Test case brutal untuk parser Pascal-S Bahasa Indonesia }
{ Mencakup: array 1D, nested control flow, expressions, functions, procedures }

konstanta
    MAX = 100;
    MIN = 1;
    PI = 3.14159;
    PESAN = 'Halo Dunia';
    NEWLINE = '\n';

variabel
    i, j, k, count, total: integer;
    avg, sum, result: real;
    arr, data, sorted: larik[1..10] dari integer;
    scores: larik[0..20] dari real;
    huruf: larik[1..26] dari char;
    found, valid, isDone: boolean;
    ch: char;

fungsi Fibonacci(n: integer): integer;
variabel
    a, b, temp, idx: integer;
mulai
    jika n <= 1 maka
        Fibonacci := n
    selain-itu
    mulai
        a := 0;
        b := 1;
        untuk idx := 2 ke n lakukan
        mulai
            temp := a + b;
            a := b;
            b := temp
        selesai;
        Fibonacci := b
    selesai
selesai;

fungsi IsPrime(num: integer): boolean;
variabel
    idx: integer;
    isPrime: boolean;
mulai
    isPrime := true;
    jika num <= 1 maka
        isPrime := false
    selain-itu
    mulai
        idx := 2;
        selama (idx * idx <= num) dan isPrime lakukan
        mulai
            jika num mod idx = 0 maka
                isPrime := false;
            idx := idx + 1
        selesai
    selesai;
    IsPrime := isPrime
selesai;

fungsi Max(a, b: integer): integer;
mulai
    jika a > b maka
        Max := a
    selain-itu
        Max := b
selesai;

fungsi Min(a, b: integer): integer;
mulai
    jika a < b maka
        Min := a
    selain-itu
        Min := b
selesai;

prosedur BubbleSort(n: integer);
variabel
    idx, jdx, temp: integer;
    swapped: boolean;
mulai
    untuk idx := 1 ke n - 1 lakukan
    mulai
        swapped := false;
        untuk jdx := 1 ke n - idx lakukan
        mulai
            jika arr[jdx] > arr[jdx + 1] maka
            mulai
                temp := arr[jdx];
                arr[jdx] := arr[jdx + 1];
                arr[jdx + 1] := temp;
                swapped := true
            selesai
        selesai;
        jika tidak swapped maka
            idx := n
    selesai
selesai;

prosedur PrintArray(n: integer);
variabel
    idx: integer;
mulai
    untuk idx := 1 ke n lakukan
    mulai
        write(arr[idx]);
        jika idx < n maka
            write(' ')
    selesai;
    writeln()
selesai;

prosedur InitArray(n: integer);
variabel
    idx: integer;
mulai
    untuk idx := 1 ke n lakukan
        arr[idx] := (n - idx + 1) * 2
selesai;

mulai
    { Test 1: Array operations dengan nested loops }
    writeln('=== Test 1: Array Operations ===');
    InitArray(10);
    writeln('Array setelah inisialisasi:');
    PrintArray(10);

    { Test 2: Nested if-else dengan complex expressions }
    writeln('=== Test 2: Complex Conditionals ===');
    count := 0;
    total := 0;
    untuk i := 1 ke 10 lakukan
    mulai
        jika IsPrime(arr[i]) maka
        mulai
            writeln(arr[i], ' adalah bilangan prima');
            count := count + 1;
            total := total + arr[i]
        selesai
        selain-itu
        mulai
            jika arr[i] mod 2 = 0 maka
                writeln(arr[i], ' adalah bilangan genap')
            selain-itu
                writeln(arr[i], ' adalah bilangan ganjil')
        selesai
    selesai;

    { Test 3: While loop dengan logical operators }
    writeln('=== Test 3: While Loop ===');
    i := 1;
    sum := 0.0;
    selama (i <= 10) dan (sum < 100.0) lakukan
    mulai
        sum := sum + (i * 1.5);
        writeln('Iterasi ', i, ': sum = ', sum);
        i := i + 1
    selesai;

    { Test 4: For loop turun-ke }
    writeln('=== Test 4: Countdown ===');
    untuk i := 10 turun-ke 1 lakukan
    mulai
        jika i mod 3 = 0 maka
            writeln('Fizz')
        selain-itu
            jika i mod 5 = 0 maka
                writeln('Buzz')
            selain-itu
                writeln(i)
    selesai;

    { Test 5: Repeat-until loop }
    writeln('=== Test 5: Repeat Until ===');
    k := 0;
    ulangi
        k := k + 1;
        writeln('Fibonacci(', k, ') = ', Fibonacci(k))
    sampai k >= 10;

    { Test 6: Complex arithmetic expressions }
    writeln('=== Test 6: Arithmetic ===');
    result := ((10.5 + 20.3) * 3.0 - 15.0) / 2.5;
    writeln('Expression result: ', result);

    i := 17;
    j := 5;
    writeln(i, ' bagi ', j, ' = ', i bagi j);
    writeln(i, ' mod ', j, ' = ', i mod j);
    writeln(i, ' / ', j, ' = ', i / j);

    { Test 7: Relational dan logical operators }
    writeln('=== Test 7: Logical Operations ===');
    valid := (MAX > MIN) dan (PI > 3.0) dan tidak (count = 0);
    jika valid maka
        writeln('Semua kondisi terpenuhi')
    selain-itu
        writeln('Ada kondisi yang tidak terpenuhi');

    found := (i > j) atau (j < 0);
    isDone := tidak found dan valid;

    jika (i >= 10) dan (j <= 10) maka
        writeln('i >= 10 dan j <= 10')
    selain-itu
        jika i <> j maka
            writeln('i tidak sama dengan j');

    { Test 8: String operations }
    writeln('=== Test 8: String Operations ===');
    writeln(PESAN);
    writeln('Panjang pesan: 10 karakter');

    { Test 9: Nested procedure calls dan functions }
    writeln('=== Test 9: Sorting ===');
    writeln('Sebelum sorting:');
    PrintArray(10);

    BubbleSort(10);

    writeln('Setelah sorting:');
    PrintArray(10);

    { Test 10: Function calls dalam expressions }
    writeln('=== Test 10: Function Calls ===');
    i := Max(15, 20);
    j := Min(15, 20);
    writeln('Max(15, 20) = ', i);
    writeln('Min(15, 20) = ', j);

    k := Max(Fibonacci(5), Fibonacci(6));
    writeln('Max(Fib(5), Fib(6)) = ', k);

    { Test 11: Array dengan real numbers }
    writeln('=== Test 11: Real Arrays ===');
    untuk i := 0 ke 10 lakukan
        scores[i] := i * 1.5;

    sum := 0.0;
    untuk i := 0 ke 10 lakukan
        sum := sum + scores[i];

    avg := sum / 11.0;
    writeln('Rata-rata scores: ', avg);

    { Test 12: Edge cases dan complex conditions }
    writeln('=== Test 12: Edge Cases ===');

    jika count > 0 maka
    mulai
        avg := total bagi count;
        writeln('Rata-rata bilangan prima: ', avg);
        result := total / count;
        writeln('Hasil pembagian real: ', result)
    selesai
    selain-itu
        writeln('Tidak ada bilangan prima ditemukan');

    { Test 13: Nested for loops }
    writeln('=== Test 13: Nested Loops ===');
    total := 0;
    untuk i := 1 ke 5 lakukan
        untuk j := 1 ke 5 lakukan
            total := total + (i * j);

    writeln('Total dari nested loops: ', total);

    { Test 14: Deep nesting }
    writeln('=== Test 14: Deep Nesting ===');
    untuk i := 1 ke 3 lakukan
    mulai
        jika i mod 2 = 0 maka
        mulai
            untuk j := 1 ke 3 lakukan
            mulai
                jika j > 1 maka
                    writeln('i=', i, ', j=', j)
                selain-itu
                    writeln('Skip')
            selesai
        selesai
        selain-itu
            writeln('i adalah ganjil: ', i)
    selesai;

    { Test 15: Operator precedence }
    writeln('=== Test 15: Operator Precedence ===');
    i := 10 + 20 * 3 - 5;
    writeln('10 + 20 * 3 - 5 = ', i);

    valid := (5 > 3) dan (10 < 20) atau (15 = 15);
    jika valid maka
        writeln('Complex boolean expression is true');

    writeln('=== Program Selesai ===')
selesai.
