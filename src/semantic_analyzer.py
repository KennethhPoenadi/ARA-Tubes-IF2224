#!/usr/bin/env python3
"""
Semantic Analyzer for Pascal-S Compiler

This module implements the SemanticVisitor class that traverses the AST
and performs semantic analysis including:
- Symbol table management
- Type checking
- Scope management
- Declaration verification
- Expression type inference

Compatible with ast_nodes.py and symbol_table.py
"""

from typing import Optional, List, Any, Union
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Import symbol table components
from symbol_table import (
    SymbolTable, SymbolTableEntry, ObjectType, DataType,
    data_type_from_ast
)

# Import all AST node classes
from ast_nodes import (
    ASTNode, ProgramNode, DeclarationPartNode,
    ConstDeclNode, TypeDeclNode, VarDeclNode,
    ProcedureDeclNode, FunctionDeclNode, ParamNode,
    TypeSpecNode, PrimitiveTypeNode, ArrayTypeNode, CustomTypeNode, RangeTypeNode, RangeNode,
    StatementNode, CompoundStatementNode, AssignmentNode, IfStatementNode,
    WhileStatementNode, ForStatementNode, RepeatStatementNode,
    ProcedureCallNode, EmptyStatementNode,
    ExpressionNode, BinOpNode, UnaryOpNode, VarNode, ArrayAccessNode,
    FunctionCallNode, NumberLiteralNode, CharLiteralNode,
    StringLiteralNode, BooleanLiteralNode
)


class SemanticError(Exception):
    """Exception for semantic errors during analysis"""
    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None):
        self.message = message
        self.line = line
        self.column = column
        location = ""
        if line is not None:
            location = f" at line {line}"
            if column is not None:
                location += f", column {column}"
        super().__init__(f"Semantic Error{location}: {message}")


class SemanticVisitor:
    """
    AST visitor for semantic analysis.
    
    Traverses the AST and performs:
    - Symbol table population
    - Type checking
    - Scope management
    - Semantic validation
    
    Usage:
        visitor = SemanticVisitor()
        visitor.visit(ast)
        errors = visitor.errors
        symbol_table = visitor.symbol_table
    """
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors: List[SemanticError] = []
        self.warnings: List[str] = []
        self.current_function: Optional[str] = None  # Track current function for return type checking
        self.current_function_return_type: Optional[DataType] = None
    
    def visit(self, node: ASTNode) -> Optional[DataType]:
        """
        Main visit dispatcher - routes to appropriate visit_* method.
        Returns the type of the node (for expressions) or None.
        """
        if node is None:
            return None
        
        # Get the method name based on node class
        method_name = f"visit_{node.__class__.__name__}"
        
        # Get the visitor method, defaulting to generic_visit
        visitor_method = getattr(self, method_name, self.generic_visit)
        
        return visitor_method(node)
    
    def generic_visit(self, node: ASTNode) -> None:
        """Default visitor for unhandled nodes - visits children if available"""
        # Try to visit any child nodes
        for attr_name in dir(node):
            if attr_name.startswith('_'):
                continue
            attr = getattr(node, attr_name)
            if isinstance(attr, ASTNode):
                self.visit(attr)
            elif isinstance(attr, list):
                for item in attr:
                    if isinstance(item, ASTNode):
                        self.visit(item)
    
    def add_error(self, message: str, node: Optional[ASTNode] = None):
        """Add a semantic error"""
        line = getattr(node, 'line', None) if node else None
        column = getattr(node, 'column', None) if node else None
        error = SemanticError(message, line, column)
        self.errors.append(error)
    
    def add_warning(self, message: str, node: Optional[ASTNode] = None):
        """Add a warning"""
        line = getattr(node, 'line', None) if node else None
        location = f" at line {line}" if line else ""
        self.warnings.append(f"Warning{location}: {message}")
    
    # ========================================================================
    # PROGRAM STRUCTURE VISITORS
    # ========================================================================
    
    def visit_ProgramNode(self, node: ProgramNode) -> None:
        """Visit program node - entry point for analysis"""
        # Enter program name into symbol table
        self.symbol_table.enter_program(node.name)  # Program identifier
        
        # Visit declarations
        if node.declarations:
            self.visit(node.declarations)
        
        # Visit program body
        if node.body:
            self.visit(node.body)
    
    def visit_DeclarationPartNode(self, node: DeclarationPartNode) -> None:
        """Visit declaration part - process all declarations"""
        # Process constants first (they can be used in type definitions)
        for const_decl in node.const_decls:
            self.visit(const_decl)
        
        # Process type declarations
        for type_decl in node.type_decls:
            self.visit(type_decl)
        
        # Process variable declarations
        for var_decl in node.var_decls:
            self.visit(var_decl)
        
        # Process subprogram declarations
        for subprog_decl in node.subprogram_decls:
            self.visit(subprog_decl)
    
    # ========================================================================
    # DECLARATION VISITORS
    # ========================================================================
    
    def visit_ConstDeclNode(self, node: ConstDeclNode) -> None:
        """Visit constant declaration - add to symbol table"""
        # Check for duplicate declaration
        existing = self.symbol_table.lookup_in_current_scope(node.name)
        if existing:
            self.add_error(f"Duplicate declaration of constant '{node.name}'", node)
            return
        
        # Determine type from value
        if isinstance(node.value, (int, float)):
            data_type = DataType.REAL if isinstance(node.value, float) else DataType.INTEGER
        elif isinstance(node.value, bool):
            data_type = DataType.BOOLEAN
        elif isinstance(node.value, str):
            if len(node.value) == 1:
                data_type = DataType.CHAR
            else:
                data_type = DataType.STRING
        else:
            data_type = DataType.INTEGER  # Default
        
        # Enter constant into symbol table and get index
        tab_index = self.symbol_table.enter_constant(node.name, data_type, node.value)
        
        # Decorate the AST node
        node.tab_index = tab_index
        node.computed_type = data_type
        node.scope_level = self.symbol_table.current_level
    
    def visit_TypeDeclNode(self, node: TypeDeclNode) -> None:
        """Visit type declaration - add custom type to symbol table"""
        # Check for duplicate declaration
        existing = self.symbol_table.lookup_in_current_scope(node.name)
        if existing:
            self.add_error(f"Duplicate declaration of type '{node.name}'", node)
            return
        
        # Get the data type from AST
        data_type = data_type_from_ast(node.type_spec)
        
        # Handle array types
        if isinstance(node.type_spec, ArrayTypeNode):
            array_ref = self._process_array_type(node.type_spec)
            tab_index = self.symbol_table.enter_type(node.name, DataType.ARRAY, array_ref)
        else:
            tab_index = self.symbol_table.enter_type(node.name, data_type)
        
        # Decorate the AST node
        node.tab_index = tab_index
        node.computed_type = data_type
        node.scope_level = self.symbol_table.current_level
    
    def visit_VarDeclNode(self, node: VarDeclNode) -> None:
        """Visit variable declaration - add variables to symbol table"""
        # Get the data type
        data_type = data_type_from_ast(node.type_spec)

        # Handle array types
        array_ref = -1
        if isinstance(node.type_spec, ArrayTypeNode):
            array_ref = self._process_array_type(node.type_spec)
            data_type = DataType.ARRAY
        # Handle custom type references (e.g., arr: Larik1D where Larik1D is array type)
        elif isinstance(node.type_spec, CustomTypeNode):
            # Look up the custom type in symbol table
            type_entry = self.symbol_table.lookup(node.type_spec.type_name)
            if type_entry and type_entry.obj == ObjectType.TYPE:
                data_type = type_entry.type
                array_ref = type_entry.ref  # Get array reference if it's an array type
            else:
                self.add_error(f"Unknown type '{node.type_spec.type_name}'", node)
                data_type = DataType.INTEGER  # Fallback

        # Track indices for all variables in this declaration
        tab_indices = []

        # Enter each variable name
        for var_name in node.names:
            # Check for duplicate declaration in current scope
            existing = self.symbol_table.lookup_in_current_scope(var_name)
            if existing:
                self.add_error(f"Duplicate declaration of variable '{var_name}'", node)
                tab_indices.append(-1)
                continue

            tab_index = self.symbol_table.enter_variable(var_name, data_type, array_ref)
            tab_indices.append(tab_index)

        # Decorate the AST node
        # Store ALL tab indices for each variable
        node.tab_indices = tab_indices  # List of all indices
        node.tab_index = tab_indices[0] if tab_indices else -1  # First index for compatibility
        node.computed_type = data_type
        node.scope_level = self.symbol_table.current_level
    
    def visit_ProcedureDeclNode(self, node: ProcedureDeclNode) -> None:
        """Visit procedure declaration"""
        # Check for duplicate declaration
        existing = self.symbol_table.lookup_in_current_scope(node.name)
        if existing:
            self.add_error(f"Duplicate declaration of procedure '{node.name}'", node)
            return
        
        # Enter procedure into symbol table (creates new scope)
        tab_index = self.symbol_table.enter_procedure(node.name, DataType.VOID)
        
        # Decorate the AST node
        node.tab_index = tab_index
        node.computed_type = DataType.VOID
        node.scope_level = self.symbol_table.current_level - 1  # Procedure declared in parent scope
        
        # Process parameters in the new scope
        for param in node.params:
            self.visit(param)
        
        # Process local declarations
        if node.declarations:
            self.visit(node.declarations)
        
        # Process procedure body
        if node.body:
            self.visit(node.body)
        
        # Exit procedure scope
        self.symbol_table.exit_scope()
    
    def visit_FunctionDeclNode(self, node: FunctionDeclNode) -> None:
        """Visit function declaration"""
        # Check for duplicate declaration
        existing = self.symbol_table.lookup_in_current_scope(node.name)
        if existing:
            self.add_error(f"Duplicate declaration of function '{node.name}'", node)
            return
        
        # Get return type
        return_type = data_type_from_ast(node.return_type) if node.return_type else DataType.INTEGER
        
        # Enter function into symbol table (creates new scope)
        tab_index = self.symbol_table.enter_procedure(node.name, return_type)
        
        # Decorate the AST node
        node.tab_index = tab_index
        node.computed_type = return_type
        node.scope_level = self.symbol_table.current_level - 1  # Function declared in parent scope
        
        # Track current function for return type checking
        old_function = self.current_function
        old_return_type = self.current_function_return_type
        self.current_function = node.name
        self.current_function_return_type = return_type
        
        # Process parameters
        for param in node.params:
            self.visit(param)
        
        # Process local declarations
        if node.declarations:
            self.visit(node.declarations)
        
        # Process function body
        if node.body:
            self.visit(node.body)
        
        # Restore previous function context
        self.current_function = old_function
        self.current_function_return_type = old_return_type
        
        # Exit function scope
        self.symbol_table.exit_scope()
    
    def visit_ParamNode(self, node: ParamNode) -> None:
        """Visit parameter node - add parameters to symbol table"""
        param_type = data_type_from_ast(node.type_spec)

        tab_indices = []
        for param_name in node.names:
            # Check for duplicate parameter
            existing = self.symbol_table.lookup_in_current_scope(param_name)
            if existing:
                self.add_error(f"Duplicate parameter '{param_name}'", node)
                tab_indices.append(-1)
                continue

            tab_index = self.symbol_table.enter_parameter(param_name, param_type)
            tab_indices.append(tab_index)

        # Decorate the AST node
        node.tab_indices = tab_indices  # List of all indices
        node.tab_index = tab_indices[0] if tab_indices else -1
        node.computed_type = param_type
        node.scope_level = self.symbol_table.current_level
    
    # ========================================================================
    # TYPE VISITORS
    # ========================================================================
    
    def visit_PrimitiveTypeNode(self, node: PrimitiveTypeNode) -> DataType:
        """Visit primitive type node"""
        type_map = {
            "integer": DataType.INTEGER,
            "real": DataType.REAL,
            "boolean": DataType.BOOLEAN,
            "char": DataType.CHAR,
            "string": DataType.STRING
        }
        return type_map.get(node.type_name.lower(), DataType.INTEGER)
    
    def visit_ArrayTypeNode(self, node: ArrayTypeNode) -> DataType:
        """Visit array type node"""
        return DataType.ARRAY
    
    def visit_CustomTypeNode(self, node: CustomTypeNode) -> DataType:
        """Visit custom type node - check if type exists"""
        type_entry = self.symbol_table.lookup(node.type_name)
        if not type_entry or type_entry.obj != ObjectType.TYPE:
            self.add_error(f"Unknown type '{node.type_name}'", node)
            return DataType.INTEGER  # Default fallback
        return type_entry.type
    
    def visit_RangeTypeNode(self, node: RangeTypeNode) -> DataType:
        """Visit range type node"""
        return DataType.INTEGER  # Ranges are typically integer
    
    def visit_RangeNode(self, node: RangeNode) -> DataType:
        """Visit range node"""
        # Visit start and end expressions
        start_type = self.visit(node.start)
        end_type = self.visit(node.end)
        
        # Both should be integer or compatible
        if start_type != DataType.INTEGER or end_type != DataType.INTEGER:
            self.add_warning("Range bounds should be integer expressions", node)
        
        return DataType.INTEGER
    
    # ========================================================================
    # STATEMENT VISITORS
    # ========================================================================
    
    def visit_CompoundStatementNode(self, node: CompoundStatementNode) -> None:
        """Visit compound statement (block) - just visit statements without creating new scope.
        
        Note: In Pascal, compound statements (begin..end) do NOT create new scopes.
        Only procedures and functions create new scopes. Variable declarations
        are handled at the declaration level, not within compound statements.
        """
        # Visit all statements in the block (no scope change)
        for stmt in node.statements:
            self.visit(stmt)
    
    def visit_AssignmentNode(self, node: AssignmentNode) -> None:
        """Visit assignment statement - check types match"""
        # Get target type
        target_type = self.visit(node.target)
        
        # Get value type
        value_type = self.visit(node.value)
        
        if target_type is None:
            return  # Error already reported
        
        if value_type is None:
            return  # Error already reported
        
        # Check type compatibility
        if not self._types_compatible(target_type, value_type):
            self.add_error(
                f"Type mismatch in assignment: cannot assign {value_type.value} to {target_type.value}",
                node
            )
        
        # Store the computed type in the node for later use
        node.computed_type = target_type
    
    def visit_IfStatementNode(self, node: IfStatementNode) -> None:
        """Visit if statement - check condition is boolean"""
        # Check condition type
        condition_type = self.visit(node.condition)
        if condition_type and condition_type != DataType.BOOLEAN:
            self.add_error("If condition must be a boolean expression", node)
        
        # Visit then branch
        self.visit(node.then_stmt)
        
        # Visit else branch if present
        if node.else_stmt:
            self.visit(node.else_stmt)
    
    def visit_WhileStatementNode(self, node: WhileStatementNode) -> None:
        """Visit while statement - check condition is boolean"""
        # Check condition type
        condition_type = self.visit(node.condition)
        if condition_type and condition_type != DataType.BOOLEAN:
            self.add_error("While condition must be a boolean expression", node)
        
        # Visit loop body
        self.visit(node.body)
    
    def visit_ForStatementNode(self, node: ForStatementNode) -> None:
        """Visit for statement - check loop variable and bounds"""
        # Check loop variable exists and is integer
        var_entry = self.symbol_table.lookup(node.var_name)
        if not var_entry:
            self.add_error(f"Undeclared loop variable '{node.var_name}'", node)
        elif var_entry.type != DataType.INTEGER:
            self.add_error(f"Loop variable '{node.var_name}' must be integer", node)
        
        # Check start expression is integer
        start_type = self.visit(node.start)
        if start_type and start_type != DataType.INTEGER:
            self.add_error("For loop start value must be integer", node)
        
        # Check end expression is integer
        end_type = self.visit(node.end)
        if end_type and end_type != DataType.INTEGER:
            self.add_error("For loop end value must be integer", node)
        
        # Visit loop body
        self.visit(node.body)
    
    def visit_RepeatStatementNode(self, node: RepeatStatementNode) -> None:
        """Visit repeat statement - check condition is boolean"""
        # Visit loop body (list of statements)
        for stmt in node.body:
            self.visit(stmt)
        
        # Check condition type
        condition_type = self.visit(node.condition)
        if condition_type and condition_type != DataType.BOOLEAN:
            self.add_error("Repeat-until condition must be a boolean expression", node)
    
    def visit_ProcedureCallNode(self, node: ProcedureCallNode) -> None:
        """Visit procedure call - check procedure exists and arguments match"""
        # Look up procedure
        proc_entry, tab_index = self.symbol_table.lookup_with_index(node.name)
        
        if not proc_entry:
            # Built-in procedures are handled specially (not in symbol table)
            if node.name.lower() in ['writeln', 'write', 'readln', 'read']:
                # Visit arguments but don't type check built-ins strictly
                for arg in node.args:
                    self.visit(arg)
                # Built-ins don't have symbol table entries, use special decoration
                node.tab_index = -1  # No table entry
                node.computed_type = DataType.VOID
                node.scope_level = 0  # Built-in level
                return
            else:
                self.add_error(f"Undeclared procedure '{node.name}'", node)
                return
        
        if proc_entry.obj not in [ObjectType.PROCEDURE, ObjectType.FUNCTION]:
            self.add_error(f"'{node.name}' is not a procedure", node)
            return
        
        # Visit all arguments
        for arg in node.args:
            self.visit(arg)
        
        # Decorate the AST node
        node.tab_index = tab_index
        node.computed_type = proc_entry.type
        node.scope_level = proc_entry.lev
    
    def visit_EmptyStatementNode(self, node: EmptyStatementNode) -> None:
        """Visit empty statement - nothing to do"""
        pass
    
    # ========================================================================
    # EXPRESSION VISITORS
    # ========================================================================
    
    def visit_BinOpNode(self, node: BinOpNode) -> DataType:
        """Visit binary operation - compute result type"""
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        
        if left_type is None or right_type is None:
            return None  # Error already reported
        
        # Store computed type in node
        result_type = self._compute_binop_type(node.operator, left_type, right_type, node)
        node.computed_type = result_type
        node.scope_level = self.symbol_table.current_level
        return result_type
    
    def visit_UnaryOpNode(self, node: UnaryOpNode) -> DataType:
        """Visit unary operation - compute result type"""
        operand_type = self.visit(node.operand)
        
        if operand_type is None:
            return None
        
        operator = node.operator.lower()
        
        if operator in ['+', '-']:
            # Numeric unary operators
            if operand_type not in [DataType.INTEGER, DataType.REAL]:
                self.add_error(f"Unary '{operator}' requires numeric operand", node)
                return None
            node.computed_type = operand_type
            node.scope_level = self.symbol_table.current_level
            return operand_type
        
        elif operator in ['tidak', 'not']:
            # Boolean negation
            if operand_type != DataType.BOOLEAN:
                self.add_error("'tidak' requires boolean operand", node)
                return None
            node.computed_type = DataType.BOOLEAN
            node.scope_level = self.symbol_table.current_level
            return DataType.BOOLEAN
        
        node.computed_type = operand_type
        node.scope_level = self.symbol_table.current_level
        return operand_type
    
    def visit_VarNode(self, node: VarNode) -> DataType:
        """Visit variable reference - look up in symbol table"""
        # Handle boolean literals (true, false) as special built-in constants
        if node.name.lower() in ['true', 'false']:
            node.tab_index = -1  # No symbol table entry (built-in)
            node.computed_type = DataType.BOOLEAN
            node.scope_level = 0  # Global level
            return DataType.BOOLEAN

        entry, tab_index = self.symbol_table.lookup_with_index(node.name)

        if not entry:
            self.add_error(f"Undeclared variable '{node.name}'", node)
            return None

        # Allow FUNCTION in addition to VARIABLE, PARAMETER, CONSTANT
        # This is needed for function return value assignment (e.g., functionName := result)
        if entry.obj not in [ObjectType.VARIABLE, ObjectType.PARAMETER, ObjectType.CONSTANT, ObjectType.FUNCTION]:
            self.add_error(f"'{node.name}' is not a variable", node)
            return None

        # Decorate the AST node
        node.tab_index = tab_index
        node.computed_type = entry.type
        node.scope_level = entry.lev

        return entry.type
    
    def visit_ArrayAccessNode(self, node: ArrayAccessNode) -> DataType:
        """Visit array access - check array exists and index type"""
        entry, tab_index = self.symbol_table.lookup_with_index(node.array_name)
        
        if not entry:
            self.add_error(f"Undeclared array '{node.array_name}'", node)
            return None
        
        if entry.type != DataType.ARRAY:
            self.add_error(f"'{node.array_name}' is not an array", node)
            return None
        
        # Check index type
        index_type = self.visit(node.index)
        if index_type and index_type != DataType.INTEGER:
            self.add_error("Array index must be integer", node)
        
        # Get element type from array table
        element_type = DataType.INTEGER  # Default fallback
        if entry.ref >= 0:
            array_info = self.symbol_table.get_array_info(entry.ref)
            if array_info:
                element_type = array_info.eltyp
        
        # Decorate the AST node
        node.tab_index = tab_index
        node.computed_type = element_type
        node.scope_level = entry.lev
        
        return element_type
    
    def visit_FunctionCallNode(self, node: FunctionCallNode) -> DataType:
        """Visit function call - check function exists and return type"""
        entry, tab_index = self.symbol_table.lookup_with_index(node.name)
        
        if not entry:
            self.add_error(f"Undeclared function '{node.name}'", node)
            return None
        
        if entry.obj != ObjectType.FUNCTION:
            self.add_error(f"'{node.name}' is not a function", node)
            return None
        
        # Visit all arguments
        for arg in node.args:
            self.visit(arg)
        
        # Decorate the AST node
        node.tab_index = tab_index
        node.computed_type = entry.type
        node.scope_level = entry.lev
        
        return entry.type
    
    def visit_NumberLiteralNode(self, node: NumberLiteralNode) -> DataType:
        """Visit number literal - return integer or real"""
        if isinstance(node.value, float):
            node.computed_type = DataType.REAL
        else:
            node.computed_type = DataType.INTEGER
        node.scope_level = self.symbol_table.current_level
        return node.computed_type
    
    def visit_CharLiteralNode(self, node: CharLiteralNode) -> DataType:
        """Visit char literal"""
        node.computed_type = DataType.CHAR
        node.scope_level = self.symbol_table.current_level
        return DataType.CHAR
    
    def visit_StringLiteralNode(self, node: StringLiteralNode) -> DataType:
        """Visit string literal"""
        node.computed_type = DataType.STRING
        node.scope_level = self.symbol_table.current_level
        return DataType.STRING
    
    def visit_BooleanLiteralNode(self, node: BooleanLiteralNode) -> DataType:
        """Visit boolean literal"""
        node.computed_type = DataType.BOOLEAN
        node.scope_level = self.symbol_table.current_level
        return DataType.BOOLEAN
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _process_array_type(self, array_type: ArrayTypeNode) -> int:
        """Process array type and return array table reference"""
        # Visit range to get bounds
        self.visit(array_type.index_range)
        
        # Extract bounds (simplified - would need expression evaluation for complex bounds)
        low = 1
        high = 10
        
        if isinstance(array_type.index_range.start, NumberLiteralNode):
            low = int(array_type.index_range.start.value)
        if isinstance(array_type.index_range.end, NumberLiteralNode):
            high = int(array_type.index_range.end.value)
        
        # Get element type
        element_type = data_type_from_ast(array_type.element_type)
        
        return self.symbol_table.enter_array(DataType.INTEGER, element_type, low, high)
    
    def _compute_binop_type(self, operator: str, left_type: DataType, 
                           right_type: DataType, node: ASTNode) -> Optional[DataType]:
        """Compute the result type of a binary operation"""
        op = operator.lower()
        
        # Arithmetic operators: +, -, *, /, div, mod
        if op in ['+', '-', '*']:
            if left_type in [DataType.INTEGER, DataType.REAL] and right_type in [DataType.INTEGER, DataType.REAL]:
                # If either is real, result is real
                if left_type == DataType.REAL or right_type == DataType.REAL:
                    return DataType.REAL
                return DataType.INTEGER
            # String concatenation with +
            if op == '+' and (left_type == DataType.STRING or right_type == DataType.STRING):
                return DataType.STRING
            self.add_error(f"Invalid operand types for '{operator}'", node)
            return None
        
        if op == '/':
            # Division always returns real in Pascal
            if left_type in [DataType.INTEGER, DataType.REAL] and right_type in [DataType.INTEGER, DataType.REAL]:
                return DataType.REAL
            self.add_error(f"Invalid operand types for '/'", node)
            return None
        
        if op in ['bagi', 'mod']:
            # Integer division (bagi) or modulo (mod)
            # 'bagi' is Indonesian keyword for integer division
            if left_type == DataType.INTEGER and right_type == DataType.INTEGER:
                return DataType.INTEGER
            self.add_error(f"'{op}' requires integer operands", node)
            return None
        
        # Comparison operators: =, <>, <, >, <=, >=
        if op in ['=', '<>', '<', '>', '<=', '>=']:
            if not self._types_compatible(left_type, right_type):
                self.add_error(f"Cannot compare {left_type.value} with {right_type.value}", node)
                return None
            return DataType.BOOLEAN
        
        # Logical operators: dan (and), atau (or)
        if op in ['dan', 'atau', 'and', 'or']:
            if left_type != DataType.BOOLEAN or right_type != DataType.BOOLEAN:
                self.add_error(f"'{op}' requires boolean operands", node)
                return None
            return DataType.BOOLEAN
        
        self.add_error(f"Unknown operator '{operator}'", node)
        return None
    
    def _types_compatible(self, type1: DataType, type2: DataType) -> bool:
        """Check if two types are compatible for assignment/comparison"""
        if type1 == type2:
            return True
        
        # Integer and Real are compatible (implicit conversion)
        if {type1, type2} == {DataType.INTEGER, DataType.REAL}:
            return True
        
        # Char and String are compatible
        if {type1, type2} == {DataType.CHAR, DataType.STRING}:
            return True
        
        return False
    
    def has_errors(self) -> bool:
        """Check if any errors were found during analysis"""
        return len(self.errors) > 0
    
    def print_errors(self):
        """Print all semantic errors"""
        for error in self.errors:
            print(f"ERROR: {error.message}")
    
    def print_warnings(self):
        """Print all warnings"""
        for warning in self.warnings:
            print(warning)
    
    def print_symbol_table(self, table_name: str = "all"):
        """Print the symbol table for debugging"""
        self.symbol_table.print_table(table_name)


def analyze(ast: ASTNode) -> SemanticVisitor:
    """
    Perform semantic analysis on an AST.
    
    Args:
        ast: The root node of the AST
        
    Returns:
        SemanticVisitor instance with results
    """
    visitor = SemanticVisitor()
    visitor.visit(ast)
    return visitor


# ============================================================================
# MAIN INTEGRATION EXAMPLE
# ============================================================================

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    
    from lexer import tokenize_from_text, load_rules
    from parser import Parser
    from ast_builder import ASTBuilder
    
    # Example Pascal-S code
    source_code = '''
    program SemanticTest;
    
    variabel
        x, y: integer;
        z: real;
        flag: boolean;
    
    mulai
        x := 5;
        y := 10;
        z := x + y;
        flag := x < y;
        
        jika flag maka
            writeln('x is less than y')
        selain-itu
            writeln('x is not less than y');
        
        selama x > 0 lakukan
            x := x - 1;
        
        writeln('Done!');
    selesai.
    '''
    
    print("=" * 60)
    print("SEMANTIC ANALYSIS DEMONSTRATION")
    print("=" * 60)
    print("\nSource Code:")
    print(source_code)
    
    try:
        # Step 1: Tokenize
        print("\n1. Tokenizing...")
        rules = load_rules('rules/dfa_rules_final.json')
        tokens = tokenize_from_text(source_code, 'rules/dfa_rules_final.json')
        print(f"   Generated {len(tokens)} tokens")
        
        # Step 2: Parse
        print("\n2. Parsing...")
        parser = Parser(tokens)
        parse_tree = parser.parse()
        print("   Parse tree generated")
        
        # Step 3: Build AST
        print("\n3. Building AST...")
        builder = ASTBuilder()
        ast = builder.build(parse_tree)
        print(f"   AST root: {ast}")
        
        # Step 4: Semantic Analysis
        print("\n4. Performing Semantic Analysis...")
        visitor = analyze(ast)
        
        # Print results
        if visitor.has_errors():
            print("\n=== SEMANTIC ERRORS ===")
            visitor.print_errors()
        else:
            print("\n   ✓ No semantic errors found!")
        
        if visitor.warnings:
            print("\n=== WARNINGS ===")
            visitor.print_warnings()
        
        print("\n=== SYMBOL TABLE ===")
        visitor.print_symbol_table("tab")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()