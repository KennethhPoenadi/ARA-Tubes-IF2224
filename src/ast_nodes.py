from typing import List, Optional, Union, Any

class ASTNode:
    def __init__(self, line: Optional[int] = None, column: Optional[int] = None):
        self.line = line
        self.column = column

        self.tab_index: Optional[int] = None      
        self.computed_type: Optional[Any] = None  
        self.scope_level: Optional[int] = None    

    def __repr__(self):
        return f"{self.__class__.__name__}()"

class ProgramNode(ASTNode):

    def __init__(self, name: str, declarations: 'DeclarationPartNode', 
                 body: 'CompoundStatementNode', line: Optional[int] = None):
        super().__init__(line)
        self.name = name
        self.declarations = declarations
        self.body = body

    def __repr__(self):
        return f"ProgramNode(name='{self.name}')"

class DeclarationPartNode(ASTNode):

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

class ConstDeclNode(ASTNode):

    def __init__(self, name: str, value: Any, line: Optional[int] = None):
        super().__init__(line)
        self.name = name
        self.value = value  

    def __repr__(self):
        return f"ConstDeclNode(name='{self.name}', value={self.value})"

class TypeDeclNode(ASTNode):

    def __init__(self, name: str, type_spec: 'TypeSpecNode', line: Optional[int] = None):
        super().__init__(line)
        self.name = name
        self.type_spec = type_spec

    def __repr__(self):
        return f"TypeDeclNode(name='{self.name}')"

class VarDeclNode(ASTNode):

    def __init__(self, names: List[str], type_spec: 'TypeSpecNode', line: Optional[int] = None):
        super().__init__(line)
        self.names = names  
        self.type_spec = type_spec

    def __repr__(self):
        return f"VarDeclNode(names={self.names}, type={self.type_spec})"

class ProcedureDeclNode(ASTNode):

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

    def __init__(self, names: List[str], type_spec: 'TypeSpecNode', line: Optional[int] = None):
        super().__init__(line)
        self.names = names
        self.type_spec = type_spec

    def __repr__(self):
        return f"ParamNode(names={self.names}, type={self.type_spec})"

class TypeSpecNode(ASTNode):

    pass

class PrimitiveTypeNode(TypeSpecNode):

    def __init__(self, type_name: str, line: Optional[int] = None):
        super().__init__(line)
        self.type_name = type_name  

    def __repr__(self):
        return f"PrimitiveTypeNode(type='{self.type_name}')"

class ArrayTypeNode(TypeSpecNode):

    def __init__(self, index_range: 'RangeNode', element_type: TypeSpecNode, line: Optional[int] = None):
        super().__init__(line)
        self.index_range = index_range
        self.element_type = element_type

    def __repr__(self):
        return f"ArrayTypeNode(range={self.index_range}, element_type={self.element_type})"

class CustomTypeNode(TypeSpecNode):

    def __init__(self, type_name: str, line: Optional[int] = None):
        super().__init__(line)
        self.type_name = type_name

    def __repr__(self):
        return f"CustomTypeNode(type='{self.type_name}')"

class RangeTypeNode(TypeSpecNode):

    def __init__(self, range_spec: 'RangeNode', line: Optional[int] = None):
        super().__init__(line)
        self.range_spec = range_spec

    def __repr__(self):
        return f"RangeTypeNode(range={self.range_spec})"

class RangeNode(ASTNode):

    def __init__(self, start: 'ExpressionNode', end: 'ExpressionNode', line: Optional[int] = None):
        super().__init__(line)
        self.start = start
        self.end = end

    def __repr__(self):
        return f"RangeNode(start={self.start}, end={self.end})"

class StatementNode(ASTNode):

    pass

class CompoundStatementNode(StatementNode):

    def __init__(self, statements: List[StatementNode], line: Optional[int] = None):
        super().__init__(line)
        self.statements = statements

    def __repr__(self):
        return f"CompoundStatementNode(statements={len(self.statements)})"

class AssignmentNode(StatementNode):

    def __init__(self, target: Union['VarNode', 'ArrayAccessNode'], 
                 value: 'ExpressionNode', line: Optional[int] = None):
        super().__init__(line)
        self.target = target
        self.value = value

    def __repr__(self):
        return f"AssignmentNode(target={self.target})"

class IfStatementNode(StatementNode):

    def __init__(self, condition: 'ExpressionNode', then_stmt: StatementNode,
                 else_stmt: Optional[StatementNode] = None, line: Optional[int] = None):
        super().__init__(line)
        self.condition = condition
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

    def __repr__(self):
        return f"IfStatementNode(has_else={self.else_stmt is not None})"

class WhileStatementNode(StatementNode):

    def __init__(self, condition: 'ExpressionNode', body: StatementNode, line: Optional[int] = None):
        super().__init__(line)
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"WhileStatementNode()"

class ForStatementNode(StatementNode):

    def __init__(self, var_name: str, start: 'ExpressionNode', 
                 end: 'ExpressionNode', body: StatementNode,
                 is_downto: bool = False, line: Optional[int] = None):
        super().__init__(line)
        self.var_name = var_name
        self.start = start
        self.end = end
        self.body = body
        self.is_downto = is_downto  

    def __repr__(self):
        direction = "downto" if self.is_downto else "to"
        return f"ForStatementNode(var='{self.var_name}', direction='{direction}')"

class RepeatStatementNode(StatementNode):

    def __init__(self, body: List[StatementNode], condition: 'ExpressionNode', line: Optional[int] = None):
        super().__init__(line)
        self.body = body
        self.condition = condition

    def __repr__(self):
        return f"RepeatStatementNode(statements={len(self.body)})"

class ProcedureCallNode(StatementNode):

    def __init__(self, name: str, args: List['ExpressionNode'] = None, line: Optional[int] = None):
        super().__init__(line)
        self.name = name
        self.args = args or []

    def __repr__(self):
        return f"ProcedureCallNode(name='{self.name}', args={len(self.args)})"

class EmptyStatementNode(StatementNode):

    def __repr__(self):
        return "EmptyStatementNode()"

class ExpressionNode(ASTNode):

    pass

class BinOpNode(ExpressionNode):

    def __init__(self, operator: str, left: ExpressionNode, right: ExpressionNode, line: Optional[int] = None):
        super().__init__(line)
        self.operator = operator  
        self.left = left
        self.right = right

    def __repr__(self):
        return f"BinOpNode(op='{self.operator}')"

class UnaryOpNode(ExpressionNode):

    def __init__(self, operator: str, operand: ExpressionNode, line: Optional[int] = None):
        super().__init__(line)
        self.operator = operator  
        self.operand = operand

    def __repr__(self):
        return f"UnaryOpNode(op='{self.operator}')"

class VarNode(ExpressionNode):

    def __init__(self, name: str, line: Optional[int] = None):
        super().__init__(line)
        self.name = name

    def __repr__(self):
        return f"VarNode(name='{self.name}')"

class ArrayAccessNode(ExpressionNode):

    def __init__(self, array_name: str, index: ExpressionNode, line: Optional[int] = None):
        super().__init__(line)
        self.array_name = array_name
        self.index = index

    def __repr__(self):
        return f"ArrayAccessNode(array='{self.array_name}')"

class FunctionCallNode(ExpressionNode):

    def __init__(self, name: str, args: List[ExpressionNode] = None, line: Optional[int] = None):
        super().__init__(line)
        self.name = name
        self.args = args or []

    def __repr__(self):
        return f"FunctionCallNode(name='{self.name}', args={len(self.args)})"

class NumberLiteralNode(ExpressionNode):

    def __init__(self, value: Union[int, float], line: Optional[int] = None):
        super().__init__(line)
        self.value = value

    def __repr__(self):
        return f"NumberLiteralNode(value={self.value})"

class CharLiteralNode(ExpressionNode):

    def __init__(self, value: str, line: Optional[int] = None):
        super().__init__(line)
        self.value = value

    def __repr__(self):
        return f"CharLiteralNode(value='{self.value}')"

class StringLiteralNode(ExpressionNode):

    def __init__(self, value: str, line: Optional[int] = None):
        super().__init__(line)
        self.value = value

    def __repr__(self):
        return f"StringLiteralNode(value='{self.value}')"

class BooleanLiteralNode(ExpressionNode):

    def __init__(self, value: bool, line: Optional[int] = None):
        super().__init__(line)
        self.value = value

    def __repr__(self):
        return f"BooleanLiteralNode(value={self.value})"
