import sys
from src.lexer import tokenize_from_file
from src.parser import Parser
from src.tree_printer import print_tree

def main():
    if len(sys.argv) != 2:
        print("Usage: python compiler.py <source_file.pas>")
        sys.exit(1)

    source_file = sys.argv[1]
    dfa_rules = "rules/dfa_rules_final.json"

    try:
        tokens = tokenize_from_file(dfa_rules, source_file)

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
