#!/usr/bin/env python3
"""
Script untuk menjalankan semantic analysis pada file Pascal-S
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexer import tokenize_from_file
from parser import Parser
from ast_builder import ASTBuilder
from semantic_analyzer import analyze
from ast_printer import print_ast, print_decorated_ast

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 test_semantic.py <source_file.pas>")
        sys.exit(1)
    
    source_file = sys.argv[1]
    dfa_rules = "rules/dfa_rules_final.json"
    
    print("=" * 80)
    print("SEMANTIC ANALYSIS - Pascal-S Compiler")
    print("=" * 80)
    print(f"\nSource File: {source_file}\n")
    
    try:
        # Step 1: Lexical Analysis
        print("Step 1: Lexical Analysis...")
        tokens = tokenize_from_file(dfa_rules, source_file)
        if not tokens:
            print("  ERROR: Lexical analysis failed")
            sys.exit(1)
        print(f"  ✓ Generated {len(tokens)} tokens")
        
        # Step 2: Syntax Analysis (Parsing)
        print("\nStep 2: Syntax Analysis (Parsing)...")
        parser = Parser(tokens)
        parse_tree = parser.parse()
        print("  ✓ Parse tree generated successfully")
        
        # Step 3: AST Building
        print("\nStep 3: AST Building...")
        builder = ASTBuilder()
        ast = builder.build(parse_tree)
        print(f"  ✓ AST built successfully (root: {ast.__class__.__name__})")
        
        # Step 4: Semantic Analysis
        print("\nStep 4: Semantic Analysis...")
        visitor = analyze(ast)
        
        # Print Results
        print("\n" + "=" * 80)
        print("SEMANTIC ANALYSIS RESULTS")
        print("=" * 80)
        
        if visitor.has_errors():
            print(f"\n❌ SEMANTIC ERRORS FOUND: {len(visitor.errors)} error(s)\n")
            for i, error in enumerate(visitor.errors, 1):
                location = ""
                if error.line:
                    location = f" (line {error.line}"
                    if error.column:
                        location += f", col {error.column}"
                    location += ")"
                print(f"{i}. {error.message}{location}")
        else:
            print("\n✅ NO SEMANTIC ERRORS FOUND!")
        
        if visitor.warnings:
            print(f"\n⚠️  WARNINGS: {len(visitor.warnings)} warning(s)\n")
            for i, warning in enumerate(visitor.warnings, 1):
                print(f"{i}. {warning}")
        
        # Print Symbol Table
        print("\n" + "=" * 80)
        print("SYMBOL TABLE")
        print("=" * 80)
        visitor.print_symbol_table("tab")
        
        # Print Plain AST
        print("\n" + "=" * 80)
        print("ABSTRACT SYNTAX TREE (AST)")
        print("=" * 80)
        print_ast(ast)
        
        # Print Decorated AST (optional, hanya jika tidak ada error)
        if not visitor.has_errors():
            print("\n" + "=" * 80)
            print("DECORATED AST (with semantic attributes)")
            print("=" * 80)
            print_decorated_ast(ast)
        
        # Save output
        base_name = os.path.basename(source_file)
        file_name = os.path.splitext(base_name)[0]
        
        if "milestone-3" in source_file:
            output_dir = "test/milestone-3/output"
        else:
            output_dir = os.path.dirname(source_file) or "."
        
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"output_{file_name}.txt")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("SEMANTIC ANALYSIS RESULTS - Pascal-S Compiler\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Source File: {source_file}\n")
            f.write(f"Total Tokens: {len(tokens)}\n")
            f.write(f"Analysis Date: November 29, 2025\n\n")
            
            # Error/Success Status
            f.write("=" * 80 + "\n")
            f.write("STATUS\n")
            f.write("=" * 80 + "\n")
            if visitor.has_errors():
                f.write(f"❌ SEMANTIC ERRORS: {len(visitor.errors)} error(s)\n\n")
                for i, error in enumerate(visitor.errors, 1):
                    location = ""
                    if error.line:
                        location = f" (line {error.line}"
                        if error.column:
                            location += f", col {error.column}"
                        location += ")"
                    f.write(f"{i}. {error.message}{location}\n")
            else:
                f.write("✅ NO SEMANTIC ERRORS FOUND!\n")
            
            if visitor.warnings:
                f.write(f"\n⚠️  WARNINGS: {len(visitor.warnings)} warning(s)\n\n")
                for i, warning in enumerate(visitor.warnings, 1):
                    f.write(f"{i}. {warning}\n")
            
            # Symbol Table
            f.write("\n" + "=" * 80 + "\n")
            f.write("SYMBOL TABLE\n")
            f.write("=" * 80 + "\n\n")
            
            # Redirect print output to file
            import io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            visitor.print_symbol_table("tab")
            symbol_table_output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            f.write(symbol_table_output)
            
            # Plain AST Structure
            f.write("\n" + "=" * 80 + "\n")
            f.write("ABSTRACT SYNTAX TREE (AST)\n")
            f.write("=" * 80 + "\n\n")
            
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            print_ast(ast)
            ast_output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            f.write(ast_output)
            
            # Decorated AST
            if not visitor.has_errors():
                f.write("\n" + "=" * 80 + "\n")
                f.write("DECORATED AST (with semantic attributes)\n")
                f.write("=" * 80 + "\n\n")
                
                old_stdout = sys.stdout
                sys.stdout = io.StringIO()
                print_decorated_ast(ast)
                ast_output = sys.stdout.getvalue()
                sys.stdout = old_stdout
                f.write(ast_output)
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("END OF SEMANTIC ANALYSIS\n")
            f.write("=" * 80 + "\n")
        
        print(f"\n\nOutput saved to: {output_file}")
        print("=" * 80)
        
        # Exit with error code if there are semantic errors
        sys.exit(1 if visitor.has_errors() else 0)
        
    except FileNotFoundError as e:
        print(f"\nERROR: File not found - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
