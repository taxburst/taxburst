.PHONY: dist test examples doc

all: test examples

examples:
	cd examples && snakemake --delete-all-output && snakemake -j 1
	cp examples/*.html doc/examples/

dist:
	python -m build

test:
	pytest

serve:
	mkdocs serve

doc:
	mkdocs build
