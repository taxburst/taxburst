# Command-line docs for taxburst

## Basic usage

The basic usage for taxburst is simple:

```
taxburst -F <format> <input_file> -o <output.HTML>
```

The following input formats are supported:

* `tax_annotate`: a sourmash file produced by running  `sourmash tax annotate` on the output of `sourmash gather`. This is the recommended sourmash format.
* `csv_summary`: a sourmash file produced by running `sourmash tax metagenome` on the output of `sourmash gather`.
* `SingleM`: the profile TSV output by `singlem pipe ... -p <output.tsv>`.
* `krona`: a krona-format TSV file.
* `json`: a list of nested dictionaries, in JSON format; see below for details.

## Formats, counts, and scores

### `tax_annotate`

The `-F tax_annotate` format will take in sourmash gather results
annotated with `sourmash tax annotate`. The resulting counts in the
taxburst display will be the weighted number of hashes matching at
each taxonomic level; multiply this by the scaled factor used in
sourmash to get an estimate of the bp in the original metagenome.

This format is the preferred sourmash format because it supports
assignments down to the genome level, while `sourmash tax
metagenome`'s `csv_summary` format only goes down to the species
level.

### `csv_summary`

The `-F csv_summary` format will take in the results of `sourmash tax
metagenome` run with `-F csv_summary`. The counts produced for
taxburst are 1000 times the `f_weighted_at_rank` value.

### `SingleM`

The `-F SingleM` format will take in the results of `singlem pipe -p`,
a profile TSV file. The count reported by taxburst is 1000 x the
`coverage` column.

```tsv
sample  coverage        taxonomy
SRR11125891_1   0.48    Root; d__Archaea
SRR11125891_1   1.73    Root; d__Bacteria
SRR11125891_1   2.21    Root; d__Bacteria; p__Bacillota
SRR11125891_1   0.05    Root; d__Bacteria; p__Pseudomonadota
SRR11125891_1   0.17    Root; d__Bacteria; p__Verrucomicrobiota
SRR11125891_1   2.89    Root; d__Bacteria; p__Bacillota; c__Clostridia
SRR11125891_1   0.56    Root; d__Bacteria; p__Bacillota; c__Bacilli
SRR11125891_1   0.57    Root; d__Bacteria; p__Bacillota; c__Negativicutes
```

### `krona` format

The `-F krona` format will take in a standard Krona-format file. The
reported count is 1000 x the `fraction` column.

```tsv
fraction        superkingdom    phylum  class   order   family  genus   species
0.06582267833109018     Eukaryota       Chordata        Mammalia        Artiodactyla    Suidae  Sus     Sus scrofa
0.0259084791386272      d__Bacteria     p__Pseudomonadota       c__Gammaproteobacteria  o__Enterobacterales     f__Enterobacteriaceae   g__Escherichia  s__Escherichia coli
```

## Outputting JSON format

Instead of (or in addition to) an HTML file, taxburst can produce a
JSON format with `--save-json <output.json>`. This format can then be
consumed by taxburst with `-F json`.

The JSON format is a list of nested dictionaries:
```json
[
  {
    "name": "A",
    "count": 5,
    "rank": "Phylum",
    "children": [
      {
        "name": "B",
        "count": 3,
        "score": 0.2,
        "rank": "Class"
      },
      {
        "name": "C",
        "count": 1,
        "rank": "Class"
      }
    ]
  }
]
```
