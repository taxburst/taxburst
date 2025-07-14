#! /usr/bin/env python
import sys
import csv
import pprint
import argparse
import os.path
from collections import defaultdict
import json

from . import checks

dirname = os.path.dirname(__file__)
templatedir = os.path.join(dirname, "./templates")

ranks = [
    "superkingdom",
    "phylum",
    "class",
    "order",
    "family",
    "genus",
    "species",
    "strain",
    "genome",
]


def generate_html(top_nodes, *, name=None):
    # find templates
    outer_template = os.path.join(templatedir, "krona-template.html")
    inner_template = os.path.join(templatedir, "krona-fill.html")

    # read templates
    with open(outer_template, "rt") as fp:
        template = fp.read()

    with open(inner_template, "rt") as fp:
        fill = fp.read()

    fill2 = [make_node_xml(n) for n in top_nodes]

    # build top node
    if name is None:
        name = "all"

    count_sum = round(sum([float(n["count"]) for n in top_nodes]), 4)
    fill2 = "\n".join(fill2)
    fill2 = (
        f'<node name="{name}">\n<count><val>{count_sum}</val></count>\n{fill2}\n</node>'
    )

    # fill in template
    fill = fill.replace("{{ nodes }}", fill2)
    template = template.replace("{{ krona }}", fill)

    return template


# track total node count, for distinguishing purposes
node_count = 1

def make_node_xml(d, indent=0):
    "Turn a given node dict into a <node>."
    global node_count

    # any children?
    children = d.get("children", [])
    child_nodes = []
    if children:
        child_nodes = [make_node_xml(dd, indent=indent + 1) for dd in children]

    # grab & format values
    name = d["name"]
    count = float(d["count"])
    score = float(d["score"])
    rank = d["rank"]
    child_out = ""
    if child_nodes:
        child_out = "\n" + "\n".join(child_nodes)

    # indent nicely, 'cause why ot
    spc = "  " * indent

    x = f"""\
{spc}<node name="{name}">
{spc}    <members><val>node{node_count}.members.0.js</val></members>
{spc}    <rank><val>{rank}</val></rank>
{spc}    <count><val>{count:.01f}</val></count>
{spc}    <score><val>{score:.03f}</val></score>{child_out}
{spc}</node>"""
    # increment global node count
    node_count += 1

    return x


def extract_rows_beneath(tax_rows, prefix, rank_idx):
    "Extract rows beneath a node."

    # no more!
    if rank_idx >= len(ranks):
        return []

    children = []
    prefix_str = prefix + ";"

    desired_rank = ranks[rank_idx]
    for lineage, val in tax_rows:
        if val["rank"] == desired_rank and lineage.startswith(prefix_str):
            children.append(val)

    return children


def make_child_d(tax_rows, prefix, this_row, rank_idx):
    "Make child node dicts."
    lineage = this_row["lineage"]

    children = []

    # never descend into unclassified
    if lineage == "unclassified":
        assert rank_idx == 0
        assert not prefix
    else:
        child_rows = extract_rows_beneath(tax_rows, lineage, rank_idx + 1)
        for child_row in child_rows:
            child_d = make_child_d(tax_rows, lineage, child_row, rank_idx + 1)
            children.append(child_d)

    name = lineage[len(prefix) :].lstrip(";")

    child_d = dict(
        name=name,
        count=1000 * float(this_row["f_weighted_at_rank"]),
        score=this_row["fraction"],
        rank=this_row["rank"],
        children=children,
    )

    return child_d


def parse_csv_summary(tax_csv):
    # load in all tax rows. CTB: move into a class already!
    tax_rows = []
    with open(tax_csv, "r", newline="") as fp:
        r = csv.DictReader(fp)
        for row in r:
            lineage = row["lineage"]
            # eliminate all unclassified that are not top-level
            if lineage == "unclassified" and row["rank"] != "superkingdom":
                continue

            tax_rows.append((lineage, row))

    ###

    # find the top nodes/names
    top_names = []
    for k, row in tax_rows:
        if row["rank"] == ranks[0]:
            top_names.append((k, row))

    top_nodes = []
    for name, row in top_names:
        node_d = make_child_d(tax_rows, "", row, 0)
        top_nodes.append(node_d)

    return top_nodes


def parse_tax_annotate(tax_csv):
    # load in all tax rows. CTB: move into a class already!
    tax_rows = []
    with open(tax_csv, "r", newline="") as fp:
        r = csv.DictReader(fp)
        for row in r:
            tax_rows.append(row)

    ###

    rows_by_tax = defaultdict(list)
    name_col = 'match_name'
    if name_col not in tax_rows[0].keys():
        name_col = 'name'
    for row in tax_rows:
        lin = row["lineage"] + ';' + row[name_col]
        last = None
        while lin or last:
            rows_by_tax[lin].append(row)

            if ";" not in lin:
                break
            lin, last = lin.rsplit(";", 1)
            if not last:
                # @CTB handle
                continue

    # make nodes
    nodes_by_tax = {}
    for lin, rows in rows_by_tax.items():
        name = lin.rsplit(";")[-1]
        rank = ranks[lin.count(";")]
        count = 0.0
        score = 0.0
        for row in rows:
            count += float(row["f_unique_weighted"]) * 1000
            score += float(row["f_unique_to_query"])

        node = dict(name=name, rank=rank, count=count, score=score)
        nodes_by_tax[lin] = node

    # add children
    def is_child(lin1, lin2):
        if lin1 == lin2:
            return False

        len_lin1 = lin1.count(";")
        len_lin2 = lin2.count(";")
        if len_lin2 == len_lin1 + 1 and lin1 + ";" in lin2:
            return True
        return False

    for lin1, node in nodes_by_tax.items():
        children = []
        for lin2, node2 in nodes_by_tax.items():
            if is_child(lin1, lin2):
                children.append(node2)
        node["children"] = children

    top_nodes = []
    for lin, node in nodes_by_tax.items():
        if node["rank"] == "superkingdom":
            top_nodes.append(node)

    # calc unassigned...
    last_row = tax_rows[-1]
    total = int(last_row["total_weighted_hashes"])
    found = int(last_row["sum_weighted_found"])

    top_nodes.append(
        dict(
            name="unclassified",
            score=1,  # @CTB
            count=1000 - found / total * 1000,
            rank="superkingdom",
        )
    )

    return top_nodes


def strip_suffix(filename, endings):
    filename = os.path.basename(filename)

    for ending in endings:
        if filename.endswith(ending):
            filename = filename[:-len(ending)]
    return filename


def main():
    p = argparse.ArgumentParser()
    p.add_argument("tax_csv", help="input tax CSV, in sourmash csv_summary format")
    p.add_argument("-F", "--input-format", default="csv_summary")
    p.add_argument(
        "-o", "--output-html", required=True, help="output HTML file to this location."
    )
    p.add_argument("--save-json", help="output a JSON file of the taxonomy")
    p.add_argument("--check-tree", help="check that tree makes sense",
                   action="store_true")
    p.add_argument("--fail-on-error", help="fail if tree doesn't pass checks; implies --check-tree",
                   action="store_true")
    args = p.parse_args()

    # parse!
    top_nodes = None
    name = None
    if args.input_format == "csv_summary":
        top_nodes = parse_csv_summary(args.tax_csv)
        name = strip_suffix(args.tax_csv, [".csv", ".csv_summary"])
    elif args.input_format == "tax_annotate":
        top_nodes = parse_tax_annotate(args.tax_csv)
        name = strip_suffix(args.tax_csv, [".csv", ".with-lineages"])
    else:
        assert 0, f"unknown input format specified: {args.input_format}"

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
