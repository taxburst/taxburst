import os.path
from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader("taxburst"),
    autoescape=select_autoescape()
)

dirname = os.path.dirname(__file__)
templatedir = os.path.join(dirname, "./templates")


def generate_html(top_nodes, *, name=None):
    template = env.get_template("krona.html")

    fill2 = [make_node_xml(n) for n in top_nodes]

    # build top node
    if name is None:
        name = "all"

    count_sum = round(sum([float(n["count"]) for n in top_nodes]), 4)
    fill2 = "\n".join(fill2)

    return template.render(nodes=fill2,
                           name=name,
                           count_sum=count_sum)


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
