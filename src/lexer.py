# lexer untuk pascal-s dengan bahasa indonesia
# baca token dari kode pascal terus convert jadi list of tuples (type, value)

import json
import sys

# keywords bahasa indonesia buat pascal-s
KEYWORDS = {
    "program", "variabel", "mulai", "selesai", "jika", "maka", "selain-itu",
    "selama", "lakukan", "untuk", "ke", "turun-ke", "integer", "real", "boolean",
    "char", "larik", "dari", "prosedur", "fungsi", "konstanta", "tipe", "string",
    "kasus", "ulangi", "sampai", "rekaman"
}
# operator logika bahasa indonesia
LOGICAL_OPERATORS = {"dan", "atau", "tidak"}
# operator aritmatika bahasa indonesia
ARITHMETIC_OPERATORS = {"bagi", "mod"}

def load_rules(json_path):
    # load DFA rules dari file json
    with open(json_path, "r") as f:
        return json.load(f)

def match(ch, pattern):
    # cek apakah karakter ch cocok sama pattern dari DFA
    # pattern bisa berupa single char, range (A..Z), atau ALL_EXCEPT
    if "ALL_EXCEPT " in pattern:
        exceptions = pattern[len("ALL_EXCEPT "):].split(", ")
        return ch not in exceptions
    if len(pattern) == 1:
        return ch == pattern
    for part in pattern.split(","):
        part = part.strip()
        if ".." in part:
            # range pattern misal A..Z
            lo, hi = part.split("..")
            if lo and hi and lo <= ch <= hi:
                return True
        elif part == ch:
            return True
    return False

def skip_comment(text, pos):
    # skip comment { } atau (* *) dan return posisi setelah comment
    n = len(text)

    # cek comment style { ... }
    if text[pos] == '{':
        start_pos = pos
        pos += 1
        while pos < n:
            if text[pos] == '}':
                return pos + 1
            pos += 1
        # kalo gak ketemu closing berarti unclosed, error!
        raise Exception(f"Unclosed comment '{{' starting at position {start_pos}")

    # cek comment style (* ... *)
    if pos + 1 < n and text[pos] == '(' and text[pos + 1] == '*':
        start_pos = pos
        pos += 2
        while pos + 1 < n:
            if text[pos] == '*' and text[pos + 1] == ')':
                return pos + 2
            pos += 1
        # unclosed comment
        raise Exception(f"Unclosed comment '(*' starting at position {start_pos}")

    # bukan comment
    return pos

def lexical_analyze(text, dfa, keywords, logical_operators, arithmetic_operators):
    # fungsi utama buat tokenizing, jalan dari kiri ke kanan pake DFA
    tokens = []
    pos = 0
    n = len(text)
    while pos < n:
        # skip whitespace
        if text[pos].isspace():
            pos += 1
            continue

        # skip comment
        if text[pos] == '{' or (pos + 1 < n and text[pos:pos+2] == '(*'):
            pos = skip_comment(text, pos)
            continue

        # mulai dari start state
        state = dfa["Start_state"]
        current_lexeme = ""
        last_accept_state = None
        last_accept_pos = pos

        # coba transisi state sampe gak bisa lagi
        while pos < n:
            ch = text[pos]
            transitioned = False
            # cari transisi yang cocok
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
            # catet posisi terakhir yang valid
            if state in dfa["Final_states"]:
                last_accept_state = state
                last_accept_pos = pos

        # error handling
        if pos == n and state in dfa.get("Error_states", {}):
            print(f"Error: invalid '{current_lexeme}' ({dfa['Error_states'][state]})")
            return tokens

        if (not last_accept_state):
            print(f"Error: Unknown symbol '{text[pos]}'")
            return tokens

        # bikin token dari lexeme yang udah dikumpulin
        if last_accept_state and state not in dfa.get("Error_states", {}):
            tok_type = dfa["Token_mapping"].get(last_accept_state, "UNKNOWN")
            val = current_lexeme
            # reklasifikasi identifier jadi keyword/operator kalo perlu
            if tok_type == "IDENTIFIER" and val.lower() in keywords:
                tok_type = "KEYWORD"
            elif tok_type == "IDENTIFIER" and val.lower() in logical_operators:
                tok_type = "LOGICAL_OPERATOR"
            elif tok_type == "IDENTIFIER" and val.lower() in arithmetic_operators:
                tok_type = "ARITHMETIC_OPERATOR"
            # edge case buat number yang diikuti .. (range operator)
            if state == "NUMBER_DOT" and pos < n and text[pos] == '.':
                tok_type = "NUMBER"
                val = current_lexeme[0:-1]
            # bedain . (dot) sama .. (range)
            if tok_type == "RANGE_OPERATOR" and val == ".":
                tok_type = "DOT"

            tokens.append((tok_type, val))
            pos = last_accept_pos
        elif state in dfa.get("Error_states", {}):
            print(f"Error: invalid '{current_lexeme}' ({dfa['Error_states'][state]})")
        else:
            pos += 1

    # merge compound keywords kayak selain-itu dan turun-ke
    tokens = merge_compound_keywords(tokens)
    return tokens

def merge_compound_keywords(tokens):
    # gabungin token yang pisah jadi compound keyword
    # misal: selain - itu -> selain-itu
    result = []
    i = 0
    while i < len(tokens):
        if i + 2 < len(tokens):
            tok1, tok2, tok3 = tokens[i], tokens[i+1], tokens[i+2]
            # cek pattern selain - itu
            if (tok1[0] == "IDENTIFIER" and tok1[1].lower() == "selain" and
                tok2[0] == "ARITHMETIC_OPERATOR" and tok2[1] == "-" and
                tok3[0] == "IDENTIFIER" and tok3[1].lower() == "itu"):
                result.append(("KEYWORD", "selain-itu"))
                i += 3
                continue
            # cek pattern turun - ke
            elif (tok1[0] == "IDENTIFIER" and tok1[1].lower() == "turun" and
                  tok2[0] == "ARITHMETIC_OPERATOR" and tok2[1] == "-" and
                  (tok3[0] == "IDENTIFIER" or tok3[0] == "KEYWORD") and tok3[1].lower() == "ke"):
                result.append(("KEYWORD", "turun-ke"))
                i += 3
                continue
        result.append(tokens[i])
        i += 1
    return result

def tokenize_from_file(dfa_path, source_path):
    # baca file pascal dan tokenize
    dfa = load_rules(dfa_path)

    # auto detect encoding (utf-16-le atau utf-8)
    with open(source_path, 'rb') as f:
        first_bytes = f.read(2)

    encoding = 'utf-16-le' if first_bytes == b'\xff\xfe' else 'utf-8'

    with open(source_path, "r", encoding=encoding) as f:
        source = f.read()
    return lexical_analyze(source, dfa, KEYWORDS, LOGICAL_OPERATORS, ARITHMETIC_OPERATORS)

def tokenize_from_text(text, dfa_path):
    dfa = load_rules(dfa_path)
    return lexical_analyze(text, dfa, KEYWORDS, LOGICAL_OPERATORS, ARITHMETIC_OPERATORS)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 lexer.py <dfa_rules.json> <source_file.pas>")
        sys.exit(1)

    dfa = load_rules(sys.argv[1])

    # auto detect encoding (utf-16-le atau utf-8)
    with open(sys.argv[2], 'rb') as f:
        first_bytes = f.read(2)

    encoding = 'utf-16-le' if first_bytes == b'\xff\xfe' else 'utf-8'

    with open(sys.argv[2], "r", encoding=encoding) as f:
        source = f.read()

    result = lexical_analyze(source, dfa, KEYWORDS, LOGICAL_OPERATORS, ARITHMETIC_OPERATORS)
    for t in result:
        print(f"{t[0]}({t[1]})")
