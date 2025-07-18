# taxburst: sunburst charts for taxonomy, based on Krona

**WARNING: alpha mode software. Use at your own risk.**

This is an update of Krona, written with the following goals in mind:

* liberate tax displays from the tyranny of NCBI taxonomy IDs and taxdump;
* support dynamic generation of Krona-style plots;
* rewrite in modern Python;
* support ~nicer multi-stage generation of XHTML;
* probably other things;

The output HTML is derived from Krona, https://github.com/marbl/Krona.

All bugs are mine until proven otherwise.

Please file bugs and feature requests on [the issue tracker](https://github.com/taxburst/taxburst/issues).

## Examples

[A small example](https://taxburst.github.io/taxburst/pages/small.tax.html) - a test data set.

[A bigger example](https://taxburst.github.io/taxburst/pages/SRR606249.x.podar.tax.html) - SRR606249 against known reference genomes.

A screenshot:

![example output screenshot](examples/SRR606249.x.podar.tax.png)

## Install

```
pip install taxburst
```

## Run

### Using sourmash tax metagenome output - `summary_csv` format

An example using the summary_csv format
from `sourmash tax metagenome` (see
[docs](https://sourmash.readthedocs.io/en/latest/command-line.html#sourmash-tax-metagenome-summarize-metagenome-content-from-gather-results)),
```
taxburst SRR11125891.summarized.csv -o SRR11125891.summarized.html
```
then open `SRR11125891.summarized.html` in a browser.

### Using `sourmash tax annotate` output

An example using the with-lineages format
from `sourmash tax annotate` (see
[tax annotate docs](https://sourmash.readthedocs.io/en/latest/command-line.html#sourmash-tax-annotate-annotates-gather-output-with-taxonomy)

```
taxburst -F tax_annotate \
    SRR11125891.t0.gather.with-lineages.csv \
    -o SRR11125891.tax_annotate.html
```
then open `SRR11125891.tax_annotate.html` in a browser.

### Using `singleM pipe` output

An example using the profile format
from `singleM pipe` (see
[singlem pipe docs](https://wwood.github.io/singlem/tools/pipe)):

```
taxburst -F singlem \
    SRR11125891.singleM.profile.tsv \
    -o SRR11125891.singleM.html
```
then open `SRR11125891.singleM.html` in a browser.

## Background and history

[Krona](https://github.com/marbl/Krona) is a super cool way to explore
taxonomic breakdowns of metagenomes. But it's kind of old, and isn't
being actively maintained. Moreover, it doesn't work easily with
GTDB or other non-NCBI taxonomies.

So, why not grab the JavaScript code and rewrite the preprocessing code?

Voila! 'taxburst'!

I'd call it Krona2 or something, but the licensing for Krona prohibits that,
to my understanding. Hence, 'taxburst'.

## Citation information

When using Krona, please cite:
[Interactive metagenomic visualization in a Web browser](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-12-385),
Ondov et al., 2011.

---

CTB July 2025

ctbrown@ucdavis.edu
