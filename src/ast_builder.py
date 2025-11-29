# ast builder/transformer untuk pascal-s compiler
# konversi parse tree (dari parser.py) jadi abstract syntax tree
#
# parse tree sangat detail dan mencakup semua token syntax
# ast lebih simpel dan fokus pada struktur semantic program

from ast_nodes import *
from typing import Dict, List, Any, Optional

class ASTBuilder:
    """
    transformer class yang konversi parse tree jadi ast
    
    cara kerja:
    1. traverse parse tree secara recursive
    2. extract informasi semantic yang penting
    3. buang detail syntax yang tidak diperlukan (semicolons, keywords, dll)
    4. return ast nodes yang terstruktur
    """
    
    def __init__(self):
        self.errors = []  # buat collect semantic errors
    
    def build(self, parse_tree: Dict) -> ProgramNode:
        """
        main entry point untuk transform parse tree ke ast
        
        args:
            parse_tree: output dari parser.parse() (dictionary structure)
        
        returns:
            programnode: root node dari ast
        """
        if parse_tree["type"] != "<program>":
            raise ValueError("Expected <program> as root node")
        
        return self.transform_program(parse_tree)
    
    # ========================================================================
    # PROGRAM STRUCTURE TRANSFORMERS
    # ========================================================================
    
    def transform_program(self, node: Dict) -> ProgramNode:
        """transform program node"""
        # <program> ::= <program-header> <declaration-part> <compound-statement> .
        children = node["children"]
        
        # Extract program name dari <program-header>
        program_header = children[0]
        program_name = self.extract_identifier(program_header["children"][1])
        
        # Transform declaration part
        declarations = self.transform_declaration_part(children[1])
        
        # Transform compound statement (body)
        body = self.transform_compound_statement(children[2])
        
        return ProgramNode(name=program_name, declarations=declarations, body=body)
    
    def transform_declaration_part(self, node: Dict) -> DeclarationPartNode:
        """Transform <declaration-part> node"""
        const_decls = []
        type_decls = []
        var_decls = []
        subprogram_decls = []
        
        for child in node.get("children", []):
            node_type = child.get("type", "")
            
            if node_type == "<const-declaration>":
                const_decls.extend(self.transform_const_declaration(child))
            elif node_type == "<type-declaration>":
                type_decls.extend(self.transform_type_declaration(child))
            elif node_type == "<var-declaration>":
                var_decls.extend(self.transform_var_declaration(child))
            elif node_type == "<procedure-declaration>":
                subprogram_decls.append(self.transform_procedure_declaration(child))
            elif node_type == "<function-declaration>":
                subprogram_decls.append(self.transform_function_declaration(child))
        
        return DeclarationPartNode(
            const_decls=const_decls,
            type_decls=type_decls,
            var_decls=var_decls,
            subprogram_decls=subprogram_decls
        )
    
    # transformers untuk deklarasi
    
    def transform_const_declaration(self, node: Dict) -> List[ConstDeclNode]:
        """transform const declaration node, bisa multiple constants"""
        # konstanta ID = VALUE ; ID = VALUE ; ...
        const_nodes = []
        children = node["children"]
        
        i = 1  # skip keyword 'konstanta'
        while i < len(children):
            name = self.extract_identifier(children[i])
            i += 2  # skip '='
            
            # Extract value (bisa number, char, string, atau identifier)
            value_token = children[i]
            if hasattr(value_token, 'type'):
                if value_token.type == "NUMBER":
                    value = self.parse_number(value_token.value)
                elif value_token.type == "CHAR_LITERAL":
                    value = value_token.value
                elif value_token.type == "STRING_LITERAL":
                    # Remove quotes from string literal
                    value = value_token.value[1:-1] if len(value_token.value) >= 2 else value_token.value
                elif value_token.type == "IDENTIFIER":
                    value = value_token.value  # reference ke const lain
                else:
                    value = value_token.value
            else:
                value = value_token
            
            const_nodes.append(ConstDeclNode(name=name, value=value))
            i += 2  # skip ';'
        
        return const_nodes
    
    def transform_type_declaration(self, node: Dict) -> List[TypeDeclNode]:
        """transform type declaration node, bisa multiple types"""
        # tipe ID = TYPE ; ID = TYPE ; ...
        type_nodes = []
        children = node["children"]
        
        i = 1  # skip keyword 'tipe'
        while i < len(children):
            name = self.extract_identifier(children[i])
            i += 2  # skip '='
            
            type_spec = self.transform_type(children[i])
            type_nodes.append(TypeDeclNode(name=name, type_spec=type_spec))
            i += 2  # skip ';'
        
        return type_nodes
    
    def transform_var_declaration(self, node: Dict) -> List[VarDeclNode]:
        """transform var declaration node, bisa multiple variable groups"""
        # variabel ID1, ID2 : TYPE ; ID3 : TYPE ; ...
        var_nodes = []
        children = node["children"]
        
        i = 1  # skip keyword 'variabel'
        while i < len(children):
            # Parse identifier list
            id_list = self.transform_identifier_list(children[i])
            i += 2  # skip ':'
            
            # Parse type
            type_spec = self.transform_type(children[i])
            var_nodes.append(VarDeclNode(names=id_list, type_spec=type_spec))
            i += 2  # skip ';'
        
        return var_nodes
    
    def transform_identifier_list(self, node: Dict) -> List[str]:
        """transform identifier list node"""
        # ID , ID , ID
        identifiers = []
        for child in node["children"]:
            if hasattr(child, 'type') and child.type == "IDENTIFIER":
                identifiers.append(child.value)
        return identifiers
    
    def transform_procedure_declaration(self, node: Dict) -> ProcedureDeclNode:
        """transform procedure declaration node"""
        # prosedur ID (params) ; <block> ;
        children = node["children"]
        
        name = self.extract_identifier(children[1])
        
        # Check if there are parameters
        params = []
        block_idx = 2
        if len(children) > 3 and isinstance(children[2], dict) and children[2].get("type") == "<formal-parameter-list>":
            params = self.transform_formal_parameter_list(children[2])
            block_idx = 3
        
        # Skip semicolon, get block
        block = children[block_idx + 1]
        declarations = self.transform_declaration_part(block["children"][0])
        body = self.transform_compound_statement(block["children"][1])
        
        return ProcedureDeclNode(name=name, params=params, declarations=declarations, body=body)
    
    def transform_function_declaration(self, node: Dict) -> FunctionDeclNode:
        """transform function declaration node"""
        # fungsi ID (params) : TYPE ; <block> ;
        children = node["children"]
        
        name = self.extract_identifier(children[1])
        
        # Check if there are parameters
        params = []
        type_idx = 2
        if len(children) > 3 and isinstance(children[2], dict) and children[2].get("type") == "<formal-parameter-list>":
            params = self.transform_formal_parameter_list(children[2])
            type_idx = 3
        
        # Skip colon, get return type
        return_type = self.transform_type(children[type_idx + 1])
        
        # Skip semicolon, get block
        block_idx = type_idx + 2
        block = children[block_idx + 1]
        declarations = self.transform_declaration_part(block["children"][0])
        body = self.transform_compound_statement(block["children"][1])
        
        return FunctionDeclNode(name=name, params=params, return_type=return_type,
                               declarations=declarations, body=body)
    
    def transform_formal_parameter_list(self, node: Dict) -> List[ParamNode]:
        """transform formal parameter list node"""
        # ( <parameter-group> ; <parameter-group> ; ... )
        params = []
        children = node["children"]
        
        for child in children:
            if isinstance(child, dict) and child.get("type") == "<parameter-group>":
                param_group = child["children"]
                # <identifier-list> : <type>
                id_list = self.transform_identifier_list(param_group[0])
                type_spec = self.transform_type(param_group[2])
                params.append(ParamNode(names=id_list, type_spec=type_spec))
        
        return params
    
    # transformers untuk tipe
    
    def transform_type(self, node: Dict) -> TypeSpecNode:
        """transform type node"""
        child = node["children"][0]
        
        if isinstance(child, dict):
            node_type = child.get("type", "")
            if node_type == "<array-type>":
                return self.transform_array_type(child)
            elif node_type == "<range>":
                return RangeTypeNode(range_spec=self.transform_range(child))
        else:
            # Token: bisa keyword (primitive type) atau identifier (custom type)
            if hasattr(child, 'type'):
                if child.type == "KEYWORD":
                    # Primitive type
                    return PrimitiveTypeNode(type_name=child.value.lower())
                elif child.type == "IDENTIFIER":
                    # Custom type
                    return CustomTypeNode(type_name=child.value)
        
        raise ValueError(f"Unknown type structure: {node}")
    
    def transform_array_type(self, node: Dict) -> ArrayTypeNode:
        """transform array type node"""
        # larik [ <range> ] dari <type>
        children = node["children"]
        # Skip 'larik' and '['
        range_node = self.transform_range(children[2])
        # Skip ']' and 'dari'
        element_type = self.transform_type(children[5])
        
        return ArrayTypeNode(index_range=range_node, element_type=element_type)
    
    def transform_range(self, node: Dict) -> RangeNode:
        """transform range node"""
        # <expression> .. <expression>
        children = node["children"]
        start = self.transform_expression(children[0])
        end = self.transform_expression(children[2])
        
        return RangeNode(start=start, end=end)
    
    # transformers untuk statement
    
    def transform_compound_statement(self, node: Dict) -> CompoundStatementNode:
        """transform compound statement node"""
        # mulai <statement-list> selesai
        statement_list = node["children"][1]
        statements = self.transform_statement_list(statement_list)
        
        return CompoundStatementNode(statements=statements)
    
    def transform_statement_list(self, node: Dict) -> List[StatementNode]:
        """transform statement list node"""
        statements = []
        
        for child in node["children"]:
            if isinstance(child, dict) and "type" in child:
                # Filter out semicolons
                if not child["type"].startswith("<"):
                    continue
                stmt = self.transform_statement(child)
                if not isinstance(stmt, EmptyStatementNode):
                    statements.append(stmt)
        
        return statements
    
    def transform_statement(self, node: Dict) -> StatementNode:
        """transform statement node (dispatcher untuk berbagai jenis statement)"""
        node_type = node.get("type", "")
        
        if node_type == "<compound-statement>":
            return self.transform_compound_statement(node)
        elif node_type == "<assignment-statement>":
            return self.transform_assignment_statement(node)
        elif node_type == "<if-statement>":
            return self.transform_if_statement(node)
        elif node_type == "<while-statement>":
            return self.transform_while_statement(node)
        elif node_type == "<for-statement>":
            return self.transform_for_statement(node)
        elif node_type == "<repeat-statement>":
            return self.transform_repeat_statement(node)
        elif node_type == "<procedure/function-call>":
            return self.transform_procedure_call(node)
        elif node_type == "<empty-statement>":
            return EmptyStatementNode()
        else:
            raise ValueError(f"Unknown statement type: {node_type}")
    
    def transform_assignment_statement(self, node: Dict) -> AssignmentNode:
        """transform assignment statement node"""
        # ID := <expression> atau ID[<expression>] := <expression>
        children = node["children"]
        
        var_name = self.extract_identifier(children[0])
        
        # Check if array access (look for LBRACKET token)
        if len(children) > 2 and hasattr(children[1], 'type') and children[1].type == "LBRACKET":
            # Array access: ID [ <expression> ] := <expression>
            index = self.transform_expression(children[2])
            target = ArrayAccessNode(array_name=var_name, index=index)
            value = self.transform_expression(children[5])  # skip ], :=
        else:
            # Simple variable: ID := <expression>
            target = VarNode(name=var_name)
            value = self.transform_expression(children[2])  # skip :=
        
        return AssignmentNode(target=target, value=value)
    
    def transform_if_statement(self, node: Dict) -> IfStatementNode:
        """transform if statement node"""
        # jika <expression> maka <statement> [selain-itu <statement>]
        children = node["children"]
        
        condition = self.transform_expression(children[1])  # skip 'jika'
        then_stmt = self.transform_statement(children[3])  # skip 'maka'
        
        # Check for else clause
        else_stmt = None
        if len(children) > 4:
            else_stmt = self.transform_statement(children[5])  # skip 'selain-itu'
        
        return IfStatementNode(condition=condition, then_stmt=then_stmt, else_stmt=else_stmt)
    
    def transform_while_statement(self, node: Dict) -> WhileStatementNode:
        """transform while statement node"""
        # selama <expression> lakukan <statement>
        children = node["children"]
        
        condition = self.transform_expression(children[1])  # skip 'selama'
        body = self.transform_statement(children[3])  # skip 'lakukan'
        
        return WhileStatementNode(condition=condition, body=body)
    
    def transform_for_statement(self, node: Dict) -> ForStatementNode:
        """transform for statement node"""
        # untuk ID := <expression> ke/turun-ke <expression> lakukan <statement>
        children = node["children"]
        
        var_name = self.extract_identifier(children[1])  # skip 'untuk'
        start = self.transform_expression(children[3])  # skip ':='
        
        # Check direction
        direction_token = children[4]
        is_downto = False
        if hasattr(direction_token, 'value') and direction_token.value == "turun-ke":
            is_downto = True
        
        end = self.transform_expression(children[5])
        body = self.transform_statement(children[7])  # skip 'lakukan'
        
        return ForStatementNode(var_name=var_name, start=start, end=end, 
                              body=body, is_downto=is_downto)
    
    def transform_repeat_statement(self, node: Dict) -> RepeatStatementNode:
        """transform repeat statement node"""
        # ulangi <statement-list> sampai <expression>
        children = node["children"]
        
        # Transform statement list
        statement_list = self.transform_statement_list(children[1])  # skip 'ulangi'
        condition = self.transform_expression(children[3])  # skip 'sampai'
        
        return RepeatStatementNode(body=statement_list, condition=condition)
    
    def transform_procedure_call(self, node: Dict) -> ProcedureCallNode:
        """transform procedure call node (as statement)"""
        # ID ( [<parameter-list>] )
        children = node["children"]
        
        name = self.extract_identifier(children[0])
        
        # Check for parameters
        args = []
        if len(children) > 2 and isinstance(children[2], dict):
            args = self.transform_parameter_list(children[2])
        
        return ProcedureCallNode(name=name, args=args)
    
    def transform_parameter_list(self, node: Dict) -> List[ExpressionNode]:
        """transform parameter list node (actual parameters)"""
        # <expression> , <expression> , ...
        params = []
        
        for child in node["children"]:
            if isinstance(child, dict) and child.get("type", "").startswith("<"):
                params.append(self.transform_expression(child))
        
        return params
    
    # transformers untuk expression
    
    def transform_expression(self, node: Dict) -> ExpressionNode:
        """transform expression node"""
        # <simple-expression> [<relational-op> <simple-expression>]
        children = node["children"]
        
        left = self.transform_simple_expression(children[0])
        
        # Check for relational operator
        if len(children) > 1:
            op_token = children[1]
            if hasattr(op_token, 'type') and op_token.type == "RELATIONAL_OPERATOR":
                right = self.transform_simple_expression(children[2])
                return BinOpNode(operator=op_token.value, left=left, right=right)
        
        return left
    
    def transform_simple_expression(self, node: Dict) -> ExpressionNode:
        """transform simple expression node"""
        # [+/-] <term> {[+/-/atau] <term>}
        children = node["children"]
        idx = 0
        
        # Check for unary sign
        result = None
        if hasattr(children[0], 'type') and children[0].type == "ARITHMETIC_OPERATOR":
            sign = children[0].value
            term = self.transform_term(children[1])
            result = UnaryOpNode(operator=sign, operand=term)
            idx = 2
        else:
            result = self.transform_term(children[0])
            idx = 1
        
        # Process additional terms with operators
        while idx < len(children):
            if hasattr(children[idx], 'type'):
                if children[idx].type == "ARITHMETIC_OPERATOR" or children[idx].type == "LOGICAL_OPERATOR":
                    operator = children[idx].value
                    right = self.transform_term(children[idx + 1])
                    result = BinOpNode(operator=operator, left=result, right=right)
                    idx += 2
                else:
                    idx += 1
            else:
                idx += 1
        
        return result
    
    def transform_term(self, node: Dict) -> ExpressionNode:
        """transform term node"""
        # <factor> {[*/ /bagi/mod/dan] <factor>}
        children = node["children"]
        
        result = self.transform_factor(children[0])
        idx = 1
        
        # Process additional factors with operators
        while idx < len(children):
            if hasattr(children[idx], 'type'):
                if children[idx].type == "ARITHMETIC_OPERATOR" or children[idx].type == "LOGICAL_OPERATOR":
                    operator = children[idx].value
                    right = self.transform_factor(children[idx + 1])
                    result = BinOpNode(operator=operator, left=result, right=right)
                    idx += 2
                else:
                    idx += 1
            else:
                idx += 1
        
        return result
    
    def transform_factor(self, node: Dict) -> ExpressionNode:
        """transform factor node"""
        children = node["children"]
        child = children[0]
        
        # Check if it's a nested structure or token
        if isinstance(child, dict):
            node_type = child.get("type", "")
            if node_type == "<function-call>":
                return self.transform_function_call(child)
            elif node_type == "<expression>":
                # Parenthesized expression: skip ( and )
                return self.transform_expression(child)
            elif node_type == "<factor>":
                # 'tidak' <factor>
                operand = self.transform_factor(child)
                return UnaryOpNode(operator="tidak", operand=operand)
        else:
            # It's a token
            if hasattr(child, 'type'):
                if child.type == "IDENTIFIER":
                    # Could be variable or array access
                    if len(children) > 1 and hasattr(children[1], 'type') and children[1].type == "LBRACKET":
                        # Array access: ID [ <expression> ]
                        index = self.transform_expression(children[2])
                        return ArrayAccessNode(array_name=child.value, index=index)
                    else:
                        return VarNode(name=child.value)
                elif child.type == "NUMBER":
                    return NumberLiteralNode(value=self.parse_number(child.value))
                elif child.type == "CHAR_LITERAL":
                    return CharLiteralNode(value=child.value)
                elif child.type == "STRING_LITERAL":
                    # Remove quotes from string literal
                    value = child.value[1:-1] if len(child.value) >= 2 else child.value
                    return StringLiteralNode(value=value)
                elif child.type == "LOGICAL_OPERATOR" and child.value == "tidak":
                    # Unary 'tidak'
                    operand = self.transform_factor(children[1])
                    return UnaryOpNode(operator="tidak", operand=operand)
                elif child.type == "LPARENTHESIS":
                    # Parenthesized expression
                    return self.transform_expression(children[1])
        
        raise ValueError(f"Unknown factor structure: {node}")
    
    def transform_function_call(self, node: Dict) -> FunctionCallNode:
        """transform function call node (in expression)"""
        # ID ( [<parameter-list>] )
        children = node["children"]
        
        name = self.extract_identifier(children[0])
        
        # Check for parameters
        args = []
        if len(children) > 2 and isinstance(children[2], dict):
            args = self.transform_parameter_list(children[2])
        
        return FunctionCallNode(name=name, args=args)
    
    # helper methods
    
    def extract_identifier(self, token) -> str:
        """extract identifier name dari token"""
        if hasattr(token, 'value'):
            return token.value
        raise ValueError(f"Expected identifier token, got: {token}")
    
    def parse_number(self, value: str) -> Union[int, float]:
        """parse number string ke int atau float"""
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            return value  # return as string kalo parsing fails
