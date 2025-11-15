import sys
import os
from lexer import tokenize_from_file
from parser import Parser
from tree_printer import print_tree, tree_to_string

def parse_token_file(token_file):
    tokens = []
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

def get_output_path(source_file):
    # tentukan output path berdasarkan input file
    base_name = os.path.basename(source_file)
    file_name = os.path.splitext(base_name)[0]

    # kalau file di folder milestone-2/input, output ke milestone-2/output
    if "milestone-2" in source_file:
        output_dir = "test/milestone-2/output"
        os.makedirs(output_dir, exist_ok=True)
        return os.path.join(output_dir, f"output{file_name}.txt")

    # kalau bukan, output di folder yang sama dengan input
    source_dir = os.path.dirname(source_file)
    return os.path.join(source_dir, f"output{file_name}.txt")

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

        # print ke terminal
        print_tree(parse_tree, is_root=True)

        # save ke file
        output_path = get_output_path(source_file)
        tree_string = tree_to_string(parse_tree, is_root=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(tree_string)

        print(f"\nOutput saved to: {output_path}")

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
