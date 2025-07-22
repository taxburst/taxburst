def nodes_beneath_top(top_nodes):
    """
    Yield all nodes beneath a list of nodes (including the nodes in the list).
    """
    for node in top_nodes:
        yield node
        for n in nodes_beneath(node, recurse=True):
            yield n


def nodes_beneath(node, *, recurse=False):
    "Yield all nodes directly under this node, with optional recursion."
    for child in node.get('children', []):
        yield child
        if recurse:
            for c in nodes_beneath(child, recurse=recurse):
                yield c


def collect_all_nodes(top_nodes_list):
    "Return a _list_ of all nodes."
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


def check_structure(nodelist):
    seen = set()
    for n in nodelist:
        name = n["name"]
        assert name not in seen, f"duplicate name: '{name}'"
        seen.add(name)
        for c in nodes_beneath(n, recurse=True):
            name = c["name"]
            assert name not in seen, f"duplicate name: '{name}'"
            seen.add(name)


def copy_tree(nodelist):
    "Make a copy of a list of nodes (recursively)"
    new_nodelist = []
    for n in nodelist:
        new_node = dict(n)      # copy
        children = n.get("children")
        if children:
            new_node["children"] = copy_tree(children)
        new_nodelist.append(new_node)
        
    return new_nodelist


def trees_are_equal(top_nodes1, top_nodes2):
    "Check that trees are equal in name/score/count and children."
    nodelist1 = collect_all_nodes(top_nodes1)
    nodelist2 = collect_all_nodes(top_nodes2)

    n1_to_nodes = {}
    n2_to_nodes = {}
    for n1 in nodelist1:
        n1_to_nodes[n1["name"]] = n1
    for n2 in nodelist2:
        n2_to_nodes[n2["name"]] = n2

    for name in set(n1_to_nodes) | set(n2_to_nodes):
        n1 = n1_to_nodes[name]
        n2 = n2_to_nodes[name]
        assert n1 is not n2, "trees share specific node objects, oops"

        if n1["name"] != n2["name"]:
            return False
        if n1["score"] != n2["score"]:
            return False
        if n1["count"] != n2["count"]:
            return False

        c1 = { c["name"] for c in n1.get("children", []) }
        c2 = { c["name"] for c in n2.get("children", []) }
        assert c1 == c2

    return True


def augment_node(node, names_to_nodes):
    "Augment a node with child nodes from other trees."
    name = node["name"]

    child_names = set()
    for other_node in names_to_nodes[name]:
        for child in other_node.get("children", []):
            child_name = child["name"]
            child_names.add(child_name)

    remaining = set(child_names)
    children = node.get("children", []) # make a copy
    new_children = []
    for child in children:
        remaining.remove(child["name"])
        child = dict(child)     # make a copy
        augment_node(child, names_to_nodes)
        new_children.append(child)

    for missing_child in remaining:
        new_child = dict(name=missing_child,
                         score=0,
                         count=0)
        # add children from others?
        new_children.append(new_child)
        augment_node(new_child, names_to_nodes)

    node["children"] = new_children


def augment_tree(first_top_nodes, other_top_nodes, names_to_nodes):
    "Augment a set of top nodes with child nodes from other trees."
    names = set()
    found = set()
    for nodelist in other_top_nodes:
        for top_node in nodelist:
            names.add(top_node.get("name"))

    # augment existing top node
    new_top_nodes = []
    for top_node in first_top_nodes:
        top_node = dict(top_node)
        found.add(top_node["name"])
        augment_node(top_node, names_to_nodes)

        new_top_nodes.append(top_node)

    # add missing top nodes
    for missing_name in names - found:
        new_node = dict(name=missing_name,
                        score=0,
                        count=0)
        augment_node(new_node, names_to_nodes)
        new_top_nodes.append(new_node)

    return new_top_nodes


def check(top_nodes, *, fail_on_error=True):
    check_all_counts(top_nodes, fail_on_error=fail_on_error)
    check_names(top_nodes, fail_on_error=fail_on_error)
