from typing import List, Optional, Union, Any

# ============================================================================
# BASE NODE CLASS
# ============================================================================

class ASTNode:
    """
    Base class untuk semua AST nodes.
    
    Decoration Attributes (for Semantic Analysis):
    - tab_index: Reference to symbol table (tab) entry index
    - computed_type: DataType computed during semantic analysis
    - scope_level: Lexical scope level where this node resides
    """
    def __init__(self, line: Optional[int] = None, column: Optional[int] = None):
        self.line = line
        self.column = column
        # Decoration attributes for semantic analysis
        self.tab_index: Optional[int] = None      # Reference to tab entry
        self.computed_type: Optional[Any] = None  # DataType from symbol_table
        self.scope_level: Optional[int] = None    # Lexical level
    
    def __repr__(self):
        return f"{self.__class__.__name__}()"


# ============================================================================
# PROGRAM STRUCTURE NODES
# ============================================================================

class ProgramNode(ASTNode):
    """Node untuk program utama Pascal-S"""
    def __init__(self, name: str, declarations: 'DeclarationPartNode', 
                 body: 'CompoundStatementNode', line: Optional[int] = None):
        super().__init__(line)
        self.name = name
        self.declarations = declarations
        self.body = body
    
    def __repr__(self):
        return f"ProgramNode(name='{self.name}')"


class DeclarationPartNode(ASTNode):
    """Node untuk bagian deklarasi (konstanta, tipe, variabel, subprogram)"""
    def __init__(self, const_decls: List['ConstDeclNode'] = None,
                 type_decls: List['TypeDeclNode'] = None,
                 var_decls: List['VarDeclNode'] = None,
                 subprogram_decls: List[Union['ProcedureDeclNode', 'FunctionDeclNode']] = None,
                 line: Optional[int] = None):
        super().__init__(line)
        self.const_decls = const_decls or []
        self.type_decls = type_decls or []
        self.var_decls = var_decls or []
        self.subprogram_decls = subprogram_decls or []
    
    def __repr__(self):
        return f"DeclarationPartNode(consts={len(self.const_decls)}, types={len(self.type_decls)}, vars={len(self.var_decls)}, subprograms={len(self.subprogram_decls)})"


# ============================================================================
# DECLARATION NODES
# ============================================================================

class ConstDeclNode(ASTNode):
    """Node untuk deklarasi konstanta"""
    def __init__(self, name: str, value: Any, line: Optional[int] = None):
        super().__init__(line)
        self.name = name
        self.value = value  # bisa number, string, char, atau identifier reference
    
    def __repr__(self):
        return f"ConstDeclNode(name='{self.name}', value={self.value})"


class TypeDeclNode(ASTNode):
    """Node untuk deklarasi tipe custom"""
    def __init__(self, name: str, type_spec: 'TypeSpecNode', line: Optional[int] = None):
        super().__init__(line)
        self.name = name
        self.type_spec = type_spec
    
    def __repr__(self):
        return f"TypeDeclNode(name='{self.name}')"


class VarDeclNode(ASTNode):
    """Node untuk deklarasi variabel"""
    def __init__(self, names: List[str], type_spec: 'TypeSpecNode', line: Optional[int] = None):
        super().__init__(line)
        self.names = names  # bisa multiple variables (x, y, z: integer)
        self.type_spec = type_spec
    
    def __repr__(self):
        return f"VarDeclNode(names={self.names}, type={self.type_spec})"


class ProcedureDeclNode(ASTNode):
    """Node untuk deklarasi prosedur"""
    def __init__(self, name: str, params: List['ParamNode'] = None,
                 declarations: 'DeclarationPartNode' = None,
                 body: 'CompoundStatementNode' = None,
                 line: Optional[int] = None):
        super().__init__(line)
        self.name = name
        self.params = params or []
        self.declarations = declarations
        self.body = body
    
    def __repr__(self):
        return f"ProcedureDeclNode(name='{self.name}', params={len(self.params)})"


class FunctionDeclNode(ASTNode):
    """Node untuk deklarasi fungsi"""
    def __init__(self, name: str, params: List['ParamNode'] = None,
                 return_type: 'TypeSpecNode' = None,
                 declarations: 'DeclarationPartNode' = None,
                 body: 'CompoundStatementNode' = None,
                 line: Optional[int] = None):
        super().__init__(line)
        self.name = name
        self.params = params or []
        self.return_type = return_type
        self.declarations = declarations
        self.body = body
    
    def __repr__(self):
        return f"FunctionDeclNode(name='{self.name}', params={len(self.params)}, return_type={self.return_type})"


class ParamNode(ASTNode):
    """Node untuk parameter formal di prosedur/fungsi"""
    def __init__(self, names: List[str], type_spec: 'TypeSpecNode', line: Optional[int] = None):
        super().__init__(line)
        self.names = names
        self.type_spec = type_spec
    
    def __repr__(self):
        return f"ParamNode(names={self.names}, type={self.type_spec})"


# ============================================================================
# TYPE NODES
# ============================================================================

class TypeSpecNode(ASTNode):
    """Base class untuk type specifications"""
    pass


class PrimitiveTypeNode(TypeSpecNode):
    """Node untuk tipe primitif (integer, real, boolean, char, string)"""
    def __init__(self, type_name: str, line: Optional[int] = None):
        super().__init__(line)
        self.type_name = type_name  # 'integer', 'real', 'boolean', 'char', 'string'
    
    def __repr__(self):
        return f"PrimitiveTypeNode(type='{self.type_name}')"


class ArrayTypeNode(TypeSpecNode):
    """Node untuk tipe array"""
    def __init__(self, index_range: 'RangeNode', element_type: TypeSpecNode, line: Optional[int] = None):
        super().__init__(line)
        self.index_range = index_range
        self.element_type = element_type
    
    def __repr__(self):
        return f"ArrayTypeNode(range={self.index_range}, element_type={self.element_type})"


class CustomTypeNode(TypeSpecNode):
    """Node untuk custom type (user-defined)"""
    def __init__(self, type_name: str, line: Optional[int] = None):
        super().__init__(line)
        self.type_name = type_name
    
    def __repr__(self):
        return f"CustomTypeNode(type='{self.type_name}')"


class RangeTypeNode(TypeSpecNode):
    """Node untuk range type (misal: 1..10)"""
    def __init__(self, range_spec: 'RangeNode', line: Optional[int] = None):
        super().__init__(line)
        self.range_spec = range_spec
    
    def __repr__(self):
        return f"RangeTypeNode(range={self.range_spec})"


class RangeNode(ASTNode):
    """Node untuk range specification (start..end)"""
    def __init__(self, start: 'ExpressionNode', end: 'ExpressionNode', line: Optional[int] = None):
        super().__init__(line)
        self.start = start
        self.end = end
    
    def __repr__(self):
        return f"RangeNode(start={self.start}, end={self.end})"


# ============================================================================
# STATEMENT NODES
# ============================================================================

class StatementNode(ASTNode):
    """Base class untuk semua statement nodes"""
    pass


class CompoundStatementNode(StatementNode):
    """Node untuk compound statement (mulai...selesai)"""
    def __init__(self, statements: List[StatementNode], line: Optional[int] = None):
        super().__init__(line)
        self.statements = statements
    
    def __repr__(self):
        return f"CompoundStatementNode(statements={len(self.statements)})"


class AssignmentNode(StatementNode):
    """Node untuk assignment statement (x := expr atau arr[i] := expr)"""
    def __init__(self, target: Union['VarNode', 'ArrayAccessNode'], 
                 value: 'ExpressionNode', line: Optional[int] = None):
        super().__init__(line)
        self.target = target
        self.value = value
    
    def __repr__(self):
        return f"AssignmentNode(target={self.target})"


class IfStatementNode(StatementNode):
    """Node untuk if statement"""
    def __init__(self, condition: 'ExpressionNode', then_stmt: StatementNode,
                 else_stmt: Optional[StatementNode] = None, line: Optional[int] = None):
        super().__init__(line)
        self.condition = condition
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt
    
    def __repr__(self):
        return f"IfStatementNode(has_else={self.else_stmt is not None})"


class WhileStatementNode(StatementNode):
    """Node untuk while loop"""
    def __init__(self, condition: 'ExpressionNode', body: StatementNode, line: Optional[int] = None):
        super().__init__(line)
        self.condition = condition
        self.body = body
    
    def __repr__(self):
        return f"WhileStatementNode()"


class ForStatementNode(StatementNode):
    """Node untuk for loop"""
    def __init__(self, var_name: str, start: 'ExpressionNode', 
                 end: 'ExpressionNode', body: StatementNode,
                 is_downto: bool = False, line: Optional[int] = None):
        super().__init__(line)
        self.var_name = var_name
        self.start = start
        self.end = end
        self.body = body
        self.is_downto = is_downto  # True untuk 'turun-ke', False untuk 'ke'
    
    def __repr__(self):
        direction = "downto" if self.is_downto else "to"
        return f"ForStatementNode(var='{self.var_name}', direction='{direction}')"


class RepeatStatementNode(StatementNode):
    """Node untuk repeat-until loop"""
    def __init__(self, body: List[StatementNode], condition: 'ExpressionNode', line: Optional[int] = None):
        super().__init__(line)
        self.body = body
        self.condition = condition
    
    def __repr__(self):
        return f"RepeatStatementNode(statements={len(self.body)})"


class ProcedureCallNode(StatementNode):
    """Node untuk procedure call"""
    def __init__(self, name: str, args: List['ExpressionNode'] = None, line: Optional[int] = None):
        super().__init__(line)
        self.name = name
        self.args = args or []
    
    def __repr__(self):
        return f"ProcedureCallNode(name='{self.name}', args={len(self.args)})"


class EmptyStatementNode(StatementNode):
    """Node untuk empty statement"""
    def __repr__(self):
        return "EmptyStatementNode()"


# ============================================================================
# EXPRESSION NODES
# ============================================================================

class ExpressionNode(ASTNode):
    """Base class untuk semua expression nodes"""
    pass


class BinOpNode(ExpressionNode):
    """Node untuk binary operation (x + y, x > y, x dan y, etc)"""
    def __init__(self, operator: str, left: ExpressionNode, right: ExpressionNode, line: Optional[int] = None):
        super().__init__(line)
        self.operator = operator  # '+', '-', '*', '/', '=', '<>', '<', '>', 'dan', 'atau', dll
        self.left = left
        self.right = right
    
    def __repr__(self):
        return f"BinOpNode(op='{self.operator}')"


class UnaryOpNode(ExpressionNode):
    """Node untuk unary operation (+x, -x, tidak x)"""
    def __init__(self, operator: str, operand: ExpressionNode, line: Optional[int] = None):
        super().__init__(line)
        self.operator = operator  # '+', '-', 'tidak'
        self.operand = operand
    
    def __repr__(self):
        return f"UnaryOpNode(op='{self.operator}')"


class VarNode(ExpressionNode):
    """Node untuk variable reference"""
    def __init__(self, name: str, line: Optional[int] = None):
        super().__init__(line)
        self.name = name
    
    def __repr__(self):
        return f"VarNode(name='{self.name}')"


class ArrayAccessNode(ExpressionNode):
    """Node untuk array element access (arr[i])"""
    def __init__(self, array_name: str, index: ExpressionNode, line: Optional[int] = None):
        super().__init__(line)
        self.array_name = array_name
        self.index = index
    
    def __repr__(self):
        return f"ArrayAccessNode(array='{self.array_name}')"


class FunctionCallNode(ExpressionNode):
    """Node untuk function call dalam expression"""
    def __init__(self, name: str, args: List[ExpressionNode] = None, line: Optional[int] = None):
        super().__init__(line)
        self.name = name
        self.args = args or []
    
    def __repr__(self):
        return f"FunctionCallNode(name='{self.name}', args={len(self.args)})"


class NumberLiteralNode(ExpressionNode):
    """Node untuk number literal"""
    def __init__(self, value: Union[int, float], line: Optional[int] = None):
        super().__init__(line)
        self.value = value
    
    def __repr__(self):
        return f"NumberLiteralNode(value={self.value})"


class CharLiteralNode(ExpressionNode):
    """Node untuk char literal"""
    def __init__(self, value: str, line: Optional[int] = None):
        super().__init__(line)
        self.value = value
    
    def __repr__(self):
        return f"CharLiteralNode(value='{self.value}')"


class StringLiteralNode(ExpressionNode):
    """Node untuk string literal"""
    def __init__(self, value: str, line: Optional[int] = None):
        super().__init__(line)
        self.value = value
    
    def __repr__(self):
        return f"StringLiteralNode(value='{self.value}')"


class BooleanLiteralNode(ExpressionNode):
    """Node untuk boolean literal (true/false)"""
    def __init__(self, value: bool, line: Optional[int] = None):
        super().__init__(line)
        self.value = value
    
    def __repr__(self):
        return f"BooleanLiteralNode(value={self.value})"
