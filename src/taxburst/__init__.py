#! /usr/bin/env python
import sys
import csv
import pprint
import argparse
import os.path

dirname = os.path.dirname(__file__)
templatedir = os.path.join(dirname, './templates')

ranks = ['superkingdom',
         'phylum',
         'class',
         'order',
         'family',
         'genus',
         'species',
         'strain']


nodes = [
    { 'name': 'A',
      'count': 5,
      'score': 0.831,
      'rank': 'Phylum',
      'children': [
          { 'name': 'B', 'count': 3, 'score': 0.2, 'rank': 'Class' },
          { 'name': 'C', 'count': 1, 'score': 0.1, 'rank': 'Class' }
          ]
     },
]


node_count = 1
def make_node_xml(d, indent=0):
    global node_count
    output = []
    children = d.get('children', [])

    child_nodes = []
    if children:
        child_nodes = [ make_node_xml(dd, indent=indent+1) for dd in children ]

    name = d['name']
    count = float(d['count'])
    score = float(d['score'])
    rank = d['rank']
    child_out = ""
    if child_nodes:
        child_out = "\n" + "\n".join(child_nodes)
    # indent? @CTB

    spc = "  "*indent

    x = f"""\
{spc}<node name="{name}">
{spc}    <rank><val>{rank}</val></rank>
{spc}    <count><val>{count:.01f}</val></count>
{spc}    <score><val>{score:.03f}</val></score>{child_out}
{spc}    <members><val>node{node_count}.members.0.js</val></members>
{spc}</node>
"""
    node_count += 1

    return x

def extract_rows_beneath(tax_rows, prefix, rank_idx):
    children = []
    prefix_str = prefix + ';'
    desired_lin_count = prefix_str.count(';')
    if rank_idx >= len(ranks):
        return []

    desired_rank = ranks[rank_idx]
    for lineage, val in tax_rows:
        if val['rank'] == desired_rank:
            if lineage == 'unclassified' or \
               (lineage.startswith(prefix_str) and lineage.count(';') == desired_lin_count):
                children.append(val)

    return children

def make_child_d(tax_rows, prefix, this_row, rank_idx):
    lineage = this_row['lineage']

    children = []
    if lineage != 'unclassified':
        child_rows = extract_rows_beneath(tax_rows, lineage, rank_idx + 1)
        for child_row in child_rows:
            child_d = make_child_d(tax_rows, lineage, child_row, rank_idx + 1)
            children.append(child_d)

    name = lineage
    if name != 'unclassified':
        name = lineage[len(prefix) + 1:]
    else:
        assert rank_idx == 0
        rank = ranks[rank_idx]
        name = f'unclassified'
    
    child_d = dict(name=name,
                   count=1000*float(this_row['f_weighted_at_rank']),
                   score=this_row['fraction'],
                   rank=this_row['rank'],
                   children=children)
    
    return child_d

def main():
    p = argparse.ArgumentParser()
    p.add_argument('tax_csv', help='input tax CSV, in sourmash csv_summary format')
    p.add_argument('-o', '--output-html', required=True,
                   help="output HTML file to this location.")
    args = p.parse_args()

    outer_template = os.path.join(templatedir, 'krona-template.html')
    inner_template = os.path.join(templatedir, 'krona-fill.html')

    with open(outer_template, 'rt') as fp:
        template = fp.read()

    with open(inner_template, 'rt') as fp:
        fill = fp.read()

    #fill2 = [ make_node_xml(n) for n in nodes ]
    #fill2 = "\n".join(fill2)

    tax_rows = []
    with open(args.tax_csv, 'r', newline='') as fp:
        r = csv.DictReader(fp)
        for row in r:
            lineage = row['lineage']
            if lineage == 'unclassified' and row['rank'] != 'superkingdom':
                continue

            tax_rows.append((lineage, row))

    ###

    top_names = []
    for k, row in tax_rows:
        if k.count(';') == 0 and row['rank'] == 'superkingdom':
            top_names.append((k, row))

    top_nodes = []
    for name, row in top_names:
        child_rows = extract_rows_beneath(tax_rows, name, 1)
        children = []
        if name != 'unclassified':
            for child_row in child_rows:
                child_d = make_child_d(tax_rows, name, child_row, 1)
                children.append(child_d)

        node_d = dict(name=row['lineage'],
                      count=1000*float(row['f_weighted_at_rank']),
                      score=row['fraction'],
                      rank=row['rank'],
                      children=children)
        top_nodes.append(node_d)

    fill2 = [ make_node_xml(n) for n in top_nodes ]
    count_sum = sum([ float(n['count']) for n in top_nodes ])
    fill2 = "\n".join(fill2)
    fill2 = f'<node name="all">\n<count><val>{count_sum}</val></count>\n{fill2}\n</node>'

    fill = fill.replace('{{ nodes }}', fill2)
    template = template.replace('{{ krona }}', fill)

    with open(args.output_html, 'wt') as fp:
        fp.write(template)
    print(f"wrote output to '{args.output_html}'")
