# Additional documentation

## Using with sourmash output

The suggested sourmash workflow is:

* run sourmash gather to generate a gather CSV;
* annotate the gather output with taxonomy using `sourmash tax annotate`;
* use `taxburst -F tax_annotate <with-lineages CSV> -o <taxburst HTML>`

This will give the most detailed output possible.

## Formats, counts, and scores

### `tax_annotate`

The `-F tax_annotate` format will take in sourmash gather results
annotated with `sourmash tax annotate`. The resulting counts in the
taxburst display will be the weighted number of hashes matching at
each taxonomic level; multiply this by the scaled factor used in
sourmash to get an estimate of the bp in the original metagenome.  The
`score` (displayed as "Avg. confidence" in the taxburst panel) is the
normalized fraction of the number of unique k-mers in the metagenome
matched at this rank (unweighted) - it is the aggregated
`f_unique_weighted` value in the sourmash gather output.

### `csv_summary`

The `-F csv_summary` format will take in the results of `sourmash tax
metagenome` run with `-F csv_summary`. The counts produced for
taxburst are 1000 times the `f_weighted_at_rank` value, and the score
is the `fration` column (aggregated `f_unique_weighted`) at that rank.

### `SingleM`

The `-F SingleM` format will take in the results of `singlem pipe -p`,
a profile TSV file. The count reported by taxburst is 1000 x the
`coverage` column. `score` is set to 1.0 for all rows.

## Internals of the input and output formats

The taxburst code works in the following stages:

1. Load in an input file containing some taxonomic summary.
2. Convert that summary into an internal tree format in Python, based on nested lists of dictionaries.
3. Convert that internal tree format into XHTML, which can then be saved in a static HTML file with accompanying JavaScript to support interactive visualization.

These two intermediate formats are useful to know about because there
are two ways to support new input formats: you can either write a
Python function to convert a new format into the internal tree format,
or you can write code in _any_ language to output JSON that can be
loaded into the internal tree format.

taxburst consumes a JSON version of this format with `-F json`, and
produces this format with `--save-json <filenam>`.

(In the future, it should be possible to modify the internal JavaScript in
the static HTML file to read the JSON directly, which would simplify this
even more and allow for more flexibility as well.)

### Internal dictionary format

Here is a simple example of the internal dictionary format:

```python
nodes = [
    {
        "name": "A",
        "count": 5,
        "score": 0.831,
        "rank": "Phylum",
        "children": [
            {"name": "B", "count": 3, "score": 0.2, "rank": "Class"},
            {"name": "C", "count": 1, "score": 0.1, "rank": "Class"},
        ],
    },
]
```

See `examples/simple-output.py` in the github repo for example code
to produce an output HTML from this.

### JSON version of the internal dictionary format

This nested dictionary format converts to fairly simple JSON:
```json
[
  {
    "name": "A",
    "count": 5,
    "score": 0.831,
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
        "score": 0.1,
        "rank": "Class"
      }
    ]
  }
]
```

This can be loaded from a file and converted into an HTML file like so:
```python
import json
import taxburst

with open('nodes.json') as fp:
   nodes = json.load(fp)
   
content = taxburst.generate_html(nodes)
with open('nodes.html') as fp:
   fp.write(content)
```
This is equivalent to `taxburst -F json nodes.json -o nodes.html`.
