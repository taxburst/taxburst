import pytest

import taxburst
from taxburst import checks, parsers

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


def test_assign_children_empty_lin():
    # empty lineages are not allowed by 'assign_children'
    node_d = dict(name='foo', rank='superkingdom', count=100)
    nodes_by_tax = { '': node_d }

    with pytest.raises(AssertionError):
        parsers.assign_children(nodes_by_tax)


def test_assign_children_empty_superkingdom():
    node_d = dict(name='foo', rank='phylum', count=100)
    nodes_by_tax = { ';test': node_d }

    with pytest.raises(AssertionError) as e:
        parsers.assign_children(nodes_by_tax)

    assert 'has empty sublineage' in str(e.value)
