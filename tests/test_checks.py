"Test the checks code. IINNNNNNNCEPTION!!"
import pytest

from taxburst import checks

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

def test_check_structure_1():
    checks.check_structure(good_nodes)


def test_check_structure_2():
    bad = checks.copy_tree(good_nodes)
    bad[0]["children"][1]["name"] = "B"
    with pytest.raises(AssertionError):
        checks.check_structure(bad)


def test_check_fail_if_tree_shares_objects():
    with pytest.raises(AssertionError):
        checks.trees_are_equal(good_nodes, good_nodes)
