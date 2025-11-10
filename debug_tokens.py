import sys
from src.lexer import tokenize_from_file

source_file = sys.argv[1] if len(sys.argv) > 1 else "test/milestone-2/test3.pas"
dfa_rules = "rules/dfa_rules_final.json"

tokens = tokenize_from_file(dfa_rules, source_file)

for i, (tok_type, val) in enumerate(tokens):
    print(f"{i}: {tok_type}({val})")
