#! /usr/bin/env python
import sys
import pprint
import argparse
import os.path
import json

from . import checks
from .parsers import parse_file
from .taxinfo import ranks
from .output import generate_html


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("tax_csv", help="input tax CSV, in sourmash csv_summary format")
    p.add_argument("-F", "--input-format", default="csv_summary",
                   choices=[
                       "csv_summary",
                       "tax_annotate",
                       "SingleM",
                   ])
    p.add_argument(
        "-o", "--output-html", required=True, help="output HTML file to this location."
    )
    p.add_argument("--save-json", help="output a JSON file of the taxonomy")
    p.add_argument("--check-tree", help="check that tree makes sense",
                   action="store_true")
    p.add_argument("--fail-on-error", help="fail if tree doesn't pass checks; implies --check-tree",
                   action="store_true")
    if argv is None:
        args = p.parse_args()
    else:
        args = p.parse_args(argv)

    # parse!
    top_nodes, name = parsers.parse_file(args.tax_csv, args.input_format)
    assert top_nodes is not None

    if args.save_json:
        print(f"saving tree in JSON format to '{args.save_json}'")
        with open(args.save_json, "wt") as fp:
            json.dump(top_nodes, fp)

    if args.check_tree or args.fail_on_error:
        checks.check_all_counts(top_nodes, fail_on_error=args.fail_on_error)

    # build XHTML
    content = generate_html(top_nodes, name=name)

    # output!!
    with open(args.output_html, "wt") as fp:
        fp.write(content)

    print(f"wrote output to '{args.output_html}'")
