from .tree_utils import *

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
            assert c.get("score") is not None
            assert c.get("count") is not None
            assert c.get("rank") is not None
            seen.add(name)


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
        if n1["rank"] != n2["rank"]:
            return False

        c1 = { c["name"] for c in n1.get("children", []) }
        c2 = { c["name"] for c in n2.get("children", []) }
        assert c1 == c2

    return True


def check(top_nodes, *, fail_on_error=True):
    check_all_counts(top_nodes, fail_on_error=fail_on_error)
    check_names(top_nodes, fail_on_error=fail_on_error)
