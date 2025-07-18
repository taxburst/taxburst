import os.path
import pytest

import taxburst
from taxburst import checks


example_dir = os.path.join(os.path.dirname(__file__),
                           '../examples')

def get_example_filepath(filename):
    return os.path.abspath(os.path.join(example_dir, filename))


def test_basic_tax_annotate():
    csv = get_example_filepath('SRR11125891.summarized.csv')
    top_nodes = taxburst.parse_csv_summary(csv)

    assert len(top_nodes) == 4 # Mammalia, unclassified

    check_counts = {'p__Bacillota': 548,
                    'p__Bacteroidota': 47,
                    's__Methanocatella smithii': 27,
                    'Eukaryota': 27}
    check_percent = {'p__Bacillota': 54.75,
                     'p__Bacteroidota': 4.71,
                     's__Methanocatella smithii': 2.72,
                     'Eukaryota': 2.73}

    total = sum([ node["count"] for node in top_nodes ])

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
