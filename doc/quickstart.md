# Quickstart

## Example command lines

All data files are available in the GitHub repository under `examples/`.

### Using `sourmash tax metagenome` output - `summary_csv` format

An example using the summary_csv format
from `sourmash tax metagenome` (see
[tax metagenome docs](https://sourmash.readthedocs.io/en/latest/command-line.html#sourmash-tax-metagenome-summarize-metagenome-content-from-gather-results)),
```
taxburst examples/SRR11125891.summarized.csv \
    -o pages/SRR11125891.summarized.html
```
then open `pages/SRR11125891.summarized.html` in a browser.

### Using `sourmash tax annotate` output

An example using the with-lineages format
from `sourmash tax annotate` (see
[tax annotate docs](https://sourmash.readthedocs.io/en/latest/command-line.html#sourmash-tax-annotate-annotates-gather-output-with-taxonomy)

```
taxburst -F tax_annotate \
    examples/SRR11125891.t0.gather.with-lineages.csv \
    -o pages/SRR11125891.tax_annotate.html
```
then open `pages/SRR11125891.tax_annotate.html` in a browser.

### Using `singleM pipe` output

An example using the profile format
from `singlem pipe` (see
[singlem pipe docs](https://wwood.github.io/singlem/tools/pipe)):

```
taxburst -F singleM \
    examples/SRR11125891.singleM.profile.tsv \
    -o pages/SRR11125891.singleM.html
```
then open `pages/SRR11125891.singleM.html` in a browser.

