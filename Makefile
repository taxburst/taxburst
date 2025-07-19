.PHONY: dist test

all: test
	cd examples && snakemake --delete-all-output && snakemake -j 1

dist:
	python -m build

test:
	pytest
