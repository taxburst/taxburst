import pytest

import taxburst
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


def test_check_ok():
    checks.check(good_nodes, fail_on_error=True)


bad_nodes = [
    {
        "name": "",
        "count": 2,
        "score": 0.831,
        "rank": "Phylum",
        "children": [
            {"name": "B", "count": 3, "score": 0.2, "rank": "Class"},
            {"name": "C", "count": 1, "score": 0.1, "rank": "Class"},
        ],
    },
]


def test_check_fail():
    with pytest.raises(Exception):
        checks.check(bad_nodes, fail_on_error=True)


def test_check_fail_name():
    with pytest.raises(Exception):
        checks.check_names(bad_nodes, fail_on_error=True)


def test_check_fail_counts():
    with pytest.raises(Exception):
        checks.check_all_counts(bad_nodes, fail_on_error=True)
