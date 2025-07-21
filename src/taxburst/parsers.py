"""
Top level module for parsing input formats.
"""
import csv
import os
from collections import defaultdict
import json

from .taxinfo import ranks


def parse_file(filename, input_format):
    "Parse a variety of input formats. Top level function."
    top_nodes = None
    name = None
    if input_format == "csv_summary":
        top_nodes = parse_csv_summary(filename)
        name = _strip_suffix(filename, [".csv", ".csv_summary"])
    elif input_format == "tax_annotate":
        top_nodes = parse_tax_annotate(filename)
        name = _strip_suffix(filename, [".csv", ".with-lineages"])
    elif input_format.lower() == "singlem":
        top_nodes = parse_SingleM(filename)
        name = _strip_suffix(filename, [".tsv", ".profile"])
    elif input_format.lower() == "json":
        with open(filename, "rb") as fp:
            top_nodes = json.load(fp)
        name = _strip_suffix(filename, [".json"])
    else:
        assert 0, f"unknown input format specified: {input_format}"

    return top_nodes, name


def _strip_suffix(filename, endings):
    "Remove endings if present, in order of list."
    filename = os.path.basename(filename)

    for ending in endings:
        if filename.endswith(ending):
            filename = filename[:-len(ending)]
    return filename


def _make_nodes_by_rank_d(nodes_by_tax):
    nodes_by_rank = defaultdict(list)
    for lin, node in nodes_by_tax.items():
        rank = node["rank"]
        nodes_by_rank[rank].append((lin, node))

    return nodes_by_rank


def parse_csv_summary(tax_csv):
    "Load csv_summary format from sourmash."
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
        node_d = _make_child_d(tax_rows, "", row, 0)
        top_nodes.append(node_d)

    return top_nodes


def _make_child_d(tax_rows, prefix, this_row, rank_idx):
    "Make child node dicts, recursively."
    lineage = this_row["lineage"]

    children = []

    # never descend into unclassified
    if lineage == "unclassified":
        assert rank_idx == 0
        assert not prefix
    else:
        child_rows = _extract_rows_beneath(tax_rows, lineage, rank_idx + 1)
        for child_row in child_rows:
            child_d = _make_child_d(tax_rows, lineage, child_row, rank_idx + 1)
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


def _extract_rows_beneath(tax_rows, prefix, rank_idx):
    "Extract rows beneath a node."
    # CTB speed up!

    # no more possible to extract!
    if rank_idx >= len(ranks):
        return []

    children = []
    prefix_str = prefix + ";"

    desired_rank = ranks[rank_idx]
    for lineage, val in tax_rows:
        if val["rank"] == desired_rank and lineage.startswith(prefix_str):
            children.append(val)

    return children


def parse_tax_annotate(tax_csv):
    "Load in 'tax annotate' format from sourmash tax annotate."
    # load in all tax rows.
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
        orig_lin = row["lineage"] + ';' + row[name_col]

        lin = orig_lin
        last = None
        while lin or last:
            rows_by_tax[lin].append(row)

            if ";" not in lin:
                break
            lin, last = lin.rsplit(";", 1)
            if not last:
                # CTB test!
                raise Exception(f"error!? missing taxonomic entry in row '{orig_lin}'; this is not handled by taxburst")

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

    nodes_by_rank = _make_nodes_by_rank_d(nodes_by_tax)

    # CTB: speed me up.
    for parent_rank_i in range(len(ranks)):
        parent_rank = ranks[parent_rank_i]
        child_rank_i = parent_rank_i + 1
        if child_rank_i >= len(ranks):
            continue
        child_rank = ranks[child_rank_i]

        for (lin1, node) in nodes_by_rank[parent_rank]:
            children = []
            for (lin2, node2) in nodes_by_rank[child_rank]:
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
            score=1,
            # count is just ...remaining stuff :)
            count=1000 - found / total * 1000,
            rank="superkingdom",
        )
    )

    return top_nodes


def parse_SingleM(singleM_tsv):
    "load in SingleM profile output format."
    tax_rows = []
    with open(singleM_tsv, "r", newline="") as fp:
        r = csv.DictReader(fp, delimiter='\t')
        for row in r:
            tax_rows.append(row)

    ###

    rows_by_tax = defaultdict(list)
    for row in tax_rows:
        lin = row["taxonomy"]

        # every row starts with Root; remove!
        assert lin.startswith('Root; ')
        orig_lin = lin[len('Root; '):]

        lin = orig_lin
        last = None
        while lin or last:
            rows_by_tax[lin].append(row)

            # no more lineages? break up.
            if ";" not in lin:
                break
            lin, last = lin.rsplit(";", 1)
            last = last.strip()
            if not last:
                # CTB test!
                raise Exception(f"error!? missing taxonomic entry in row '{orig_lin}'; this is not handled by taxburst")

    # make nodes
    nodes_by_tax = {}
    for lin, rows in rows_by_tax.items():
        name = lin.rsplit(";")[-1].strip()
        rank = ranks[lin.count(";")]
        count = 0.0
        score = 0.0
        for row in rows:
            count += float(row["coverage"]) * 1000
            score += float(1.0)

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

    # assign children. CTB consider speeding up!
    for lin1, node in nodes_by_tax.items():
        children = []
        for lin2, node2 in nodes_by_tax.items():
            if is_child(lin1, lin2):
                children.append(node2)
        node["children"] = children

    # pull out all the superkingdom nodes as top_nodes
    top_nodes = []
    for lin, node in nodes_by_tax.items():
        if node["rank"] == "superkingdom":
            top_nodes.append(node)

    return top_nodes
