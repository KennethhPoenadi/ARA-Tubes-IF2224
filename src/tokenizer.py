import string

def load_dfa(filename):
    dfa = {}
    start_state = None
    final_states = set()

    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if line.startswith("start_state"):
                _, value = line.split("=", 1)
                start_state = value.strip()
                continue

            if line.startswith("final_state"):
                _, value = line.split("=", 1)
                final_states = {s.strip() for s in value.split(",")}
                continue

            parts = line.split()
            if len(parts) != 3:
                continue

            src, symbol, dest = parts
            symbol = symbol.encode().decode('unicode_escape')

            if symbol == 'whitespace':
                    symbol = ' '
            
            if symbol.startswith('~'):
                exclusions = symbol[1:].split(',')
                exclusions = {s.strip() for s in exclusions if s.strip()}
                
                char_set = set(string.ascii_lowercase + string.ascii_uppercase)
                
                if src not in dfa:
                    dfa[src] = {}
                for char in char_set:
                    if char not in exclusions and char not in dfa[src]:
                        # if src == 'state_12':
                        #     print(char)
                        dfa[src][char] = dest
                
                continue

            if symbol == 'num':
                char_set = set(string.digits)

                if src not in dfa:
                    dfa[src] = {}
                for char in char_set:
                    if char not in exclusions and char not in dfa[src]:
                        dfa[src][char] = dest
                
                continue
                
            if symbol == '*':
                char_set = set(string.printable)

                if src not in dfa:
                    dfa[src] = {}

                for char in char_set:
                    if char not in dfa[src]:
                        dfa[src][char] = dest

                continue

            if symbol == '*state_1':
                char_set = set(string.ascii_letters) | set(string.digits) | {'_'}

                if src not in dfa:
                    dfa[src] = {}

                for char in char_set:
                    if char not in dfa[src]:
                        dfa[src][char] = dest

                continue
                
            if src not in dfa:
                dfa[src] = {}
            dfa[src][symbol] = dest

    return dfa, start_state, final_states



def simulate_dfa(dfa, start_state, input_string, final_states):
    state = start_state
    token = ""
    tokens = []

    i = 0
    while i < len(input_string):
        ch = input_string[i]
        transitions = dfa.get(state, {})
        print(state, ch)

        if ch in transitions:
            state = transitions[ch]
            token += ch
            i += 1
        else:
            if state in final_states and token:
                if ch in (set(string.ascii_lowercase) | set(string.ascii_uppercase) | {'_'} | set(string.digits)) and input_string[i-1] in (set(string.ascii_lowercase) | set(string.ascii_uppercase) | {'_'}):
                    state = 'state_1'
                    token += ch
                    i += 1
                    continue

                tokens.append((token.strip(), state))
                print(f"Token found: '{token.strip()}' → {state}, here")
                token = ""
                state = start_state
                continue

            # if ch.isspace():
            #     if token.strip():
            #         if state in final_states:
            #             tokens.append((token.strip(), state))
            #             print(f"Token found: '{token.strip()}' → {state}")
            #         else:
            #             print(f"Ignored unfinished token: '{token.strip()}' at whitespace")
            #     token = ""
            #     state = start_state
            #     i += 1
            #     continue

            if not ch.isalnum() and ch not in ['_', '"', "'"]:
                token = token.strip()

                if (token or len(token) != 0) and state == 'state_240':
                    tokens.append((token, "number"))
                    print(f"Token found: '{token}' → number")
                else:
                    if token or len(token) != 0:
                        tokens.append((token, "identifier"))
                        print(f"Token found: '{token}' → identifier")
                
                match ch:
                    case ';': 
                        print("  ';' → semicolon") 
                        tokens.append((ch, "semicolon"))
                    case ':': 
                        if i+1 < len(input_string)-1 and input_string[i+1] == '=':
                            print("  ':=' → assignment_operator", "here")
                            tokens.append((":=", "assignment_operator"))
                            i += 1
                        else:
                            print("  ':' → colon")
                            tokens.append((ch, "colon"))
                    case ',': 
                        print("  ',' → comma")
                        tokens.append((ch, "comma"))
                    case '.':
                        print("  '.' → dot")
                        tokens.append((ch, "dot"))
                    case '(': 
                        print("  '(' → left parenthesis")
                        tokens.append((ch, "lparenthesis"))
                    case ')': 
                        print("  ')' → right parenthesis")
                        tokens.append((ch, "rparenthesis"))
                    case '{': 
                        print("  '{' → left curly brace")
                        tokens.append((ch, "comment_start"))
                    case '}': 
                        print("  '}' → right curly brace")
                        tokens.append((ch, "comment_end"))
                    case '[': 
                        print("  '[' → left square bracket")
                        tokens.append((ch, "lbracket"))
                    case ']': 
                        print("  ']' → right square bracket")
                        tokens.append((ch, "rbracket"))
                    case '>' | '<' | '=' | '<>' | '>=' | '<=':
                        print(f"  '{ch}' → relational_operator")
                        tokens.append((ch, "relational_operator"))
                    case '+' | '-' | '*' | '/' | '%':
                        print(f"  '{ch}' → arithmetic_operator")
                        tokens.append((ch, "arithmetic_operator"))



                i += 1
                token = ""
                state = start_state
                continue

            print(f"  '{ch}' → [no transition from {state}]")
            i += 1
            token = ""
            state = start_state

    # Handle final token at EOF
    if state in final_states and token:
        tokens.append((token.strip(), state))
        print(f"Token found: '{token.strip()}' → {state}")

    print("End of input")
    print()
    print("Collected tokens:")
    for token in tokens:
        print(f"{token[1].upper()}({token[0]})")
    return tokens




if __name__ == "__main__":
    dfa, start_state, final_state = load_dfa("DFA.txt")
    print("Loaded DFA transitions:")
    # for s, edges in dfa.items():
    #     print(f"{s}: {edges}")

    test_file = "../test/milestone-1/input-procedure-functions.pas"
    with open(test_file, "r") as f:
        input_str = f.read().replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')

    print(f"\nTesting input from {test_file}:")
    print(f"Input string: {repr(input_str)}")

    accepted = simulate_dfa(dfa, start_state, input_str, final_states=final_state)
    print("Accepted!" if accepted else "Rejected!")
