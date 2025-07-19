import pytest

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
