"Test the checks code. IINNNNNNNCEPTION!!"
import pytest

from taxburst import checks, tree_utils

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
