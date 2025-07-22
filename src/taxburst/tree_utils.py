from collections import defaultdict
from .taxinfo import ranks


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


def augment_node(node, names_to_nodes):
    "Augment a node with child nodes from other trees."
    name = node["name"]
    rank = node["rank"]

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

    if remaining:
        this_rank_i = ranks.index(rank)
        child_rank = ranks[this_rank_i + 1]

        for missing_child in remaining:
            new_child = dict(name=missing_child,
                             score=0,
                             count=0,
                             rank=child_rank)
            # add children from others?
            new_children.append(new_child)
            augment_node(new_child, names_to_nodes)

    if new_children:
        node["children"] = new_children


def augment_tree(first_top_nodes, other_top_nodes):
    "Augment a set of top nodes with child nodes from other trees."
    names_to_nodes = defaultdict(list)
    for top_nodes in [first_top_nodes] + other_top_nodes:
        for node in nodes_beneath_top(top_nodes):
            name = node["name"]
            assert name         # don't allow names to be empty
            names_to_nodes[name].append(node)
    
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

    top_rank = top_node["rank"]

    # add missing top nodes
    for missing_name in names - found:
        new_node = dict(name=missing_name,
                        score=0,
                        count=0,
                        rank=top_rank)
        augment_node(new_node, names_to_nodes)
        new_top_nodes.append(new_node)

    return new_top_nodes
