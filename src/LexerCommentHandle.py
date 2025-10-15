import json
import sys

KEYWORDS = {"writeln","program", "var", "begin", "end", "if", "then", "else", "while", "do", "for", "to", "downto", "integer", "real", "boolean", "char", "array", "of", "procedure", "function", "const", "type", "string"}
LOGICAL_OPERATORS = {"and", "or", "not"}
ARITHMETIC_OPERATORS = {"div", "mod"}

def load_rules(json_path):
    with open(json_path, "r") as f:
        return json.load(f)

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
                    if (state in ["NUMBER", "NUMBER_FLOAT", "S_NUMBER"]) and (s_to in ["SPACE_NUM", "SUBSTRACT"]):
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
        if pos == n and state in dfa.get("Error_states", {}):
            print(f"Error: invalid '{current_lexeme}' ({dfa['Error_states'][state]})")
            continue
        if last_accept_state and state not in dfa.get("Error_states", {}):
            tok_type = dfa["Token_mapping"].get(last_accept_state, "UNKNOWN")
            val = current_lexeme
            if tok_type == "IDENTIFIER" and val.lower() in keywords:
                tok_type = "KEYWORD"
            elif tok_type == "IDENTIFIER" and val.lower() in logical_operators:
                tok_type = "LOGICAL_OPERATOR"
            elif tok_type == "IDENTIFIER" and val.lower() in arithmetic_operators:
                tok_type = "ARITHMETIC_OPERATOR"
            if last_accept_state == "SUBSTRACT":
                tokens.append(("NUMBER", current_lexeme[0:-(pos-last_num_pos)]))
                tok_type = "ARITHMETIC_OPERATOR"
                val = current_lexeme[-1]
            if state == "NUMBER_DOT" and pos < n and text[pos] == '.':
                tok_type = "NUMBER"
                val = current_lexeme[0:-1]
            if state == "COMMENT_END_P":
                tokens.append(("COMMENT_START", current_lexeme[:2]))
                tokens.append(("COMMENT", current_lexeme[2:-2]))
                val = current_lexeme[-2:]
            if state == "COMMENT_END_B":
                tokens.append(("COMMENT_START", current_lexeme[0]))
                tokens.append(("COMMENT", current_lexeme[1:-1]))
                val = current_lexeme[-1]
            if state == "COMMENT_END_S":
                tokens.append(("COMMENT_START", current_lexeme[0:2]))
                tokens.append(("COMMENT", current_lexeme[2:-1]))
                val = "\\n"
            if state == "COMMENT_S" and pos == n:
                tokens.append(("COMMENT_START", current_lexeme[0:2]))
                tokens.append(("COMMENT", current_lexeme[2:]))
                val = ""
                tok_type = "COMMENT_END_S"
                last_accept_pos = pos
            if state == "SPACE_NUM":
                val = current_lexeme.rstrip()
            tokens.append((tok_type, val))
            pos = last_accept_pos
        elif state in dfa.get("Error_states", {}):
            print(f"Error: invalid '{current_lexeme}' ({dfa['Error_states'][state]})")
        else:
            pos += 1
    return tokens

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python LexerTokenizer.py <dfa_rules.json> <source_file.pas>")
        sys.exit(1)

    dfa = load_rules(sys.argv[1])
    with open(sys.argv[2], "r") as f:
        source = f.read()

    result = lexical_analyze(source, dfa, KEYWORDS, LOGICAL_OPERATORS, ARITHMETIC_OPERATORS)
    for t in result:
        print(f"{t[0]}({t[1]})")
