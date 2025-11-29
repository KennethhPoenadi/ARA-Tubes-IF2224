from ast_nodes import *
from typing import Any, List

def _get_arrow_annotation(node: ASTNode) -> str:
    parts = []
    
    if hasattr(node, 'tab_index') and node.tab_index == -1:
        if isinstance(node, ProcedureCallNode) and node.name.lower() in ['writeln', 'write', 'readln', 'read']:
            return " → predefined"
    
    if hasattr(node, 'tab_index') and node.tab_index is not None and node.tab_index >= 0:
        parts.append(f"tab_index:{node.tab_index}")
    
    if hasattr(node, 'computed_type') and node.computed_type is not None:
        type_val = node.computed_type.value if hasattr(node.computed_type, 'value') else node.computed_type
        TYPE_NAMES = {0: "void", 1: "integer", 2: "real", 3: "boolean", 4: "char", 5: "array", 6: "string"}
        if isinstance(type_val, int):
            type_str = TYPE_NAMES.get(type_val, str(type_val))
        else:
            type_str = str(type_val)
        parts.append(f"type:{type_str}")
    
    if hasattr(node, 'scope_level') and node.scope_level is not None:
        parts.append(f"lev:{node.scope_level}")
    
    if parts:
        return " → " + ", ".join(parts)
    return ""

def _get_block_annotation(node: ASTNode) -> str:
    parts = []
    if hasattr(node, 'block_index') and node.block_index is not None:
        parts.append(f"block_index:{node.block_index}")
    if hasattr(node, 'scope_level') and node.scope_level is not None:
        parts.append(f"lev:{node.scope_level}")
    if parts:
        return " → " + ", ".join(parts)
    return ""

def _get_decoration_str(node: ASTNode) -> str:
    return _get_arrow_annotation(node)

def _get_simple_node_str(node: ASTNode) -> str:
    decoration = _get_decoration_str(node)
    
    if isinstance(node, VarNode):
        return f"Var('{node.name}'{decoration})"
    elif isinstance(node, NumberLiteralNode):
        return f"Num({node.value}{decoration})"
    elif isinstance(node, StringLiteralNode):
        return f"String('{node.value}'{decoration})"
    elif isinstance(node, CharLiteralNode):
        return f"Char('{node.value}'{decoration})"
    elif isinstance(node, BooleanLiteralNode):
        return f"Bool({node.value}{decoration})"
    else:
        return None

def _format_multiline_expr(node: ASTNode, base_indent: str) -> List[str]:
    decoration = _get_decoration_str(node)
    lines = []
    
    simple = _get_simple_node_str(node)
    if simple:
        return [simple]
    
    if isinstance(node, BinOpNode):
        
        
        
        header = f"BinOp(op: '{node.operator}',"
        lines.append(header)
        
        
        padding = " " * len("BinOp(")
        
        
        left_lines = _format_multiline_expr(node.left, base_indent + padding)
        lines.append(f"{padding}left: {left_lines[0]}")
        for extra_line in left_lines[1:]:
            lines.append(f"{padding}      {extra_line}")
        
        
        lines[-1] = lines[-1] + ","
        
        
        right_lines = _format_multiline_expr(node.right, base_indent + padding)
        lines.append(f"{padding}right: {right_lines[0]}")
        for extra_line in right_lines[1:]:
            lines.append(f"{padding}       {extra_line}")
        
        
        
        if decoration:
            lines[-1] = lines[-1] + f"{decoration})"
        else:
            lines[-1] = lines[-1] + ")"
        
    elif isinstance(node, UnaryOpNode):
        header = f"UnaryOp(op: '{node.operator}',"
        lines.append(header)
        padding = " " * len("UnaryOp(")
        
        operand_lines = _format_multiline_expr(node.operand, base_indent + padding)
        lines.append(f"{padding}operand: {operand_lines[0]}")
        for extra_line in operand_lines[1:]:
            lines.append(f"{padding}         {extra_line}")
        
        if decoration:
            lines[-1] = lines[-1] + f"{decoration})"
        else:
            lines[-1] = lines[-1] + ")"
        
    elif isinstance(node, ArrayAccessNode):
        header = f"ArrayAccess('{node.array_name}',"
        lines.append(header)
        padding = " " * len("ArrayAccess(")
        
        index_lines = _format_multiline_expr(node.index, base_indent + padding)
        lines.append(f"{padding}index: {index_lines[0]}")
        for extra_line in index_lines[1:]:
            lines.append(f"{padding}       {extra_line}")
        
        if decoration:
            lines[-1] = lines[-1] + f"{decoration})"
        else:
            lines[-1] = lines[-1] + ")"
        
    elif isinstance(node, FunctionCallNode):
        if not node.args:
            lines.append(f"FunctionCall('{node.name}', []{decoration})")
        else:
            header = f"FunctionCall('{node.name}',"
            lines.append(header)
            padding = " " * len("FunctionCall(")
            
            
            args_lines = ["args: ["]
            for i, arg in enumerate(node.args):
                arg_lines = _format_multiline_expr(arg, base_indent + padding + "      ")
                if i == 0:
                    args_lines[0] += arg_lines[0]
                else:
                    args_lines.append(f"{padding}      {arg_lines[0]}")
                for extra_line in arg_lines[1:]:
                    args_lines.append(f"{padding}      {extra_line}")
                if i < len(node.args) - 1:
                    args_lines[-1] += ", "
            args_lines[-1] += f"]{decoration})"
            
            lines.append(f"{padding}{args_lines[0]}")
            for extra_line in args_lines[1:]:
                lines.append(extra_line)
    else:
        lines.append(str(node))
    
    return lines

def _is_complex_expr(node: ASTNode) -> bool:
    if isinstance(node, (BinOpNode, UnaryOpNode)):
        return True
    if isinstance(node, (FunctionCallNode, ArrayAccessNode)) and hasattr(node, 'args') and node.args:
        return any(_is_complex_expr(arg) for arg in node.args)
    if isinstance(node, ArrayAccessNode):
        return _is_complex_expr(node.index)
    return False

def _has_declarations(decl_node: DeclarationPartNode) -> bool:
    if not isinstance(decl_node, DeclarationPartNode):
        return False
    return bool(decl_node.const_decls or decl_node.type_decls or 
                decl_node.var_decls or decl_node.subprogram_decls)

def get_node_info_multiline(node: ASTNode, base_prefix: str, is_last: bool) -> List[str]:
    decoration = _get_decoration_str(node)
    
    if isinstance(node, AssignmentNode):
        
        if isinstance(node.target, ArrayAccessNode):
            target_str = f"ArrayAccess('{node.target.array_name}', index: {_get_simple_node_str(node.target.index) or str(node.target.index)})"
        else:
            target_str = _get_simple_node_str(node.target) or f"Var('{node.target.name}')"
        
        if _is_complex_expr(node.value):
            
            lines = [f"{base_prefix}Assign(target: {target_str},"]
            padding = " " * (len("Assign("))
            
            new_base_prefix = base_prefix[:-4]
            if not is_last:
                new_base_prefix = new_base_prefix + "|" + " " * 4
            value_lines = _format_multiline_expr(node.value, padding)
            lines.append(f"{new_base_prefix}{padding}value: {value_lines[0]}")

            for extra_line in value_lines[1:]:
                lines.append(f"{new_base_prefix}       {extra_line}")
            lines[-1] = lines[-1] + f"{decoration})"
            return lines
        else:
            
            value_str = _get_simple_node_str(node.value) or str(node.value)
            return [f"{base_prefix}Assign(target: {target_str}, value: {value_str}{decoration})"]
    
    
    elif isinstance(node, ProcedureCallNode):
        if not node.args:
            return [f"{base_prefix}ProcedureCall(name: '{node.name}', args: []{decoration})"]
        
        has_complex_args = any(_is_complex_expr(arg) for arg in node.args)
        
        if has_complex_args or len(node.args) > 2:
            
            lines = [f"{base_prefix}ProcedureCall(name: '{node.name}',"]
            padding = " " * (len(base_prefix) + len("ProcedureCall("))
            
            lines.append(f"{padding}args: [")
            args_padding = padding + "      "
            
            for i, arg in enumerate(node.args):
                arg_lines = _format_multiline_expr(arg, args_padding)
                suffix = ", " if i < len(node.args) - 1 else ""
                
                if len(arg_lines) == 1:
                    lines.append(f"{args_padding}{arg_lines[0]}{suffix}")
                else:
                    lines.append(f"{args_padding}{arg_lines[0]}")
                    for extra_line in arg_lines[1:]:
                        lines.append(f"{args_padding}{extra_line}")
                    lines[-1] = lines[-1] + suffix
            
            lines.append(f"{padding}]{decoration})")
            return lines
        else:
            
            return [f"{base_prefix}{node.name}(...){decoration}"]
    return [base_prefix + get_node_info(node)]

def print_ast(node: ASTNode, indent: str = "", is_last: bool = True, is_root: bool = False):
    if node is None:
        return
    
    if is_root:
        connector = ""
    else:
        connector = "\\-- " if is_last else "+-- "
    
    if not is_root:
        print(indent + "|")
    print(indent + connector + get_node_info(node))
    
    children = get_node_children(node)
    
    if children:
        if is_root:
            new_indent = "  "
        else:
            new_indent = indent + ("      " if is_last else "|     ")
        
        for i, child in enumerate(children):
            if child is not None:
                print_ast(child, new_indent, i == len(children) - 1, is_root=False)

def ast_to_string(node: ASTNode, indent: str = "", is_last: bool = True, is_root: bool = False) -> str:
    if node is None:
        return ""
    
    result = []
    
    if is_root:
        connector = ""
    else:
        connector = "\\-- " if is_last else "+-- "
    
    if not is_root:
        result.append(indent + "|")
    result.append(indent + connector + get_node_info(node))
    
    children = get_node_children(node)
    
    if children:
        if is_root:
            new_indent = "  "
        else:
            new_indent = indent + ("      " if is_last else "|     ")
        
        for i, child in enumerate(children):
            if child is not None:
                result.append(ast_to_string(child, new_indent, i == len(children) - 1, is_root=False))
    
    return "\n".join(result)

def get_node_info(node: ASTNode) -> str:
    if isinstance(node, ProgramNode):
        return f"ProgramNode(name: '{node.name}')"
    
    elif isinstance(node, DeclarationPartNode):
        return "Declarations"
    
    elif isinstance(node, ConstDeclNode):
        return f"ConstDecl(name: '{node.name}', value: {node.value})"
    
    elif isinstance(node, TypeDeclNode):
        return f"TypeDecl(name: '{node.name}')"
    
    elif isinstance(node, VarDeclNode):
        if len(node.names) == 1:
            type_str = get_type_string(node.type_spec)
            return f"VarDecl(name: '{node.names[0]}', type: '{type_str}')"
        else:
            vars_str = "', '".join(node.names)
            type_str = get_type_string(node.type_spec)
            return f"VarDecl(names: ['{vars_str}'], type: '{type_str}')"
    
    elif isinstance(node, ProcedureDeclNode):
        return f"ProcedureDecl(name: '{node.name}')"
    
    elif isinstance(node, FunctionDeclNode):
        return_type = get_type_string(node.return_type) if node.return_type else 'unknown'
        return f"FunctionDecl(name: '{node.name}', return_type: '{return_type}')"
    
    elif isinstance(node, ParamNode):
        if len(node.names) == 1:
            type_str = get_type_string(node.type_spec)
            return f"Param(name: '{node.names[0]}', type: '{type_str}')"
        else:
            params_str = "', '".join(node.names)
            type_str = get_type_string(node.type_spec)
            return f"Param(names: ['{params_str}'], type: '{type_str}')"
    
    
    elif isinstance(node, PrimitiveTypeNode):
        return ""
    
    elif isinstance(node, ArrayTypeNode):
        return "ArrayType"
    
    elif isinstance(node, CustomTypeNode):
        return f"CustomType('{node.type_name}')"
    
    elif isinstance(node, RangeTypeNode):
        return "RangeType"
    
    elif isinstance(node, RangeNode):
        return "Range"
    
    
    elif isinstance(node, CompoundStatementNode):
        return "Block"
    
    elif isinstance(node, AssignmentNode):
        target_str = get_inline_expr_str(node.target)
        value_str = get_inline_expr_str(node.value)
        return f"Assign(target: {target_str}, value: {value_str})"
    
    elif isinstance(node, IfStatementNode):
        return "If"
    
    elif isinstance(node, WhileStatementNode):
        return "While"
    
    elif isinstance(node, ForStatementNode):
        direction = "downto" if node.is_downto else "to"
        return f"For(var: '{node.var_name}', direction: '{direction}')"
    
    elif isinstance(node, RepeatStatementNode):
        return "Repeat"
    
    elif isinstance(node, ProcedureCallNode):
        args_str = ", ".join([get_inline_expr_str(arg) for arg in node.args])
        return f"ProcedureCall(name: '{node.name}', args: [{args_str}])"
    
    elif isinstance(node, EmptyStatementNode):
        return "EmptyStatement"
    
    
    elif isinstance(node, BinOpNode):
        return f"BinOp(op: '{node.operator}')"
    
    elif isinstance(node, UnaryOpNode):
        return f"UnaryOp(op: '{node.operator}')"
    
    elif isinstance(node, VarNode):
        return f"Var('{node.name}')"
    
    elif isinstance(node, ArrayAccessNode):
        return f"ArrayAccess(name: '{node.array_name}')"
    
    elif isinstance(node, FunctionCallNode):
        args_str = ", ".join([get_inline_expr_str(arg) for arg in node.args])
        return f"FunctionCall(name: '{node.name}', args: [{args_str}])"
    
    elif isinstance(node, NumberLiteralNode):
        return f"Num({node.value})"
    
    elif isinstance(node, CharLiteralNode):
        return f"Char('{node.value}')"
    
    elif isinstance(node, StringLiteralNode):
        return f"String('{node.value}')"
    
    elif isinstance(node, BooleanLiteralNode):
        return f"Bool({node.value})"
    
    else:
        return str(node)


def get_inline_expr_str(node: ASTNode) -> str:
    
    if isinstance(node, VarNode):
        return f"Var('{node.name}')"
    elif isinstance(node, NumberLiteralNode):
        return f"Num({node.value})"
    elif isinstance(node, StringLiteralNode):
        return f"String('{node.value}')"
    elif isinstance(node, CharLiteralNode):
        return f"Char('{node.value}')"
    elif isinstance(node, BooleanLiteralNode):
        return f"Bool({node.value})"
    elif isinstance(node, ArrayAccessNode):
        index_str = get_inline_expr_str(node.index)
        return f"ArrayAccess('{node.array_name}', index={index_str})"
    elif isinstance(node, FunctionCallNode):
        args_str = ", ".join([get_inline_expr_str(arg) for arg in node.args])
        return f"FunctionCall('{node.name}', [{args_str}])"
    elif isinstance(node, BinOpNode):
        left_str = get_inline_expr_str(node.left)
        right_str = get_inline_expr_str(node.right)
        return f"BinOp('{node.operator}', {left_str}, {right_str})"
    elif isinstance(node, UnaryOpNode):
        operand_str = get_inline_expr_str(node.operand)
        return f"UnaryOp('{node.operator}', {operand_str})"
    else:
        return node.__class__.__name__


def _get_value_summary(node: ASTNode) -> str:
    
    if isinstance(node, NumberLiteralNode):
        return str(node.value)
    elif isinstance(node, VarNode):
        return node.name
    elif isinstance(node, BinOpNode):
        left = _get_value_summary(node.left)
        right = _get_value_summary(node.right)
        return f"{left}{node.operator}{right}"
    elif isinstance(node, UnaryOpNode):
        return f"{node.operator}(...)"
    elif isinstance(node, FunctionCallNode):
        return f"{node.name}(...)"
    elif isinstance(node, CharLiteralNode):
        return f"'{node.value}'"
    elif isinstance(node, StringLiteralNode):
        return f"'{node.value}'"
    elif isinstance(node, BooleanLiteralNode):
        return str(node.value)
    elif isinstance(node, ArrayAccessNode):
        return f"{node.array_name}[...]"
    else:
        return "..."


def get_inline_node_str(node: ASTNode) -> str:
    
    annotation = _get_arrow_annotation(node)
    
    if isinstance(node, VarNode):
        return f"'{node.name}'{annotation}"
    elif isinstance(node, NumberLiteralNode):
        return f"{node.value}{annotation}"
    elif isinstance(node, StringLiteralNode):
        return f"'{node.value}'{annotation}"
    elif isinstance(node, CharLiteralNode):
        return f"'{node.value}'{annotation}"
    elif isinstance(node, BooleanLiteralNode):
        return f"{node.value}{annotation}"
    elif isinstance(node, ArrayAccessNode):
        index_str = get_inline_node_str(node.index)
        return f"{node.array_name}[{index_str}]{annotation}"
    elif isinstance(node, FunctionCallNode):
        return f"{node.name}(...){annotation}"
    elif isinstance(node, BinOpNode):
        left_str = get_inline_node_str(node.left)
        right_str = get_inline_node_str(node.right)
        return f"({left_str} {node.operator} {right_str}){annotation}"
    elif isinstance(node, UnaryOpNode):
        operand_str = get_inline_node_str(node.operand)
        return f"({node.operator} {operand_str}){annotation}"
    else:
        
        return node.__class__.__name__


def get_type_string(type_spec: 'TypeSpecNode') -> str:
    
    if isinstance(type_spec, PrimitiveTypeNode):
        return type_spec.type_name
    elif isinstance(type_spec, ArrayTypeNode):
        elem_type = get_type_string(type_spec.element_type)
        return f"array of {elem_type}"
    elif isinstance(type_spec, CustomTypeNode):
        return type_spec.type_name
    elif isinstance(type_spec, RangeTypeNode):
        return "range"
    else:
        return "unknown"




def print_decorated_ast(node: ASTNode, indent: str = "", is_last: bool = True, is_root: bool = False):
    """
    print decorated ast dengan format tree pake unicode characters
    termasuk semantic annotations (tab_index, type, lev)
    """
    if node is None:
        return
    
    if is_root:
        connector = ""
    else:
        connector = "└─ " if is_last else "├─ "
    
    print(indent + connector + get_decorated_node_info(node))
    
    children = get_node_children(node)
    
    if children:
        if is_root:
            new_indent = " "
        else:
            new_indent = indent + ("   " if is_last else "│  ")
        
        for i, child in enumerate(children):
            if child is not None:
                print_decorated_ast(child, new_indent, i == len(children) - 1, is_root=False)


def decorated_ast_to_string(node: ASTNode, indent: str = "", is_last: bool = True, is_root: bool = False) -> str:
    """
    convert decorated ast ke string representation
    pake unicode tree characters (├─, └─, │) dan include semantic annotations
    """
    if node is None:
        return ""
    
    result = []
    
    if is_root:
        connector = ""
    else:
        connector = "└─ " if is_last else "├─ "
    
    result.append(indent + connector + get_decorated_node_info(node))
    
    children = get_node_children(node)
    
    if children:
        if is_root:
            new_indent = " "
        else:
            new_indent = indent + ("   " if is_last else "│  ")
        
        for i, child in enumerate(children):
            if child is not None:
                result.append(decorated_ast_to_string(child, new_indent, i == len(children) - 1, is_root=False))
    
    return "\n".join(result)


def get_decorated_node_info(node: ASTNode) -> str:
    """
    get string representation dari ast node dengan semantic annotations
    format: nodetype(info) → tab_index:x, type:y, lev:z
    """
    annotation = _get_arrow_annotation(node)
    
    if isinstance(node, ProgramNode):
        return f"ProgramNode(name: '{node.name}')"
    
    elif isinstance(node, DeclarationPartNode):
        return "Declarations"
    
    elif isinstance(node, ConstDeclNode):
        return f"ConstDecl('{node.name}'){annotation}"
    
    elif isinstance(node, TypeDeclNode):
        return f"TypeDecl('{node.name}'){annotation}"
    
    elif isinstance(node, VarDeclNode):
        
        if len(node.names) == 1:
            type_str = get_type_string(node.type_spec) if hasattr(node, 'type_spec') else 'unknown'
            return f"VarDecl('{node.names[0]}', type: '{type_str}'){annotation}"
        else:
            vars_str = "', '".join(node.names)
            type_str = get_type_string(node.type_spec) if hasattr(node, 'type_spec') else 'unknown'
            return f"VarDecl(['{vars_str}'], type: '{type_str}'){annotation}"
    
    elif isinstance(node, ProcedureDeclNode):
        return f"ProcedureDecl('{node.name}'){annotation}"
    
    elif isinstance(node, FunctionDeclNode):
        return f"FunctionDecl('{node.name}'){annotation}"
    
    elif isinstance(node, ParamNode):
        if len(node.names) == 1:
            return f"Param('{node.names[0]}'){annotation}"
        else:
            params_str = "', '".join(node.names)
            return f"Param(['{params_str}']){annotation}"
    
    elif isinstance(node, PrimitiveTypeNode):
        return ""
    
    elif isinstance(node, ArrayTypeNode):
        return "ArrayType"
    
    elif isinstance(node, CustomTypeNode):
        return f"CustomType('{node.type_name}')"
    
    elif isinstance(node, RangeTypeNode):
        return "RangeType"
    
    elif isinstance(node, RangeNode):
        return "Range"
    
    elif isinstance(node, CompoundStatementNode):
        return f"Block{_get_block_annotation(node)}"
    
    elif isinstance(node, AssignmentNode):
        
        if isinstance(node.target, VarNode):
            target_name = node.target.name
        elif isinstance(node.target, ArrayAccessNode):
            
            index_str = _get_value_summary(node.target.index)
            target_name = f"{node.target.array_name}[{index_str}]"
        else:
            target_name = str(node.target)
        value_str = _get_value_summary(node.value)
        return f"Assign('{target_name}' := {value_str}){annotation}"
    
    elif isinstance(node, IfStatementNode):
        return f"If{annotation}"
    
    elif isinstance(node, WhileStatementNode):
        return f"While{annotation}"
    
    elif isinstance(node, ForStatementNode):
        direction = "downto" if node.is_downto else "to"
        return f"For('{node.var_name}' {direction}){annotation}"
    
    elif isinstance(node, RepeatStatementNode):
        return f"Repeat{annotation}"
    
    elif isinstance(node, ProcedureCallNode):
        return f"{node.name}(...){annotation}"
    
    elif isinstance(node, EmptyStatementNode):
        return "EmptyStatement"
    
    elif isinstance(node, BinOpNode):
        return f"BinOp '{node.operator}'{annotation}"
    
    elif isinstance(node, UnaryOpNode):
        return f"UnaryOp '{node.operator}'{annotation}"
    
    elif isinstance(node, VarNode):
        return f"'{node.name}'{annotation}"
    
    elif isinstance(node, ArrayAccessNode):
        return f"'{node.array_name}[...]'{annotation}"
    
    elif isinstance(node, FunctionCallNode):
        return f"{node.name}(...){annotation}"
    
    elif isinstance(node, NumberLiteralNode):
        return f"{node.value}{annotation}"
    
    elif isinstance(node, CharLiteralNode):
        return f"'{node.value}'{annotation}"
    
    elif isinstance(node, StringLiteralNode):
        return f"'{node.value}'{annotation}"
    
    elif isinstance(node, BooleanLiteralNode):
        return f"{node.value}{annotation}"
    
    else:
        return str(node)

def get_node_children(node: ASTNode) -> list:
    """
    dapatkan list of children dari ast node
    return list berisi child nodes untuk traversal
    """
    children = []
    
    if isinstance(node, ProgramNode):
        children.append(node.declarations)
        children.append(node.body)
    
    elif isinstance(node, DeclarationPartNode):
        children.extend(node.const_decls)
        children.extend(node.type_decls)
        
        for var_decl in node.var_decls:
            for i, name in enumerate(var_decl.names):
                
                new_node = VarDeclNode(names=[name], type_spec=var_decl.type_spec)
                
                if hasattr(var_decl, 'tab_indices') and i < len(var_decl.tab_indices):
                    new_node.tab_index = var_decl.tab_indices[i]
                elif hasattr(var_decl, 'tab_index'):
                    new_node.tab_index = var_decl.tab_index
                if hasattr(var_decl, 'computed_type'):
                    new_node.computed_type = var_decl.computed_type
                if hasattr(var_decl, 'scope_level'):
                    new_node.scope_level = var_decl.scope_level
                children.append(new_node)
        children.extend(node.subprogram_decls)
    
    elif isinstance(node, TypeDeclNode):
        
        if node.type_spec and not isinstance(node.type_spec, str):
            children.append(node.type_spec)
    
    elif isinstance(node, VarDeclNode):
        
        pass
    
    elif isinstance(node, ProcedureDeclNode):
        children.extend(node.params)
        
        if node.declarations and _has_declarations(node.declarations):
            children.append(node.declarations)
        if node.body:
            children.append(node.body)
    
    elif isinstance(node, FunctionDeclNode):
        children.extend(node.params)
        
        
        if node.declarations and _has_declarations(node.declarations):
            children.append(node.declarations)
        if node.body:
            children.append(node.body)
    
    elif isinstance(node, ParamNode):
        
        pass
    
    elif isinstance(node, ArrayTypeNode):
        children.append(node.index_range)
        children.append(node.element_type)
    
    elif isinstance(node, RangeTypeNode):
        children.append(node.range_spec)
    
    elif isinstance(node, RangeNode):
        children.append(node.start)
        children.append(node.end)
    
    elif isinstance(node, CompoundStatementNode):
        children.extend(node.statements)
    
    elif isinstance(node, AssignmentNode):
        
        pass
    
    elif isinstance(node, IfStatementNode):
        children.append(node.condition)
        children.append(node.then_stmt)
        if node.else_stmt:
            children.append(node.else_stmt)
    
    elif isinstance(node, WhileStatementNode):
        children.append(node.condition)
        children.append(node.body)
    
    elif isinstance(node, ForStatementNode):
        children.append(node.start)
        children.append(node.end)
        children.append(node.body)
    
    elif isinstance(node, RepeatStatementNode):
        children.extend(node.body)
        children.append(node.condition)
    
    elif isinstance(node, ProcedureCallNode):
        
        pass
    
    elif isinstance(node, BinOpNode):
        children.append(node.left)
        children.append(node.right)
    
    elif isinstance(node, UnaryOpNode):
        children.append(node.operand)
    
    elif isinstance(node, ArrayAccessNode):
        children.append(node.index)
    
    elif isinstance(node, FunctionCallNode):
        
        pass
    
    
    
    return children


def print_ast_compact(node: ASTNode, indent: int = 0):
    """
    print ast dalam format compact (lebih simple, tanpa ascii art)
    berguna untuk debugging cepat
    """
    if node is None:
        return
    
    indent_str = "  " * indent
    if get_node_info(node) == "a": 
        print(f"{indent_str}{get_node_info(node)}")
    
    children = get_node_children(node)
    for child in children:
        if child is not None:
            print_ast_compact(child, indent + 1)






if __name__ == "__main__":
    import os
    import sys
    
    
    from lexer import tokenize_from_text
    from parser import Parser
    from ast_builder import ASTBuilder
    from semantic_analyzer import SemanticVisitor
    
    def run_test(input_file: str, output_file: str):
        
        
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dfa_path = os.path.join(base_dir, 'rules', 'dfa_rules_final.json')
        input_path = os.path.join(base_dir, input_file)
        output_path = os.path.join(base_dir, output_file)
        
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        print("=" * 70)
        print(f"  Testing: {input_file}")
        print("=" * 70)
        
        
        with open(input_path, 'r') as f:
            source_code = f.read()
        
        
        try:
            tokens = tokenize_from_text(source_code, dfa_path)
            print(f"  ✓ Tokenization: {len(tokens)} tokens")
        except Exception as e:
            print(f"  ✗ Lexer Error: {e}")
            return
        
        
        try:
            parser = Parser(tokens)
            parse_tree = parser.parse()
            print(f"  ✓ Parsing successful")
        except Exception as e:
            print(f"  ✗ Parser Error: {e}")
            return
        
        
        try:
            builder = ASTBuilder()
            ast = builder.build(parse_tree)
            print(f"  ✓ AST construction successful")
        except Exception as e:
            print(f"  ✗ AST Builder Error: {e}")
            return
        
        
        try:
            visitor = SemanticVisitor()
            visitor.visit(ast)
            errors = visitor.errors
            symbol_table = visitor.symbol_table
            if errors:
                print(f"  ✗ Semantic errors: {len(errors)}")
                for err in errors:
                    print(f"      - {err}")
            else:
                print(f"  ✓ Semantic analysis passed (0 errors)")
        except Exception as e:
            print(f"  ✗ Semantic Analysis Error: {e}")
            return
        
        
        print("\n" + "-" * 70)
        print("  AST (Abstract Syntax Tree)")
        print("-" * 70)
        print_ast(ast, is_root=True)
        
        
        print("\n" + "-" * 70)
        print("  DECORATED AST")
        print("-" * 70)
        print("  Legend: → tab_index:<idx>, type:<type>, lev:<scope_level>\n")
        print_decorated_ast(ast, is_root=True)
        
        
        def format_symbol_table(st) -> str:
            lines = []
            
            
            TYPE_NAMES = {
                0: "notyp",     
                1: "ints",      
                2: "reals",     
                3: "bools",     
                4: "chars",     
                5: "arrays",    
                6: "complex",   
            }
            
            def get_type_int(dtype):
                
                if hasattr(dtype, 'value'):
                    val = dtype.value
                    if isinstance(val, int):
                        return val
                    
                    type_map = {"void": 0, "integer": 1, "real": 2, "boolean": 3, "char": 4, "array": 5, "string": 6, "custom": 6}
                    return type_map.get(str(val), 0)
                return 0
            
            
            lines.append("tab (identifier table):")
            lines.append(f"{'idx':<5}{'id':<20}{'obj':<12}{'typ':<6}{'ref':<6}{'nrm':<5}{'lev':<5}{'adr':<5}{'link':<5}")
            lines.append("-" * 69)
            
            for i, entry in enumerate(st.tab):
                if entry is not None:
                    obj_str = entry.obj.value if hasattr(entry.obj, 'value') else str(entry.obj)
                    type_int = get_type_int(entry.type)
                    
                    
                    if i < st.RESERVED_COUNT:
                        lines.append(f"{i:<5}{entry.id:<20}(reserved word)")
                    
                    elif entry.id.lower() in st.RESERVED_WORDS:
                        lines.append(f"{i:<5}{entry.id:<20}{obj_str:<12}... (predefined)")
                    else:
                        
                        nrm_str = "1" if entry.nrm else "0"
                        lines.append(f"{i:<5}{entry.id:<20}{obj_str:<12}{type_int:<6}{entry.ref:<6}{nrm_str:<5}{entry.lev:<5}{entry.adr:<5}{entry.link:<5}")
            
            
            lines.append("")
            lines.append("btab (block table):")
            lines.append(f"{'idx':<5}{'last':<7}{'lpar':<7}{'psze':<7}{'vsze':<7}")
            lines.append("-" * 33)
            for i, entry in enumerate(st.btab):
                lines.append(f"{i:<5}{entry.last:<7}{entry.lastpar:<7}{entry.psize:<7}{entry.vsize:<7}")
            
            
            lines.append("")
            lines.append("atab (array table):")
            if st.atab:
                lines.append(f"{'idx':<5}{'xtyp':<6}{'etyp':<6}{'eref':<7}{'low':<6}{'high':<6}{'elsz':<7}{'size':<6}")
                lines.append("-" * 49)
                for i, entry in enumerate(st.atab):
                    inx_int = get_type_int(entry.inxtyp)
                    el_int = get_type_int(entry.eltyp)
                    lines.append(f"{i:<5}{inx_int:<6}{el_int:<6}{entry.elref:<7}{entry.low:<6}{entry.high:<6}{entry.elsize:<7}{entry.size:<6}")
            else:
                lines.append("atab: (kosong karena tidak ada array)")
            
            return "\n".join(lines)
        
        
        output_lines = []
        output_lines.append("=" * 70)
        output_lines.append(f"Pascal-S Compiler - AST Output")
        output_lines.append(f"Source: {input_file}")
        output_lines.append("=" * 70)
        output_lines.append("")
        
        
        
        output_lines.append("-" * 70)
        output_lines.append("SYMBOL TABLE:")
        output_lines.append("-" * 70)
        output_lines.append(format_symbol_table(symbol_table))
        output_lines.append("")
        
        
        output_lines.append("-" * 70)
        output_lines.append("DECORATED AST:")
        output_lines.append("Legend: → tab_index:<idx>, type:<type>, lev:<scope_level>")
        output_lines.append("-" * 70)
        output_lines.append("")
        output_lines.append(decorated_ast_to_string(ast, is_root=True))
        
        if errors:
            output_lines.append("")
            output_lines.append("-" * 70)
            output_lines.append("SEMANTIC ERRORS:")
            output_lines.append("-" * 70)
            for err in errors:
                output_lines.append(f"  - {err}")
        
        with open(output_path, 'w') as f:
            f.write("\n".join(output_lines))
        
        print(f"\n  ✓ Output saved to: {output_path}")
        print("=" * 70 + "\n")
    
    
    test_files = [
        ("test/milestone-3/input/test_1_valid.pas", "test/milestone-3/output/output_test_1_valid.txt"),
        ("test/milestone-3/input/test_2_types.pas", "test/milestone-3/output/output_test_2_types.txt"),
        ("test/milestone-3/input/test_3_scope.pas", "test/milestone-3/output/output_test_3_scope.txt"),
        ("test/milestone-3/input/test_4_undeclared.pas", "test/milestone-3/output/output_test_4_undeclared.txt"),
        ("test/milestone-3/input/test_5_complex.pas", "test/milestone-3/output/output_test_5_complex.txt"),
        ("test/milestone-3/input/test_brutal_1.pas", "test/milestone-3/output/output_test_brutal_1.txt"),
        ("test/milestone-3/input/test_brutal_2.pas", "test/milestone-3/output/output_test_brutal_2.txt"),
        ("test/milestone-3/input/test_brutal_3.pas", "test/milestone-3/output/output_test_brutal_3.txt"),
    ]
    
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        
        if arg.endswith('.pas'):
            input_file = arg
            
            if len(sys.argv) > 2:
                output_file = sys.argv[2]
            else:
                
                base_name = os.path.splitext(os.path.basename(input_file))[0]
                output_file = f"test/milestone-3/output/output_{base_name}.txt"

            run_test(input_file, output_file)

        
        elif arg.isdigit() and 1 <= int(arg) <= len(test_files):
            idx = int(arg) - 1
            run_test(test_files[idx][0], test_files[idx][1])

        else:
            print(f"Usage: python ast_printer.py [test_number | input_file.pas [output_file.txt]]")
            print(f"  No argument = run all {len(test_files)} tests")
            print(f"  test_number = run specific test (1-{len(test_files)})")
            print(f"  input_file.pas = run on custom file")
            print(f"  input_file.pas output_file.txt = run with custom output path")
            print("")
            print("Predefined tests:")
            print("  1 = test_1_valid.pas")
            print("  2 = test_2_types.pas")
            print("  3 = test_3_scope.pas")
            print("  4 = test_4_undeclared.pas")
            print("  5 = test_5_complex.pas")
            print("  6 = test_brutal_1.pas (deeply nested scopes, shadowing)")
            print("  7 = test_brutal_2.pas (type mixing, operator precedence)")
            print("  8 = test_brutal_3.pas (extreme stress test)")
    else:
        
        print("\n" + "=" * 70)
        print("  Pascal-S Compiler - AST Printer Test Suite")
        print("=" * 70 + "\n")
        
        for input_file, output_file in test_files:
            if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), input_file)):
                run_test(input_file, output_file)
            else:
                print(f"  ⚠ File not found: {input_file}")
        
        print("\n  All tests completed!")
        print("=" * 70)
