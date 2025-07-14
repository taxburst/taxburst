def nodes_beneath_top(top_nodes):
    for node in top_nodes:
        yield node
        for node in nodes_beneath(node, recurse=True):
            yield node

def nodes_beneath(node, *, recurse=False):
    for child in node.get('children', []):
        yield child
        if recurse:
            for c in nodes_beneath(child):
                yield c


def collect_all_nodes(top_nodes_list):
    nodes = []
    for top_node in top_nodes_list:
        nodes.append(top_node)
        for node in nodes_beneath(top_node, recurse=True):
            nodes.append(node)
    return nodes


def check_count(node, *, fail_on_error=False):
    "Check for a parent node count that is less than sum of child node counts."
    children = node.get("children", [])
    if not children:
        return

    sub_counts = round(sum([float(n["count"]) for n in children]))
    count = round(float(node["count"]), 4)

    if count < sub_counts:
        print(f"WARNING: parent node {node['name']} has count {count}, but nodes beneath sum to {sub_counts}")
        print([ n["count"] for n in children ])
        if fail_on_error:
            raise Exception("ERROR: some counts do not make sense; see warning message above")


def check_all_counts(top_nodes, *, fail_on_error=True):
    "Check for parent node counts that are less than sum of child node counts."
    for node in nodes_beneath_top(top_nodes):
        check_count(node, fail_on_error=fail_on_error)


def check_names(top_nodes, *, fail_on_error=True):
    "Check for empty names & duplicate names."
    names = set()
    do_fail = False
    for node in nodes_beneath_top(top_nodes):
        name = node['name']
        if not name:
            print(F"WARNING: node has empty name!?")
            do_fail = True
        elif name in names:
            print(f"WARNING: duplicate node name: '{name}'")
            do_fail = True
        else:
            names.add(name)

    if do_fail and fail_on_error:
        raise Exception("ERROR: bad name(s); see warnings above.")


def check(top_nodes, *, fail_on_error=True):
    check_all_counts(top_nodes, fail_on_error=fail_on_error)
    check_names(top_nodes, fail_on_error=fail_on_error)
