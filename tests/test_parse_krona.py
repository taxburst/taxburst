import pytest

import taxburst
from taxburst import parsers
from taxburst import checks
from taxburst_tst_utils import get_example_filepath


def test_basic_krona():
    tsv = get_example_filepath("SRR11125891.krona.tsv")
    top_nodes = parsers.parse_krona(tsv)
    all_nodes = checks.collect_all_nodes(top_nodes)

    assert len(top_nodes) == 4
    assert len(all_nodes) == 1429

    check_counts = {
        "p__Bacillota": 612,
        "p__Bacteroidota": 56,
        "s__Methanocatella smithii": 28,
    }
    check_percent = {
        "p__Bacillota": 61.24,
        "p__Bacteroidota": 5.56,
        "s__Methanocatella smithii": 2.8,
    }

    total = sum([node["count"] for node in top_nodes])

    found_count = set()
    found_percent = set()

    for node in checks.nodes_beneath_top(top_nodes):
        name = node["name"]
        if name in check_counts:
            count = round(node["count"], 0)
            assert count == check_counts[name], (name, count, check_counts[name])
            found_count.add(name)

        if name in check_percent:
            count = node["count"]
            p = round(count / total * 100, 2)
            assert p == check_percent[name], (name, p, check_percent[name])
            found_percent.add(name)

    expected_count = set(check_counts)
    remaining = expected_count - found_count
    assert not remaining, f"missing counts for: {remaining}"

    expected_percent = set(check_percent)
    remaining = expected_percent - found_percent
    assert not remaining, f"missing percent for: {remaining}"
