class Token:
    def __init__(self, token_type, value):
        self.type = token_type
        self.value = value

    def __repr__(self):
        return f"{self.type}({self.value})"

class Parser:
    def __init__(self, tokens):
        self.tokens = [Token(t[0], t[1]) for t in tokens]
        self.pos = 0
        self.current_token = self.tokens[0] if self.tokens else None

    def error(self, message):
        raise Exception(f"Syntax error at position {self.pos}: {message}")

    def peek(self, offset=0):
        index = self.pos + offset
        if index < len(self.tokens):
            return self.tokens[index]
        return None

    def advance(self):
        if self.pos < len(self.tokens):
            self.pos += 1
            self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None
        return self.current_token

    def expect(self, token_type, value=None):
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
        if not self.current_token:
            return False
        if self.current_token.type != token_type:
            return False
        if value and self.current_token.value.lower() != value.lower():
            return False
        return True

    def parse(self):
        return self.parse_program()

    def parse_program(self):
        node = {"type": "<program>", "children": []}
        node["children"].append(self.parse_program_header())
        node["children"].append(self.parse_declaration_part())
        node["children"].append(self.parse_compound_statement())
        node["children"].append(self.expect("DOT"))
        return node

    def parse_program_header(self):
        node = {"type": "<program-header>", "children": []}
        node["children"].append(self.expect("KEYWORD", "program"))
        node["children"].append(self.expect("IDENTIFIER"))
        node["children"].append(self.expect("SEMICOLON"))
        return node

    def parse_declaration_part(self):
        node = {"type": "<declaration-part>", "children": []}

        while self.match("KEYWORD", "konstanta"):
            node["children"].append(self.parse_const_declaration())

        while self.match("KEYWORD", "tipe"):
            node["children"].append(self.parse_type_declaration())

        while self.match("KEYWORD", "variabel"):
            node["children"].append(self.parse_var_declaration())

        while self.match("KEYWORD", "prosedur") or self.match("KEYWORD", "fungsi"):
            node["children"].append(self.parse_subprogram_declaration())

        return node

    def parse_const_declaration(self):
        node = {"type": "<const-declaration>", "children": []}
        node["children"].append(self.expect("KEYWORD", "konstanta"))

        while True:
            node["children"].append(self.expect("IDENTIFIER"))
            node["children"].append(self.expect("RELATIONAL_OPERATOR", "="))

            if self.match("NUMBER") or self.match("CHAR_LITERAL") or self.match("STRING_LITERAL"):
                node["children"].append(self.current_token)
                self.advance()
            elif self.match("IDENTIFIER"):
                node["children"].append(self.expect("IDENTIFIER"))
            else:
                self.error("Expected constant value")

            node["children"].append(self.expect("SEMICOLON"))

            if not self.match("IDENTIFIER"):
                break

        return node

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

    def parse_identifier_list(self):
        node = {"type": "<identifier-list>", "children": []}
        node["children"].append(self.expect("IDENTIFIER"))

        while self.match("COMMA"):
            node["children"].append(self.expect("COMMA"))
            node["children"].append(self.expect("IDENTIFIER"))

        return node

    def parse_type(self):
        node = {"type": "<type>", "children": []}

        if self.match("KEYWORD", "larik"):
            node["children"].append(self.parse_array_type())
        elif self.match("KEYWORD"):
            if self.current_token.value.lower() in ["integer", "real", "boolean", "char", "string"]:
                node["children"].append(self.current_token)
                self.advance()
            else:
                self.error("Expected type keyword")
        elif self.match("IDENTIFIER"):
            node["children"].append(self.expect("IDENTIFIER"))
        elif self.match("NUMBER") or self.match("CHAR_LITERAL"):
            node["children"].append(self.parse_range())
        else:
            self.error("Expected type")

        return node

    def parse_array_type(self):
        node = {"type": "<array-type>", "children": []}
        node["children"].append(self.expect("KEYWORD", "larik"))
        node["children"].append(self.expect("LBRACKET"))
        node["children"].append(self.parse_range())
        node["children"].append(self.expect("RBRACKET"))
        node["children"].append(self.expect("KEYWORD", "dari"))
        node["children"].append(self.parse_type())
        return node

    def parse_range(self):
        node = {"type": "<range>", "children": []}
        node["children"].append(self.parse_expression())
        node["children"].append(self.expect("RANGE_OPERATOR"))
        node["children"].append(self.parse_expression())
        return node

    def parse_subprogram_declaration(self):
        if self.match("KEYWORD", "prosedur"):
            return self.parse_procedure_declaration()
        elif self.match("KEYWORD", "fungsi"):
            return self.parse_function_declaration()
        else:
            self.error("Expected procedure or function")

    def parse_procedure_declaration(self):
        node = {"type": "<procedure-declaration>", "children": []}
        node["children"].append(self.expect("KEYWORD", "prosedur"))
        node["children"].append(self.expect("IDENTIFIER"))

        if self.match("LPARENTHESIS"):
            node["children"].append(self.parse_formal_parameter_list())

        node["children"].append(self.expect("SEMICOLON"))
        node["children"].append(self.parse_block())
        node["children"].append(self.expect("SEMICOLON"))
        return node

    def parse_function_declaration(self):
        node = {"type": "<function-declaration>", "children": []}
        node["children"].append(self.expect("KEYWORD", "fungsi"))
        node["children"].append(self.expect("IDENTIFIER"))

        if self.match("LPARENTHESIS"):
            node["children"].append(self.parse_formal_parameter_list())

        node["children"].append(self.expect("COLON"))
        node["children"].append(self.parse_type())
        node["children"].append(self.expect("SEMICOLON"))
        node["children"].append(self.parse_block())
        node["children"].append(self.expect("SEMICOLON"))
        return node

    def parse_formal_parameter_list(self):
        node = {"type": "<formal-parameter-list>", "children": []}
        node["children"].append(self.expect("LPARENTHESIS"))

        node["children"].append(self.parse_parameter_group())

        while self.match("SEMICOLON"):
            node["children"].append(self.expect("SEMICOLON"))
            node["children"].append(self.parse_parameter_group())

        node["children"].append(self.expect("RPARENTHESIS"))
        return node

    def parse_parameter_group(self):
        node = {"type": "<parameter-group>", "children": []}
        node["children"].append(self.parse_identifier_list())
        node["children"].append(self.expect("COLON"))
        node["children"].append(self.parse_type())
        return node

    def parse_block(self):
        node = {"type": "<block>", "children": []}
        node["children"].append(self.parse_declaration_part())
        node["children"].append(self.parse_compound_statement())
        return node

    def parse_compound_statement(self):
        node = {"type": "<compound-statement>", "children": []}
        node["children"].append(self.expect("KEYWORD", "mulai"))
        node["children"].append(self.parse_statement_list())
        node["children"].append(self.expect("KEYWORD", "selesai"))
        return node

    def parse_statement_list(self):
        node = {"type": "<statement-list>", "children": []}
        node["children"].append(self.parse_statement())

        while self.match("SEMICOLON"):
            node["children"].append(self.expect("SEMICOLON"))
            if not self.match("KEYWORD", "selesai"):
                node["children"].append(self.parse_statement())

        return node

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
            peek = self.peek(1)
            if peek and (peek.type == "ASSIGN_OPERATOR" or peek.type == "LBRACKET"):
                return self.parse_assignment_statement()
            else:
                return self.parse_procedure_call()
        elif self.match("KEYWORD") and self.current_token.value.lower() in ["writeln", "write", "readln", "read"]:
            return self.parse_procedure_call()
        else:
            return {"type": "<empty-statement>", "children": []}

    def parse_assignment_statement(self):
        node = {"type": "<assignment-statement>", "children": []}
        node["children"].append(self.expect("IDENTIFIER"))

        if self.match("LBRACKET"):
            node["children"].append(self.expect("LBRACKET"))
            node["children"].append(self.parse_expression())
            node["children"].append(self.expect("RBRACKET"))

        node["children"].append(self.expect("ASSIGN_OPERATOR"))
        node["children"].append(self.parse_expression())
        return node

    def parse_if_statement(self):
        node = {"type": "<if-statement>", "children": []}
        node["children"].append(self.expect("KEYWORD", "jika"))
        node["children"].append(self.parse_expression())
        node["children"].append(self.expect("KEYWORD", "maka"))
        node["children"].append(self.parse_statement())

        if self.match("KEYWORD", "selain-itu"):
            node["children"].append(self.expect("KEYWORD", "selain-itu"))
            node["children"].append(self.parse_statement())

        return node

    def parse_while_statement(self):
        node = {"type": "<while-statement>", "children": []}
        node["children"].append(self.expect("KEYWORD", "selama"))
        node["children"].append(self.parse_expression())
        node["children"].append(self.expect("KEYWORD", "lakukan"))
        node["children"].append(self.parse_statement())
        return node

    def parse_for_statement(self):
        node = {"type": "<for-statement>", "children": []}
        node["children"].append(self.expect("KEYWORD", "untuk"))
        node["children"].append(self.expect("IDENTIFIER"))
        node["children"].append(self.expect("ASSIGN_OPERATOR"))
        node["children"].append(self.parse_expression())

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

    def parse_repeat_statement(self):
        node = {"type": "<repeat-statement>", "children": []}
        node["children"].append(self.expect("KEYWORD", "ulangi"))
        node["children"].append(self.parse_statement_list())
        node["children"].append(self.expect("KEYWORD", "sampai"))
        node["children"].append(self.parse_expression())
        return node

    def parse_procedure_call(self):
        node = {"type": "<procedure/function-call>", "children": []}

        if self.match("KEYWORD"):
            node["children"].append(self.current_token)
            self.advance()
        else:
            node["children"].append(self.expect("IDENTIFIER"))

        if self.match("LPARENTHESIS"):
            node["children"].append(self.expect("LPARENTHESIS"))
            if not self.match("RPARENTHESIS"):
                node["children"].append(self.parse_parameter_list())
            node["children"].append(self.expect("RPARENTHESIS"))

        return node

    def parse_parameter_list(self):
        node = {"type": "<parameter-list>", "children": []}
        node["children"].append(self.parse_expression())

        while self.match("COMMA"):
            node["children"].append(self.expect("COMMA"))
            node["children"].append(self.parse_expression())

        return node

    def parse_expression(self):
        node = {"type": "<expression>", "children": []}
        node["children"].append(self.parse_simple_expression())

        if self.match("RELATIONAL_OPERATOR"):
            node["children"].append(self.current_token)
            self.advance()
            node["children"].append(self.parse_simple_expression())

        return node

    def parse_simple_expression(self):
        node = {"type": "<simple-expression>", "children": []}

        if self.match("ARITHMETIC_OPERATOR") and self.current_token.value in ["+", "-"]:
            node["children"].append(self.current_token)
            self.advance()

        node["children"].append(self.parse_term())

        while (self.match("ARITHMETIC_OPERATOR") and self.current_token.value in ["+", "-"]) or self.match("LOGICAL_OPERATOR", "atau"):
            node["children"].append(self.current_token)
            self.advance()
            node["children"].append(self.parse_term())

        return node

    def parse_term(self):
        node = {"type": "<term>", "children": []}
        node["children"].append(self.parse_factor())

        while (self.match("ARITHMETIC_OPERATOR") and self.current_token.value in ["*", "/"]) or self.match("ARITHMETIC_OPERATOR", "bagi") or self.match("ARITHMETIC_OPERATOR", "mod") or self.match("LOGICAL_OPERATOR", "dan"):
            node["children"].append(self.current_token)
            self.advance()
            node["children"].append(self.parse_factor())

        return node

    def parse_factor(self):
        node = {"type": "<factor>", "children": []}

        if self.match("IDENTIFIER"):
            peek = self.peek(1)
            if peek and peek.type == "LPARENTHESIS":
                node["children"].append(self.parse_function_call())
            elif peek and peek.type == "LBRACKET":
                node["children"].append(self.expect("IDENTIFIER"))
                node["children"].append(self.expect("LBRACKET"))
                node["children"].append(self.parse_expression())
                node["children"].append(self.expect("RBRACKET"))
            else:
                node["children"].append(self.expect("IDENTIFIER"))
        elif self.match("NUMBER"):
            node["children"].append(self.expect("NUMBER"))
        elif self.match("CHAR_LITERAL"):
            node["children"].append(self.expect("CHAR_LITERAL"))
        elif self.match("STRING_LITERAL"):
            node["children"].append(self.expect("STRING_LITERAL"))
        elif self.match("LPARENTHESIS"):
            node["children"].append(self.expect("LPARENTHESIS"))
            node["children"].append(self.parse_expression())
            node["children"].append(self.expect("RPARENTHESIS"))
        elif self.match("LOGICAL_OPERATOR", "tidak"):
            node["children"].append(self.expect("LOGICAL_OPERATOR", "tidak"))
            node["children"].append(self.parse_factor())
        else:
            self.error(f"Unexpected token in factor: {self.current_token}")

        return node

    def parse_function_call(self):
        node = {"type": "<function-call>", "children": []}
        node["children"].append(self.expect("IDENTIFIER"))
        node["children"].append(self.expect("LPARENTHESIS"))

        if not self.match("RPARENTHESIS"):
            node["children"].append(self.parse_parameter_list())

        node["children"].append(self.expect("RPARENTHESIS"))
        return node
