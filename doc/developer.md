# Information for Developers

Please file issues in
[the issue tracker](https://github.com/taxburst/taxburst/issues) if
you have questions or comments!

Pull requests are welcome!

## Guidance on writing new parsers

The current built-in parsers are contained in
`src/taxburst/parsers.py`.  In general, if you are a Python
programmer, the easiest way to proceed is to copy and rename an
existing parsing class (e.g. `Parse_SourmashCSVSummary` and modify the
`build` method.  Then add a new if/else branch in the top level
`parse_file` method.

The current parsers mostly work by creating a `nodes_by_tax`
dictionary that contains (key, value) pairs where each key is a
semicolon-separated lineage (e.g. `d__Bacteria;p__Spirochaetota`) and
each value is a "node dictionary", a dictionary containing at least
`name`, `count`, and `rank`. This dictionary must contain all lineage
subpaths.

If the `nodes_by_tax` dictionary is built properly, then the function
`taxburst.parsers.assign_children` will build the hierarchy of nodes
needed for conversion into XHTML.

Many consistency checks are applied to this tree before output, and
additional consistency checks can be run with `--check-tree` on the
taxburst command line. If you find an error that is not caught by
these checks, please file an issue about it and we will add it to the
checks!

An alternative approach to writing a parser is to produce your own
set of nested dictionaries in Python, or, if you prefer to program
in a different language, write code to output the JSON format (see below).

### Examples, documentation, and automated testing

For each new Python-based format parser, please add an example
(ideally, calculated for the metagenome `SRR11125891`) to the
`examples/` top-level directory, and (ideally) add a step to the
snakemake workflow in `examples/Snakefile` so that taxburst is
automatically run on the example. You should also add a link to the
example output in the `doc/README.md` file.

Please also add a brief description of the new parser format to
the `doc/command-line.md` document.

Last but by no means least, please add a new `tests/test_parse_*.py` file
that runs the parser and checks a few values.

If you are writing a parser in another language that outputs JSON,
please feel free to include the original file and the JSON output file
in the examples, and link to your parsing code in the documentation.
Note: for the moment, the JSON format doesn't support custom attribute
display; if you need this, please let us know and we'll figure
something out!

Feel free to ask for help on any of these tasks!p

### Additional points

There is no inherent restriction on ranks, although the current parsing
classes all inherit from `GenericParser` which supports the normal
NCBI/GTDB ranks from "superkingdom" on down. Eventually we want to support
custom ranks (LINS, ICTV, etc); drop us a note if you're interested in
helping out, or testing!

Other keys are allowed in the node dictionary but are ignored in the
output format unless an `extra_attributes` dictionary is returned by
the parsing function; see the `tax_annotate` format parser for an
example.

## Internals of the input and output formats

The taxburst code works in the following stages:

1. Load in an input file containing some taxonomic summary.
2. Convert that summary into an internal tree format in Python, based on nested lists of dictionaries.
3. Convert that internal tree format into XHTML, which is then saved in a static HTML file with accompanying JavaScript to support interactive visualization.

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

See
[`examples/simple-output.py`](https://github.com/taxburst/taxburst/blob/main/examples/simple-output.py)
in the github repo for example code to produce an output HTML from
this.

### JSON version of the internal dictionary format

This nested dictionary format converts to fairly simple JSON:
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

## Output formatting

taxburst uses
[Jinja2 templates](https://jinja.palletsprojects.com/en/stable/) to
provide customizable formatting of the HTML output. Please see the
files in
[src/taxburst/templates/](https://github.com/taxburst/taxburst/tree/main/src/taxburst/templates)
for implementation.
