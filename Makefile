.PHONY: dist test

all:
	cd test_workflow && snakemake --delete-all-output && snakemake

dist:
	python -m build

test:
	pytest
