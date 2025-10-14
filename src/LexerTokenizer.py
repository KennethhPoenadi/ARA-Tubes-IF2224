from curses.ascii import isdigit
import json
import string

# === JSON rules (dimasukkan langsung biar mudah) ===
'''NUMBER -> NUMBER_DOT[label = "."]
	NUMBER -> NUMBER[label="{0..9}"]
	NUMBER_DOT -> RANGE_OPERATOR[label="."]
	NUMBER_DOT -> NUMBER_FLOAT[label = "{0..9}"]
	NUMBER_FLOAT -> NUMBER_FLOAT[label="{0..9}"]
	DOT -> RANGE_OPERATOR[label = "."]
	
	
	Open_Apostrophe -> CHAR_BUILD[label="{a..z,A..Z, ALL}"]
	CHAR_BUILD -> STRING_BUILD[label="{a..z,A..Z, ALL}"]
	CHAR_BUILD -> CHAR_LITERAL[label="\'"]
	STRING_BUILD -> STRING_BUILD[label="{a..z,A..Z, ALL}"]
	STRING_BUILD -> STRING_LITERAL[label="\'"]
	STRING_LITERAL -> SUB_STRING[label="\'"]
	SUB_STRING -> STRING_BUILD[label="\'"]
	'''

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
        "LT",
        "GT",
        "EQ",
        "ARITHMETIC_OP",
        "SUBTRACT",
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
        ["START", "<", "LT"],
        ["START", ">", "GT"],
        ["START", "=", "EQ"],
        ["START", "+,/", "ARITHMETIC_OP"],
        ["START", "-", "SUBTRACT"],
        ["START", "*", "MULTIPLY"],
        ["START", "(", "LPAREN"],
        ["START", ")", "RPAREN"],
        ["START", "[", "LBRACK"],
        ["START", "]", "RBRACK"],
        ["START", "{", "COMMENT_START"],
        ["START", "}", "COMMENT_END"],

        ["LPAREN", "*", "COMMENT_START"],
        ["MULTIPLY", ")", "COMMENT_END"],
        ["SUBSTRACT", "{0..9}", "NUMBER"],

        ["LT", "=", "LEQ"],
        ["LT", ">", "NEQ"],
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

        ["DOT", ".", "RANGE_OPERATOR"],

        ["APOSTROPHE", "ALL_EXCEPT_APOSTROPHE", "CHAR_BUILD"],
        ["CHAR_BUILD", "ALL_EXCEPT_APOSTROPHE", "CHAR_BUILD"],
        ["CHAR_BUILD", "'", "CHAR_LITERAL"],
        ["CHAR_LITERAL", "'", "SUB_CHAR"],
        ["SUB_CHAR", "ALL_EXCEPT_APOSTROPHE", "STRING_BUILD"],
        ["STRING_BUILD", "ALL_EXCEPT_APOSTROPHE", "STRING_BUILD"],
        ["STRING_BUILD", "'", "STRING_LITERAL"],
        ["STRING_LITERAL", "'", "SUB_STRING"],
        ["SUB_STRING", "ALL_EXCEPT_APOSTROPHE", "STRING_BUILD"]

    ],

    "Token_mapping": {
        "IDENTIFIER": "IDENTIFIER",

        "ARITHMETIC_OP": "ARITHMETIC_OPERATOR",
        "SUBTRACT": "ARITHMETIC_OPERATOR",
        "MULTIPLY": "ARITHMETIC_OPERATOR",
        "LEQ": "RELATIONAL_OPERATOR",
        "NEQ": "RELATIONAL_OPERATOR",
        "GEQ": "RELATIONAL_OPERATOR",
        "LT": "RELATIONAL_OPERATOR",
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

KEYWORDS = {"program", "var", "begin", "end", "integer", "real", "boolean"}
LOGICAL_OPERATORS = {"and", "or", "not"}

def match(ch, pattern):
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

def lexical_analyze(text, dfa, keywords, logical_operators):
    tokens = []
    pos = 0
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
        # ======================

        if last_accept_state and state not in dfa.get("Error_states", {}):
            tok_type = dfa["Token_mapping"].get(last_accept_state, "UNKNOWN")
            val = current_lexeme

            if tok_type == "IDENTIFIER" and val.lower() in keywords:
                tok_type = "KEYWORD"
            
            if tok_type == "IDENTIFIER" and val.lower() in logical_operators:
                tok_type = "LOGICAL_OPERATOR"

            if (state == "NUMBER_DOT"):
                if (pos < n and text[pos] == '.'):
                    state = "RANGE_OPERATOR";
                    pos += 1
                elif (pos < n and isdigit(text[pos])):
                    state = "STATE_NUMBER_REAL";

            tokens.append((tok_type, val))
            pos = last_accept_pos

        elif state in dfa.get("Error_states", {}):
            msg = dfa["Error_states"][state]
            val = current_lexeme
            print(f"Error: invalid identifier '{val}' ({msg})")

        else:
            pos += 1

    return tokens



source = "_asi data_  Bangka_COM _taek _dfw_ var x; hasu_; _pr;"
result = lexical_analyze(source, dfa_rules, KEYWORDS, LOGICAL_OPERATORS)
for t in result:
    print(f"{t[0]}({t[1]})")