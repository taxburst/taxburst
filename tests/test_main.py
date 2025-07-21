"Test command-line level stuff, at the Python level."
import pytest
import os

import taxburst
from taxburst import checks
from taxburst import parsers
from taxburst_tst_utils import get_example_filepath


class FakeArgs:
    def __init__(self, **entries):
        self.__dict__.update(entries)


def test_noargs():
    with pytest.raises(SystemExit) as e:
        taxburst.main(argv=[])

    assert e.value.code == 2


def test_output_required(tmp_path):
    # check that _some_ output is req
    path = get_example_filepath("SRR11125891.lineages.json")
    output = tmp_path / "xxx.html"

    with pytest.raises(SystemExit) as e:
        taxburst.main([path, '-F', 'json'])

    assert e.value.code == -1


def test_output_json_ok(tmp_path):
    "just JSON output is fine"
    path = get_example_filepath("SRR11125891.lineages.json")
    output = tmp_path / "xxx.json"

    taxburst.main([path, '-F', 'json', "--save-json", str(output)])


def test_load_json(tmp_path):
    path = get_example_filepath("SRR11125891.lineages.json")
    output = tmp_path / "xxx.html"
    taxburst.main([path, "-o", str(output), '-F', 'json'])

    assert os.path.exists(output)


def test_csv_summ_default(tmp_path):
    path = get_example_filepath("SRR11125891.summarized.csv")
    output = tmp_path / "xxx.html"
    taxburst.main([path, "-o", str(output)])

    assert os.path.exists(output)


def test_csv_summ_specified(tmp_path):
    path = get_example_filepath("SRR11125891.summarized.csv")
    output = tmp_path / "xxx.html"
    taxburst.main([path, "-o", str(output), "-F", "csv_summary"])

    assert os.path.exists(output)


def test_tax_ann(tmp_path):
    path = get_example_filepath("SRR11125891.t0.gather.with-lineages.csv")
    output = tmp_path / "xxx.html"
    taxburst.main([path, "-o", str(output), "-F", "tax_annotate"])

    assert os.path.exists(output)


def test_SingleM(tmp_path):
    path = get_example_filepath("SRR11125891.singleM.profile.tsv")
    output = tmp_path / "xxx.html"
    taxburst.main([path, "-o", str(output), "-F", "SingleM"])

    assert os.path.exists(output)
