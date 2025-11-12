# tree printer buat nampilin parse tree ke terminal
# format output pake ASCII art biar keliatan struktur hierarkinya

def print_tree(node, indent="", is_last=True, is_root=False):
    # print parse tree ke terminal dengan format tree
    if node is None:
        return

    # tentuin connector (├── atau └──) tergantung posisi
    connector = "" if is_root else ("└── " if is_last else "├── ")

    if isinstance(node, dict):
        # node biasa dengan children
        if "type" in node:
            print(indent + connector + node["type"])
            children = node.get("children", [])
            new_indent = indent if is_root else (indent + ("    " if is_last else "│   "))

            # rekursif print semua children
            for i, child in enumerate(children):
                print_tree(child, new_indent, i == len(children) - 1, is_root=False)
        else:
            print(indent + connector + str(node))
    else:
        # leaf node (token)
        token_str = f"{node.type}({node.value})"
        print(indent + connector + token_str)

def tree_to_string(node, indent="", is_last=True):
    # sama kayak print_tree tapi return string instead of print
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
