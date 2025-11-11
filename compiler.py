import sys
import os
from src.lexer import tokenize_from_file
from src.parser import Parser
from src.tree_printer import print_tree

def parse_token_file(token_file):
    tokens = []
    # Detect encoding: check for UTF-16 LE BOM (0xFF 0xFE)
    with open(token_file, 'rb') as f:
        first_bytes = f.read(2)

    encoding = 'utf-16-le' if first_bytes == b'\xff\xfe' else 'utf-8'

    with open(token_file, 'r', encoding=encoding) as f:
        for line in f:
            line = line.strip().lstrip('\ufeff')  # Remove BOM if present
            if not line:
                continue
            if '(' in line and ')' in line:
                token_type = line.split('(')[0]
                value = line.split('(')[1].rstrip(')')
                tokens.append((token_type, value))
    return tokens

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 compiler.py <source_file.pas|tokens.txt>")
        sys.exit(1)

    source_file = sys.argv[1]
    file_ext = os.path.splitext(source_file)[1]
    dfa_rules = "rules/dfa_rules_final.json"

    try:
        if file_ext == '.txt':
            tokens = parse_token_file(source_file)
        elif file_ext == '.pas':
            tokens = tokenize_from_file(dfa_rules, source_file)
        else:
            print(f"Error: Unsupported file format '{file_ext}'. Use .pas or .txt")
            sys.exit(1)

        if not tokens:
            print("Lexical analysis failed")
            sys.exit(1)

        parser = Parser(tokens)
        parse_tree = parser.parse()

        print_tree(parse_tree)

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
