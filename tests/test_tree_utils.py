"Test the checks code. IINNNNNNNCEPTION!!"
import pytest

from taxburst import checks, tree_utils
from taxburst_tst_utils import get_example_filepath

good_nodes = [
    {
        "name": "A",
        "count": 5,
        "score": 0.831,
        "rank": "Phylum",
        "children": [
            {"name": "B", "count": 3, "score": 0.2, "rank": "Class"},
            {"name": "C", "count": 1, "score": 0.1, "rank": "Class"},
        ],
    },
]

def test_check_trees_are_equal():
    a_copy = tree_utils.copy_tree(good_nodes)
    assert checks.trees_are_equal(good_nodes, a_copy)


def test_tricky_combo():
    from taxburst import parsers

    tree1 = parsers.parse_file(get_example_filepath("SRR11125891.singleM.profile.tsv"), "SingleM")[0]
    tree2 = parsers.parse_file(get_example_filepath("SRR11125891.summarized.csv"), "csv_summary")[0]
    tree3 = parsers.parse_file(get_example_filepath("SRR11125891.t0.gather.with-lineages.csv"), "tax_annotate")[0]

    copy1 = tree_utils.copy_tree(tree1)
    copy2 = tree_utils.copy_tree(tree2)
    copy3 = tree_utils.copy_tree(tree3)

    all_names = set()
    all_names.update([ n["name"] for n in tree_utils.nodes_beneath_top(tree1) ])
    all_names.update([ n["name"] for n in tree_utils.nodes_beneath_top(tree2) ])
    all_names.update([ n["name"] for n in tree_utils.nodes_beneath_top(tree3) ])

    aug_tree = tree_utils.augment_tree(tree1, [tree2, tree3])
    aug_nodes = tree_utils.collect_all_nodes(aug_tree)

    found = set()
    for node in aug_nodes:
        found.add(node["name"])
    missing = all_names - found
    assert not missing, len(missing)

    checks.check_structure(aug_tree)
    assert checks.trees_are_equal(tree1, copy1)
    assert checks.trees_are_equal(tree2, copy2)
    assert checks.trees_are_equal(tree3, copy3)    
