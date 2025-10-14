import json
import string

dfa_rules = {
    "Start_state": "START",

    "Final_states": [
        "START",
        "IDENTIFIER",
        "COLON",
        "SEMICOLON",
        "NUMBER",
        "DOT",
        "COMMA",
        "LT/LEQ/NEQ",
        "GT",
        "EQ",
        "ARITHMETIC_OP",
        "NEGATIVE",
        "SUBSTRACT",
        "MULTIPLY",
        "LPAREN",
        "RPAREN",
        "LBRACK",
        "RBRACK",
        "COMMENT_START",
        "COMMENT_END",
        "LEQ",
        "NEQ",
        "GEQ",
        "ASSIGNMENT_OP",
        "NUMBER_DOT",
        "NUMBER_FLOAT",
        "S_NUMBER",
        "RANGE_OPERATOR",
        "CHAR_LITERAL",
        "SUB_CHAR",
        "STRING_LITERAL"
    ],

    "Transitions": [
        ["START", "A..Z,a..z,_", "IDENTIFIER"],
        ["START", ":", "COLON"],
        ["START", ";", "SEMICOLON"],
        ["START", "0..9", "NUMBER"],
        ["START", ".", "DOT"],
        ["START", ",", "COMMA"],
        ["START", "'", "APOSTROPHE"],
        ["START", "<", "LT/LEQ/NEQ"],
        ["START", ">", "GT"],
        ["START", "=", "EQ"],
        ["START", "+,/", "ARITHMETIC_OP"],
        ["START", "-", "NEGATIVE"],
        ["START", "*", "MULTIPLY"],
        ["START", "(", "LPAREN"],
        ["START", ")", "RPAREN"],
        ["START", "[", "LBRACK"],
        ["START", "]", "RBRACK"],
        ["START", "{", "COMMENT_START"],
        ["START", "}", "COMMENT_END"],

        ["LPAREN", "*", "COMMENT_START"],
        ["MULTIPLY", ")", "COMMENT_END"],
        ["NEGATIVE", "0..9", "NUMBER"],

        ["LT/LEQ/NEQ", "=,>", "LT/LEQ/NEQ"],
        ["GT", "=", "GEQ"],

        ["COLON", "=", "ASSIGNMENT_OP"],
        ["IDENTIFIER", "A..Z,a..z,0..9,_", "IDENTIFIER"],

        ["NUMBER", "0..9", "NUMBER"],
        ["NUMBER", ".", "NUMBER_DOT"],
        ["NUMBER_DOT", "0..9", "NUMBER_FLOAT"],
        ["NUMBER_FLOAT", "0..9", "NUMBER_FLOAT"],

        ["NUMBER", "e,E", "NOTATION"],
        ["NUMBER_FLOAT", "e,E", "NOTATION"],
        ["NOTATION", "+,-", "NOTATION_OP"],
        ["NOTATION", "0..9", "S_NUMBER"],
        ["NOTATION_OP", "0..9", "S_NUMBER"],
        ["S_NUMBER", "0..9", "S_NUMBER"],

        ["NUMBER_DOT", "-", "SUBSTRACT"],
        ["NUMBER", "-", "SUBSTRACT"],
        ["NUMBER_FLOAT", "-", "SUBSTRACT"],
        ["S_NUMBER", "-", "SUBSTRACT"],

        ["NUMBER_DOT", " ", "SPACE_NUM"],
        ["NUMBER", " ", "SPACE_NUM"],
        ["NUMBER_FLOAT", " ", "SPACE_NUM"],
        ["S_NUMBER", " ", "SPACE_NUM"],
        ["SPACE_NUM", "-", "SUBSTRACT"],
        ["SPACE_NUM", " ", "SPACE_NUM"],

        ["DOT", ".", "RANGE_OPERATOR"],

        ["APOSTROPHE", "ALL_EXCEPT \'", "CHAR_BUILD"],
        ["CHAR_BUILD", "ALL_EXCEPT \'", "CHAR_BUILD"],
        ["CHAR_BUILD", "'", "CHAR_LITERAL"],
        ["CHAR_LITERAL", "'", "SUB_CHAR"],
        ["SUB_CHAR", "ALL_EXCEPT \'", "STRING_BUILD"],
        ["STRING_BUILD", "ALL_EXCEPT \'", "STRING_BUILD"],
        ["STRING_BUILD", "'", "STRING_LITERAL"],
        ["STRING_LITERAL", "'", "SUB_STRING"],
        ["SUB_STRING", "ALL_EXCEPT \'", "STRING_BUILD"]

    ],

    "Token_mapping": {
        "IDENTIFIER": "IDENTIFIER",

        "ARITHMETIC_OP": "ARITHMETIC_OPERATOR",
        "NEGATIVE": "ARITHMETIC_OPERATOR",
        "MULTIPLY": "ARITHMETIC_OPERATOR",
        "LEQ": "RELATIONAL_OPERATOR",
        "NEQ": "RELATIONAL_OPERATOR",
        "GEQ": "RELATIONAL_OPERATOR",
        "LT/LEQ/NEQ": "RELATIONAL_OPERATOR",
        "GT": "RELATIONAL_OPERATOR",
        "EQ": "RELATIONAL_OPERATOR",
        "ASSIGNMENT_OP": "ASSIGN_OPERATOR",
        "RANGE_OPERATOR": "RANGE_OPERATOR",

        "NUMBER": "NUMBER",
        "NUMBER_DOT": "NUMBER",
        "NUMBER_FLOAT": "NUMBER",
        "NOTATION": "NUMBER",
        "NOTATION_OP": "NUMBER",
        "S_NUMBER": "NUMBER",
        "CHAR_LITERAL": "CHAR_LITERAL",
        "STRING_LITERAL": "STRING_LITERAL",

        "SEMICOLON": "SEMICOLON",
        "COMMA": "COMMA",
        "COLON": "COLON",
        "DOT": "DOT",
        "LPAREN": "LPARENTHESIS",
        "RPAREN": "RPARENTHESIS",
        "LBRACK": "LBRACKET",
        "RBRACK": "RBRACKET",

        "COMMENT_START": "COMMENT_START",
        "COMMENT_END": "COMMENT_END"
    },

    "Error_states": {
        "STRING_BUILD": "String not closed",
        "SUB_STRING": "String not closed",
        "CHAR_BUILD": "Character not closed",
        "NOTATION": "Invalid scientific notation",
        "NOTATION_OP": "Invalid scientific notation"
    }
}

KEYWORDS = {"program", "var", "begin", "end", "if", "then", "else", "while", "do", "for", "to", "downto", "integer", "real", "boolean", "char", "array", "of", "procedure", "function", "const", "type", "string"}
LOGICAL_OPERATORS = {"and", "or", "not"}
ARITHMETIC_OPERATORS = {"div", "mod"}

def match(ch, pattern):
    if "ALL_EXCEPT " in pattern:
        exceptions = pattern[len("ALL_EXCEPT "):].split(", ")
        return ch not in exceptions

    if len(pattern) == 1:
        return ch == pattern
    
    for part in pattern.split(","):
        part = part.strip()
        if ".." in part:
            lo, hi = part.split("..")
            if lo and hi and lo <= ch <= hi:
                return True
        elif part == ch:
            return True
    return False

def lexical_analyze(text, dfa, keywords, logical_operators, arithmetic_operators):
    tokens = []
    pos = 0
    last_num_pos = 0

    n = len(text)

    while pos < n:
        if text[pos].isspace():
            pos += 1
            continue

        state = dfa["Start_state"]
        current_lexeme = ""
        last_accept_state = None
        last_accept_pos = pos

        while pos < n:
            ch = text[pos]
            transitioned = False

            for s_from, pattern, s_to in dfa["Transitions"]:
                if s_from == state and match(ch, pattern):
                    # Buat nahan kalau tiba2 ada arithmetic
                    if (state == "NUMBER" or state == "NUMBER_DOT" or state == "NUMBER_FLOAT" or state == "S_NUMBER") and (s_to == "SPACE_NUM" or s_to == "SUBSTRACT"):
                        last_num_pos = pos   

                    state = s_to
                    current_lexeme += ch
                    pos += 1
                    transitioned = True
                    break

            if not transitioned:
                break

            if state in dfa["Final_states"]:
                last_accept_state = state
                last_accept_pos = pos

    
        # JIKA STATE TERAKHIR TIDAK ADA LANJUTAN

        if pos == n and state in dfa.get("Error_states", {}):
            msg = dfa["Error_states"][state]
            val = current_lexeme
            print(f"Error: invalid identifier '{val}' ({msg})")
            continue

        if last_accept_state and state not in dfa.get("Error_states", {}):
            tok_type = dfa["Token_mapping"].get(last_accept_state, "UNKNOWN")
            val = current_lexeme

            if tok_type == "IDENTIFIER" and val.lower() in keywords:
                tok_type = "KEYWORD"
            
            if tok_type == "IDENTIFIER" and val.lower() in logical_operators:
                tok_type = "LOGICAL_OPERATOR"
            
            if tok_type == "IDENTIFIER" and val.lower() in arithmetic_operators:
                tok_type = "ARITHMETIC_OPERATOR"
            
            if (last_accept_state == "SUBSTRACT"):
                tokens.append(("NUMBER",current_lexeme[0:-(pos-last_num_pos)]))
                tok_type = "ARITHMETIC_OPERATOR"
                val = current_lexeme[-1]

            if (state == "NUMBER_DOT"):
                if (pos < n and text[pos] == '.'):
                    tok_type = "NUMBER"
                    val = current_lexeme[0:-1]
                    last_accept_pos -= 1
        
            tokens.append((tok_type, val))
            pos = last_accept_pos

        elif state in dfa.get("Error_states", {}):
            msg = dfa["Error_states"][state]
            val = current_lexeme
            print(f"Error: invalid identifier '{val}' ({msg})")

        else:
            pos += 1

    return tokens



source = """<=<<>-64.  -  45E-3 - 34 + 888.3 - (-4) 'asutenan rek''dfengsaks''nhhjhhh'

"""

result = lexical_analyze(source, dfa_rules, KEYWORDS, LOGICAL_OPERATORS, ARITHMETIC_OPERATORS)
for t in result:
    print(f"{t[0]}({t[1]})")