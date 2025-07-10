all:
	cd test_workflow && snakemake --delete-all-output && snakemake
