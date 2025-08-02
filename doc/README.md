# taxburst documentation

taxburst is a fork of the [Krona](https://github.com/marbl/Krona)
software, (see:
[Ondov, Bergman, and Philippy, 2011](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-12-385)). It
produces static HTML pages that provide an interactive display of a
metagenomic taxonomy.

The goal of taxburst is to update Krona to a maintained, documented
piece of software that can be adapted and adjusted in a variety of
ways.  This is still alpha mode software, to be used at your own risk.

Here is an example screenshot:

![example output screenshot](examples/SRR606249.x.podar.tax.png)

## Support and help

Please file bugs and feature requests on [the issue tracker](https://github.com/taxburst/taxburst/issues).

Pull requests are welcome!

## Additional documentation

More documentation is available at [taxburst.github.io/taxburst/](https://taxburst.github.io/taxburst/).

## Examples

Here are some examples of (interactive!) taxburst plots:

* [SRR11125891.SingleM.html](examples/SRR11125891.SingleM.html) - displaying the results of `singlem pipe` on SRR11125891, a pig gut microbiome.
* [SRR11125891.summarized.html](examples/SRR11125891.summarized.html) - `sourmash` taxonomic breakdown on SRR11125891.
* [SRR11125891.tax_annotate.html](taxburst/examples/SRR11125891.tax_annotate.html) - genome-resolution taxonomic breakdown of SRR11125891.

## Install

taxburst is available on the Python Package Index (PyPI) under [pypi.org/project/taxburst](https://pypi.org/project/taxburst/).

To install it, run:

```
pip install taxburst
```

## Authors

The original Krona software was developed by Brian Ondov, Nicholas
Bergman, and Adam Philippy.

taxburst is developed by Titus Brown. The HTML format is largely unchanged,
but the parsing front-end and output mechanisms have been completely
rewritten in Python.

## Citation information

When using taxburst, please cite the Krona paper:
[Interactive metagenomic visualization in a Web browser](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-12-385),
Ondov et al., 2011.
