# Information for Developers

Please file issues in
[the issue tracker](https://github.com/taxburst/taxburst/issues) if you have questions or comments!

Pull requests are welcome!

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
