# parser untuk pascal-s dengan bahasa indonesia
# pake recursive descent buat parsing token jadi parse tree

# class buat nampung token supaya lebih gampang dipake
class Token:
    def __init__(self, token_type, value):
        self.type = token_type
        self.value = value

    def __repr__(self):
        return f"{self.type}({self.value})"

# parser utama pake recursive descent
class Parser:
    def __init__(self, tokens):
        # convert tuple dari lexer jadi object Token
        self.tokens = [Token(t[0], t[1]) for t in tokens]
        self.pos = 0
        self.current_token = self.tokens[0] if self.tokens else None

    def error(self, message):
        # throw error dengan posisi token sekarang
        raise Exception(f"Syntax error at position {self.pos}: {message}")

    def peek(self, offset=0):
        # liat token ke depan tanpa advance posisi
        index = self.pos + offset
        if index < len(self.tokens):
            return self.tokens[index]
        return None

    def advance(self):
        # maju ke token selanjutnya
        if self.pos < len(self.tokens):
            self.pos += 1
            self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None
        return self.current_token

    def expect(self, token_type, value=None):
        # cek apakah current token sesuai yang diharapkan
        if not self.current_token:
            self.error(f"Expected {token_type}, but reached end of input")
        if self.current_token.type != token_type:
            expected_str = f"{token_type}({self.get_expected_value(token_type)})"
            self.error(f"unexpected token {self.current_token.type}({self.current_token.value}), expected {expected_str}")
        if value and self.current_token.value.lower() != value.lower():
            self.error(f"unexpected token {self.current_token.value}, expected {value}")
        token = self.current_token
        self.advance()
        return token

    def get_expected_value(self, token_type):
        # mapping token type ke simbol buat error message yang lebih jelas
        common_values = {
            "SEMICOLON": ";",
            "COLON": ":",
            "COMMA": ",",
            "DOT": ".",
            "LPARENTHESIS": "(",
            "RPARENTHESIS": ")",
            "LBRACKET": "[",
            "RBRACKET": "]",
            "ASSIGN_OPERATOR": ":=",
            "RANGE_OPERATOR": ".."
        }
        return common_values.get(token_type, "")

    def match(self, token_type, value=None):
        # cek apa current token cocok tanpa consume tokennya
        if not self.current_token:
            return False
        if self.current_token.type != token_type:
            return False
        if value and self.current_token.value.lower() != value.lower():
            return False
        return True

    def parse(self):
        # entry point parsing, mulai dari <program>
        return self.parse_program()

    # grammar: <program> ::= <program-header> <declaration-part> <compound-statement> .
    def parse_program(self):
        node = {"type": "<program>", "children": []}
        node["children"].append(self.parse_program_header())
        node["children"].append(self.parse_declaration_part())
        node["children"].append(self.parse_compound_statement())
        node["children"].append(self.expect("DOT"))
        return node

    # grammar: <program-header> ::= program <identifier> ;
    def parse_program_header(self):
        node = {"type": "<program-header>", "children": []}
        node["children"].append(self.expect("KEYWORD", "program"))
        node["children"].append(self.expect("IDENTIFIER"))
        node["children"].append(self.expect("SEMICOLON"))
        return node

    # parse bagian deklarasi (konstanta, tipe, variabel, prosedur/fungsi)
    def parse_declaration_part(self):
        node = {"type": "<declaration-part>", "children": []}

        # parse semua deklarasi konstanta kalo ada
        while self.match("KEYWORD", "konstanta"):
            node["children"].append(self.parse_const_declaration())

        # parse semua deklarasi tipe kalo ada
        while self.match("KEYWORD", "tipe"):
            node["children"].append(self.parse_type_declaration())

        # parse semua deklarasi variabel kalo ada
        while self.match("KEYWORD", "variabel"):
            node["children"].append(self.parse_var_declaration())

        # parse semua prosedur/fungsi kalo ada
        while self.match("KEYWORD", "prosedur") or self.match("KEYWORD", "fungsi"):
            node["children"].append(self.parse_subprogram_declaration())

        return node

    # parse deklarasi konstanta
    def parse_const_declaration(self):
        node = {"type": "<const-declaration>", "children": []}
        node["children"].append(self.expect("KEYWORD", "konstanta"))

        while True:
            node["children"].append(self.expect("IDENTIFIER"))
            node["children"].append(self.expect("RELATIONAL_OPERATOR", "="))

            # value bisa number, char, string, atau identifier lain
            if self.match("NUMBER") or self.match("CHAR_LITERAL") or self.match("STRING_LITERAL"):
                node["children"].append(self.current_token)
                self.advance()
            elif self.match("IDENTIFIER"):
                node["children"].append(self.expect("IDENTIFIER"))
            else:
                self.error("Expected constant value")

            node["children"].append(self.expect("SEMICOLON"))

            # kalo gak ada identifier lagi berarti udah selesai
            if not self.match("IDENTIFIER"):
                break

        return node

    # parse deklarasi tipe
    def parse_type_declaration(self):
        node = {"type": "<type-declaration>", "children": []}
        node["children"].append(self.expect("KEYWORD", "tipe"))

        while True:
            node["children"].append(self.expect("IDENTIFIER"))
            node["children"].append(self.expect("RELATIONAL_OPERATOR", "="))
            node["children"].append(self.parse_type())
            node["children"].append(self.expect("SEMICOLON"))

            if not self.match("IDENTIFIER"):
                break

        return node

    # parse deklarasi variabel
    def parse_var_declaration(self):
        node = {"type": "<var-declaration>", "children": []}
        node["children"].append(self.expect("KEYWORD", "variabel"))

        while True:
            node["children"].append(self.parse_identifier_list())
            node["children"].append(self.expect("COLON"))
            node["children"].append(self.parse_type())
            node["children"].append(self.expect("SEMICOLON"))

            if not self.match("IDENTIFIER"):
                break

        return node

    # parse list identifier yang dipisah koma (misal: x, y, z)
    def parse_identifier_list(self):
        node = {"type": "<identifier-list>", "children": []}
        node["children"].append(self.expect("IDENTIFIER"))

        while self.match("COMMA"):
            node["children"].append(self.expect("COMMA"))
            node["children"].append(self.expect("IDENTIFIER"))

        return node

    # parse tipe data (primitif, array, atau custom type)
    def parse_type(self):
        node = {"type": "<type>", "children": []}

        if self.match("KEYWORD", "larik"):
            # array type
            node["children"].append(self.parse_array_type())
        elif self.match("KEYWORD"):
            # primitive type (integer, real, boolean, char, string)
            if self.current_token.value.lower() in ["integer", "real", "boolean", "char", "string"]:
                node["children"].append(self.current_token)
                self.advance()
            else:
                self.error("Expected type keyword")
        elif self.match("IDENTIFIER"):
            # custom type (user-defined)
            node["children"].append(self.expect("IDENTIFIER"))
        elif self.match("NUMBER") or self.match("CHAR_LITERAL"):
            # range type
            node["children"].append(self.parse_range())
        else:
            self.error("Expected type")

        return node

    # parse tipe array (larik[1..10] dari integer)
    def parse_array_type(self):
        node = {"type": "<array-type>", "children": []}
        node["children"].append(self.expect("KEYWORD", "larik"))
        node["children"].append(self.expect("LBRACKET"))
        node["children"].append(self.parse_range())
        node["children"].append(self.expect("RBRACKET"))
        node["children"].append(self.expect("KEYWORD", "dari"))
        node["children"].append(self.parse_type())
        return node

    # parse range (1..10 atau 'a'..'z')
    def parse_range(self):
        node = {"type": "<range>", "children": []}
        node["children"].append(self.parse_expression())
        node["children"].append(self.expect("RANGE_OPERATOR"))
        node["children"].append(self.parse_expression())
        return node

    # parse deklarasi prosedur atau fungsi
    def parse_subprogram_declaration(self):
        if self.match("KEYWORD", "prosedur"):
            return self.parse_procedure_declaration()
        elif self.match("KEYWORD", "fungsi"):
            return self.parse_function_declaration()
        else:
            self.error("Expected procedure or function")

    # parse deklarasi prosedur
    def parse_procedure_declaration(self):
        node = {"type": "<procedure-declaration>", "children": []}
        node["children"].append(self.expect("KEYWORD", "prosedur"))
        node["children"].append(self.expect("IDENTIFIER"))

        # parameter list opsional
        if self.match("LPARENTHESIS"):
            node["children"].append(self.parse_formal_parameter_list())

        node["children"].append(self.expect("SEMICOLON"))
        node["children"].append(self.parse_block())
        node["children"].append(self.expect("SEMICOLON"))
        return node

    # parse deklarasi fungsi
    def parse_function_declaration(self):
        node = {"type": "<function-declaration>", "children": []}
        node["children"].append(self.expect("KEYWORD", "fungsi"))
        node["children"].append(self.expect("IDENTIFIER"))

        # parameter list opsional
        if self.match("LPARENTHESIS"):
            node["children"].append(self.parse_formal_parameter_list())

        # return type
        node["children"].append(self.expect("COLON"))
        node["children"].append(self.parse_type())
        node["children"].append(self.expect("SEMICOLON"))
        node["children"].append(self.parse_block())
        node["children"].append(self.expect("SEMICOLON"))
        return node

    # parse formal parameter list (misal: (x, y: integer; z: real))
    def parse_formal_parameter_list(self):
        node = {"type": "<formal-parameter-list>", "children": []}
        node["children"].append(self.expect("LPARENTHESIS"))

        node["children"].append(self.parse_parameter_group())

        # multiple parameter groups dipisah semicolon
        while self.match("SEMICOLON"):
            node["children"].append(self.expect("SEMICOLON"))
            node["children"].append(self.parse_parameter_group())

        node["children"].append(self.expect("RPARENTHESIS"))
        return node

    # parse satu group parameter (x, y: integer)
    def parse_parameter_group(self):
        node = {"type": "<parameter-group>", "children": []}
        node["children"].append(self.parse_identifier_list())
        node["children"].append(self.expect("COLON"))
        node["children"].append(self.parse_type())
        return node

    # parse block (deklarasi + statement)
    def parse_block(self):
        node = {"type": "<block>", "children": []}
        node["children"].append(self.parse_declaration_part())
        node["children"].append(self.parse_compound_statement())
        return node

    # parse compound statement (mulai...selesai)
    def parse_compound_statement(self):
        node = {"type": "<compound-statement>", "children": []}
        node["children"].append(self.expect("KEYWORD", "mulai"))
        node["children"].append(self.parse_statement_list())
        node["children"].append(self.expect("KEYWORD", "selesai"))
        return node

    # parse list statement yang dipisah semicolon
    def parse_statement_list(self):
        node = {"type": "<statement-list>", "children": []}
        node["children"].append(self.parse_statement())

        while self.match("SEMICOLON"):
            node["children"].append(self.expect("SEMICOLON"))
            # kalo ketemu 'selesai' atau 'sampai' berarti udah akhir list
            if not self.match("KEYWORD", "selesai") and not self.match("KEYWORD", "sampai"):
                node["children"].append(self.parse_statement())
            else:
                break

        # validasi akhir statement list
        if not self.match("KEYWORD", "selesai") and not self.match("KEYWORD", "sampai") and not self.match("SEMICOLON"):
            self.error(f"Expected SEMICOLON(;) or KEYWORD(selesai/sampai), but got {self.current_token}")

        return node

    # parse statement (if, while, for, repeat, assignment, procedure call)
    def parse_statement(self):
        if self.match("KEYWORD", "mulai"):
            return self.parse_compound_statement()
        elif self.match("KEYWORD", "jika"):
            return self.parse_if_statement()
        elif self.match("KEYWORD", "selama"):
            return self.parse_while_statement()
        elif self.match("KEYWORD", "untuk"):
            return self.parse_for_statement()
        elif self.match("KEYWORD", "ulangi"):
            return self.parse_repeat_statement()
        elif self.match("IDENTIFIER"):
            # liat next token buat bedain assignment vs procedure call
            peek = self.peek(1)
            if peek and (peek.type == "ASSIGN_OPERATOR" or peek.type == "LBRACKET"):
                return self.parse_assignment_statement()
            else:
                return self.parse_procedure_call()
        elif self.match("KEYWORD") and self.current_token.value.lower() in ["writeln", "write", "readln", "read"]:
            # built-in procedures
            return self.parse_procedure_call()
        else:
            # empty statement
            return {"type": "<empty-statement>", "children": []}

    # parse assignment (x := 10 atau arr[i] := 5)
    def parse_assignment_statement(self):
        node = {"type": "<assignment-statement>", "children": []}
        node["children"].append(self.expect("IDENTIFIER"))

        # array indexing opsional
        if self.match("LBRACKET"):
            node["children"].append(self.expect("LBRACKET"))
            node["children"].append(self.parse_expression())
            node["children"].append(self.expect("RBRACKET"))

        node["children"].append(self.expect("ASSIGN_OPERATOR"))
        node["children"].append(self.parse_expression())
        return node

    # parse if statement (jika...maka...selain-itu)
    def parse_if_statement(self):
        node = {"type": "<if-statement>", "children": []}
        node["children"].append(self.expect("KEYWORD", "jika"))
        node["children"].append(self.parse_expression())
        node["children"].append(self.expect("KEYWORD", "maka"))
        node["children"].append(self.parse_statement())

        # else clause opsional
        if self.match("KEYWORD", "selain-itu"):
            node["children"].append(self.expect("KEYWORD", "selain-itu"))
            node["children"].append(self.parse_statement())

        return node

    # parse while loop (selama...lakukan)
    def parse_while_statement(self):
        node = {"type": "<while-statement>", "children": []}
        node["children"].append(self.expect("KEYWORD", "selama"))
        node["children"].append(self.parse_expression())
        node["children"].append(self.expect("KEYWORD", "lakukan"))
        node["children"].append(self.parse_statement())
        return node

    # parse for loop (untuk...ke/turun-ke...lakukan)
    def parse_for_statement(self):
        node = {"type": "<for-statement>", "children": []}
        node["children"].append(self.expect("KEYWORD", "untuk"))
        node["children"].append(self.expect("IDENTIFIER"))
        node["children"].append(self.expect("ASSIGN_OPERATOR"))
        node["children"].append(self.parse_expression())

        # direction bisa 'ke' (increment) atau 'turun-ke' (decrement)
        if self.match("KEYWORD", "ke"):
            node["children"].append(self.expect("KEYWORD", "ke"))
        elif self.match("KEYWORD", "turun-ke"):
            node["children"].append(self.expect("KEYWORD", "turun-ke"))
        else:
            self.error("Expected 'ke' or 'turun-ke'")

        node["children"].append(self.parse_expression())
        node["children"].append(self.expect("KEYWORD", "lakukan"))
        node["children"].append(self.parse_statement())
        return node

    # parse repeat-until loop (ulangi...sampai)
    def parse_repeat_statement(self):
        node = {"type": "<repeat-statement>", "children": []}
        node["children"].append(self.expect("KEYWORD", "ulangi"))
        node["children"].append(self.parse_statement_list())
        node["children"].append(self.expect("KEYWORD", "sampai"))
        node["children"].append(self.parse_expression())
        return node

    # parse procedure/function call
    def parse_procedure_call(self):
        node = {"type": "<procedure/function-call>", "children": []}

        # procedure name bisa keyword (writeln) atau identifier
        if self.match("KEYWORD"):
            node["children"].append(self.current_token)
            self.advance()
        else:
            node["children"].append(self.expect("IDENTIFIER"))

        node["children"].append(self.expect("LPARENTHESIS"))
        # parameter list opsional
        if not self.match("RPARENTHESIS"):
            node["children"].append(self.parse_parameter_list())
        node["children"].append(self.expect("RPARENTHESIS"))

        return node

    # parse actual parameter list saat function/procedure call
    def parse_parameter_list(self):
        node = {"type": "<parameter-list>", "children": []}
        node["children"].append(self.parse_expression())

        # multiple parameters dipisah koma
        while self.match("COMMA"):
            node["children"].append(self.expect("COMMA"))
            node["children"].append(self.parse_expression())

        return node

    # parse expression (simple-expression dengan relational operator opsional)
    def parse_expression(self):
        node = {"type": "<expression>", "children": []}
        node["children"].append(self.parse_simple_expression())

        # relational operator opsional (=, <>, <, >, <=, >=)
        if self.match("RELATIONAL_OPERATOR"):
            node["children"].append(self.current_token)
            self.advance()
            node["children"].append(self.parse_simple_expression())

        return node

    # parse simple expression (term dengan + - atau opsional)
    def parse_simple_expression(self):
        node = {"type": "<simple-expression>", "children": []}

        # unary + atau - di depan opsional
        if self.match("ARITHMETIC_OPERATOR") and self.current_token.value in ["+", "-"]:
            node["children"].append(self.current_token)
            self.advance()

        node["children"].append(self.parse_term())

        # + - atau 'atau' bisa lebih dari satu
        while (self.match("ARITHMETIC_OPERATOR") and self.current_token.value in ["+", "-"]) or self.match("LOGICAL_OPERATOR", "atau"):
            node["children"].append(self.current_token)
            self.advance()
            node["children"].append(self.parse_term())

        return node

    # parse term (factor dengan * / bagi mod dan opsional)
    def parse_term(self):
        node = {"type": "<term>", "children": []}
        node["children"].append(self.parse_factor())

        # * / bagi mod 'dan' bisa lebih dari satu
        while (self.match("ARITHMETIC_OPERATOR") and self.current_token.value in ["*", "/"]) or self.match("ARITHMETIC_OPERATOR", "bagi") or self.match("ARITHMETIC_OPERATOR", "mod") or self.match("LOGICAL_OPERATOR", "dan"):
            node["children"].append(self.current_token)
            self.advance()
            node["children"].append(self.parse_factor())

        return node

    # parse factor (identifier, number, literal, function call, array access, parenthesis, not)
    def parse_factor(self):
        node = {"type": "<factor>", "children": []}

        if self.match("IDENTIFIER"):
            # liat next token buat bedain variable, function call, atau array access
            peek = self.peek(1)
            if peek and peek.type == "LPARENTHESIS":
                # function call
                node["children"].append(self.parse_function_call())
            elif peek and peek.type == "LBRACKET":
                # array access
                node["children"].append(self.expect("IDENTIFIER"))
                node["children"].append(self.expect("LBRACKET"))
                node["children"].append(self.parse_expression())
                node["children"].append(self.expect("RBRACKET"))
            else:
                # variable biasa
                node["children"].append(self.expect("IDENTIFIER"))
        elif self.match("NUMBER"):
            node["children"].append(self.expect("NUMBER"))
        elif self.match("CHAR_LITERAL"):
            node["children"].append(self.expect("CHAR_LITERAL"))
        elif self.match("STRING_LITERAL"):
            node["children"].append(self.expect("STRING_LITERAL"))
        elif self.match("LPARENTHESIS"):
            # parenthesized expression
            node["children"].append(self.expect("LPARENTHESIS"))
            node["children"].append(self.parse_expression())
            node["children"].append(self.expect("RPARENTHESIS"))
        elif self.match("LOGICAL_OPERATOR", "tidak"):
            # logical not
            node["children"].append(self.expect("LOGICAL_OPERATOR", "tidak"))
            node["children"].append(self.parse_factor())
        else:
            self.error(f"Unexpected token in factor: {self.current_token}")

        return node

    # parse function call dalam expression
    def parse_function_call(self):
        node = {"type": "<function-call>", "children": []}
        node["children"].append(self.expect("IDENTIFIER"))
        node["children"].append(self.expect("LPARENTHESIS"))

        # parameter list opsional
        if not self.match("RPARENTHESIS"):
            node["children"].append(self.parse_parameter_list())

        node["children"].append(self.expect("RPARENTHESIS"))
        return node
