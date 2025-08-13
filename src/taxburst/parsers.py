"""
Top level module for parsing input formats.

Please see the developer docs at docs/developer.md in the git repo for
guidance on writing a new parser.
"""

import csv
import os
from collections import defaultdict
import json


input_formats = [
    "csv_summary",
    "tax_annotate",
    "SingleM",
    "krona",
    "json",
]


def parse_file(filename, input_format):
    "Parse a variety of input formats. Top level function."
    top_nodes = None
    name = None
    xtra = None

    assert input_format in input_formats
    if input_format == "csv_summary":
        top_nodes = parse_csv_summary(filename)
        name = _strip_suffix(filename, [".csv", ".csv_summary"])
    elif input_format == "tax_annotate":
        top_nodes = parse_tax_annotate(filename)
        name = _strip_suffix(filename, [".csv", ".with-lineages"])
        xtra = {"abund": 'display="Est abund"'}
    elif input_format.lower() == "singlem":
        top_nodes = parse_SingleM(filename)
        name = _strip_suffix(filename, [".tsv", ".profile"])
    elif input_format.lower() == "krona":
        top_nodes = parse_krona(filename)
        name = _strip_suffix(filename, [".tsv", ".krona"])
    elif input_format.lower() == "json":
        with open(filename, "rb") as fp:
            top_nodes = json.load(fp)
        name = _strip_suffix(filename, [".json"])
    else:
        assert 0, f"unknown input format specified: {input_format}"

    return top_nodes, name, xtra


def _strip_suffix(filename, endings):
    "Remove endings if present, in order of list."
    filename = os.path.basename(filename)

    for ending in endings:
        if filename.endswith(ending):
            filename = filename[: -len(ending)]
    return filename


# common utility function...
def assign_children(nodes_by_tax):
    """
    Takes a dictionary { lin, node_dict }; returns top nodes with children
    properly assigned. Assumes lineages are semicolon-separated and
    unclassified/unassigned have been removed.
    """
    # assign children
    children_by_lin = defaultdict(list)
    top_nodes = []
    for lin, node in nodes_by_tax.items():
        assert lin
        if lin.count(";") == 0:  # top node, no parent.
            top_nodes.append(node)
            continue

        # pick off prefix => parent sublineage.
        parent_lin = lin.rsplit(";", 1)[0]
        assert parent_lin, f"'{lin}' has empty sublineage - this is not allowed!"

        # assign child to parent
        children_by_lin[parent_lin].append(node)

    for lin, node in nodes_by_tax.items():
        children = children_by_lin[lin]
        node["children"] = children

    # every lineage in the input dict should have an entry in the
    # children_by_lin dict.
    assert len(nodes_by_tax) == len(children_by_lin)

    return top_nodes


class GenericParser:
    """Generic parser for turning CSV/TSV into internal nodes dictionaries.

    For row-oriented formats, should only need to implement 'build()'.
    """

    default_ranks = [
        "superkingdom",
        "phylum",
        "class",
        "order",
        "family",
        "genus",
        "species",
        "strain",
        "genome",  # CTB: do we use this?
    ]

    def __init__(self, filename, *, sep=",", ranks=None):
        self.filename = filename
        self.sep = sep
        if ranks is None:
            ranks = self.default_ranks
        self.ranks = ranks

    def load_rows(self):
        with open(self.filename, "r", newline="") as fp:
            r = csv.DictReader(fp, delimiter=self.sep)
            rows = list(r)

        return rows

    def build(self):
        raise NotImplementedError


class Parse_SourmashCSVSummary(GenericParser):
    def build(self):
        rows = self.load_rows()

        # turn rows into list of (lineage, row) tuples
        tax_rows = []
        for row in rows:
            lineage = row["lineage"]
            # eliminate all unclassified that are not top-level
            if lineage == "unclassified" and row["rank"] != "superkingdom":
                continue

            tax_rows.append((lineage, row))

        # build nodes
        nodes_by_tax = {}
        for lin, row in tax_rows:
            name = lin.rsplit(";")[-1]
            rank = self.ranks[lin.count(";")]
            assert row["rank"] == rank

            node = dict(
                name=name,
                count=1000 * float(row["f_weighted_at_rank"]),
                rank=row["rank"],
                score=row["fraction"],
            )

            nodes_by_tax[lin] = node

        return assign_children(nodes_by_tax)


def parse_csv_summary(tax_csv):
    "Load csv_summary format from sourmash."
    pp = Parse_SourmashCSVSummary(tax_csv)
    return pp.build()


class Parse_SourmashTaxAnnotate(GenericParser):
    def build(self):
        # load in all tax rows.
        tax_rows = []
        rows = self.load_rows()

        rows_by_tax = defaultdict(list)
        name_col = "match_name"
        if name_col not in rows[0].keys():
            name_col = "name"

        for row in rows:
            # add genome onto lineage
            orig_lin = row["lineage"]
            if not orig_lin:
                print(f'IGNORING row with empty lineage: name={row["name"]}')
                continue
            orig_lin = orig_lin + ";" + row[name_col]

            lin = orig_lin
            first = True
            last = None
            while first or last:
                first = False
                assert lin
                rows_by_tax[lin].append(row)

                if ";" not in lin:
                    break
                lin, last = lin.rsplit(";", 1)
                if not last:
                    # CTB test!
                    raise Exception(
                        f"error!? missing taxonomic entry in row '{orig_lin}'; this is not handled by taxburst"
                    )

        # make nodes
        nodes_by_tax = {}
        for lin, rows in rows_by_tax.items():
            name = lin.rsplit(";")[-1]

            rank = self.ranks[lin.count(";")]
            count = 0.0
            for row in rows:
                count += int(row["n_unique_weighted_found"])

            node = dict(name=name, rank=rank, count=count)
            if rank == "genome" or rank == "strain":
                node["abund"] = row["median_abund"]

            nodes_by_tax[lin] = node

        top_nodes = assign_children(nodes_by_tax)

        # calc unassigned...
        last_row = rows[-1]
        total = int(last_row["total_weighted_hashes"])
        found = int(last_row["sum_weighted_found"])

        top_nodes.append(
            dict(
                name="unclassified",
                count=total - found,
                rank="superkingdom",
            )
        )

        return top_nodes


def parse_tax_annotate(tax_csv):
    "Load in 'tax annotate' format from sourmash tax annotate."
    pp = Parse_SourmashTaxAnnotate(tax_csv)
    return pp.build()


class Parse_SingleMProfile(GenericParser):
    def build(self):
        tax_rows = self.load_rows()

        rows_by_tax = defaultdict(list)
        for row in tax_rows:
            lin = row["taxonomy"]

            # every row starts with Root; remove!
            assert lin.startswith("Root; ")
            orig_lin = lin[len("Root; ") :]

            # create sublineages to root for every lineage
            lin = orig_lin
            first = True
            last = None
            while first or last:
                first = False
                rows_by_tax[lin].append(row)

                # no more lineages? break up.
                if ";" not in lin:
                    break
                lin, last = lin.rsplit(";", 1)
                last = last.strip()
                if not last:
                    # CTB test!
                    raise Exception(
                        f"error!? missing taxonomic entry in row '{orig_lin}'; this is not handled by taxburst"
                    )

        # make nodes containing information for each lineage entry
        nodes_by_tax = {}
        for lin, rows in rows_by_tax.items():
            name = lin.rsplit(";")[-1].strip()
            rank = self.ranks[lin.count(";")]
            count = 0.0
            for row in rows:
                count += float(row["coverage"]) * 1000

            node = dict(name=name, rank=rank, count=count)
            nodes_by_tax[lin] = node

        # assign children & find top nodes
        return assign_children(nodes_by_tax)


def parse_SingleM(singleM_tsv):
    "load in SingleM profile output format."
    pp = Parse_SingleMProfile(singleM_tsv, sep="\t")
    return pp.build()


class Parse_Krona(GenericParser):
    def build(self):
        tax_rows = self.load_rows()

        rows_by_tax = defaultdict(list)
        available_ranks = None
        for row in tax_rows:
            # initialize list of available ranks from file itself.
            if available_ranks is None:
                available_ranks = []
                for rank in self.ranks:
                    if rank not in row:
                        break
                    available_ranks.append(rank)

            # for each line, get values for each available rank
            get_ranks = list(reversed(available_ranks))
            lineage = []
            while get_ranks:
                rank = get_ranks.pop()
                lineage.append(row[rank])

            # special case unclassified: skip building sublineages
            if row[rank] == "unclassified":
                rows_by_tax["unclassified"].append(row)
                continue

            for i in range(0, len(lineage)):
                lin = ";".join(lineage[: i + 1])
                rows_by_tax[lin].append(row)

        # make nodes
        nodes_by_tax = {}
        for lin, rows in rows_by_tax.items():
            name = lin.rsplit(";")[-1].strip()
            rank = self.ranks[lin.count(";")]
            count = 0.0
            for row in rows:
                count += float(row["fraction"]) * 1000

            node = dict(name=name, rank=rank, count=count)
            nodes_by_tax[lin] = node

        return assign_children(nodes_by_tax)


def parse_krona(krona_tsv):
    "Load in krona output format"
    pp = Parse_Krona(krona_tsv, sep="\t")
    return pp.build()
