def print_tree(node, indent="", is_last=True, is_root=False):
    if node is None:
        return

    connector = "" if is_root else ("└── " if is_last else "├── ")

    if isinstance(node, dict):
        if "type" in node:
            print(indent + connector + node["type"])
            children = node.get("children", [])
            new_indent = indent if is_root else (indent + ("    " if is_last else "│   "))

            for i, child in enumerate(children):
                print_tree(child, new_indent, i == len(children) - 1, is_root=False)
        else:
            print(indent + connector + str(node))
    else:
        token_str = f"{node.type}({node.value})"
        print(indent + connector + token_str)

def tree_to_string(node, indent="", is_last=True):
    if node is None:
        return ""

    result = []
    connector = "└── " if is_last else "├── "

    if isinstance(node, dict):
        if "type" in node:
            result.append(indent + connector + node["type"])
            children = node.get("children", [])
            new_indent = indent + ("    " if is_last else "│   ")

            for i, child in enumerate(children):
                result.append(tree_to_string(child, new_indent, i == len(children) - 1))
        else:
            result.append(indent + connector + str(node))
    else:
        token_str = f"{node.type}({node.value})"
        result.append(indent + connector + token_str)

    return "\n".join(result)
