#! /usr/bin/env python
import sys
import csv
import pprint
import argparse
import os.path

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
]


# an example nodes dictionary, just for grins
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
    if lineage == 'unclassified':
        assert rank_idx == 0
        assert not prefix
    else:
        child_rows = extract_rows_beneath(tax_rows, lineage, rank_idx + 1)
        for child_row in child_rows:
            child_d = make_child_d(tax_rows, lineage, child_row, rank_idx + 1)
            children.append(child_d)

    name = lineage[len(prefix):].lstrip(';')

    child_d = dict(
        name=name,
        count=1000 * float(this_row["f_weighted_at_rank"]),
        score=this_row["fraction"],
        rank=this_row["rank"],
        children=children,
    )

    return child_d


def main():
    p = argparse.ArgumentParser()
    p.add_argument("tax_csv", help="input tax CSV, in sourmash csv_summary format")
    p.add_argument(
        "-o", "--output-html", required=True, help="output HTML file to this location."
    )
    args = p.parse_args()

    # find templates
    outer_template = os.path.join(templatedir, "krona-template.html")
    inner_template = os.path.join(templatedir, "krona-fill.html")

    # read templates
    with open(outer_template, "rt") as fp:
        template = fp.read()

    with open(inner_template, "rt") as fp:
        fill = fp.read()

    # unused example :)
    # fill2 = [ make_node_xml(n) for n in nodes ]
    # fill2 = "\n".join(fill2)

    # load in all tax rows. CTB: move into a class already!
    tax_rows = []
    with open(args.tax_csv, "r", newline="") as fp:
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

    # build XHTML
    fill2 = [make_node_xml(n) for n in top_nodes]

    # build top node
    count_sum = sum([float(n["count"]) for n in top_nodes])
    fill2 = "\n".join(fill2)
    fill2 = (
        f'<node name="all">\n<count><val>{count_sum}</val></count>\n{fill2}\n</node>'
    )

    # fill in template
    fill = fill.replace("{{ nodes }}", fill2)
    template = template.replace("{{ krona }}", fill)

    # output!!
    with open(args.output_html, "wt") as fp:
        fp.write(template)

    print(f"wrote output to '{args.output_html}'")
