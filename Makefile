.PHONY: dist test examples

all: test examples

examples:
	cd examples && snakemake --delete-all-output && snakemake -j 1

dist:
	python -m build

test:
	pytest

serve:
	mkdocs serve
