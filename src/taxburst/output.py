import os.path
from jinja2 import Environment, PackageLoader, select_autoescape, StrictUndefined

env = Environment(
    loader=PackageLoader("taxburst"),
    autoescape=select_autoescape(),
    undefined=StrictUndefined,
)

# this one was standard in Krona but is no longer default in taxburst.
#    'score': 'display="Avg. confidence"',

basic_node_attributes = {
    "magnitude": "",
    "count": 'display="Count" dataAll="members"',
    "unassigned": 'display="Unassigned" dataNode="members"',
    "rank": 'display="Rank" mono="true"',
}


def generate_html(top_nodes, *, name=None, extra_attributes=None):
    template = env.get_template("krona.html")

    if extra_attributes is None:
        extra_attributes = {}
    else:
        extra_attributes = dict(extra_attributes)

    node_attributes = dict(basic_node_attributes)
    node_attributes.update(extra_attributes)

    fill = [make_node_xml(n, list(extra_attributes)) for n in top_nodes]
    fill = "\n".join(fill)

    # build top node
    if name is None:
        name = "all"

    count_sum = round(sum([float(n["count"]) for n in top_nodes]), 4)

    return template.render(
        nodes=fill, name=name, count_sum=count_sum, node_attributes=node_attributes
    )


# track total node count, for distinguishing purposes
node_count = 1


def make_node_xml(d, x, *, indent=0):
    "Turn a given node dict into a <node>. x is list of attributes to add."
    global node_count

    # any children?
    children = d.get("children", [])
    child_nodes = []
    if children:
        for dd in children:
            xml = make_node_xml(dd, x, indent=indent + 1)
            child_nodes.append(xml)

    # grab & format values
    name = d["name"]
    count = float(d["count"])
    rank = d["rank"]
    child_out = ""
    if child_nodes:
        child_out = "\n" + "\n".join(child_nodes)

    # indent nicely, 'cause why not
    spc = "  " * indent

    # add in extra attributes, if (1) list given and (2) node has them
    extra = ""
    for attr in x:
        val = d.get(attr)
        if val is not None:
            extra += f"{spc}    <{attr}><val>{val}</val></{attr}>\n"

    x = f"""\
{spc}<node name="{name}">
{spc}    <members><val>node{node_count}.members.0.js</val></members>
{spc}    <rank><val>{rank}</val></rank>
{spc}    <count><val>{count:.01f}</val></count>{child_out}
{extra}{spc}</node>"""
    # increment global node count
    node_count += 1

    return x
