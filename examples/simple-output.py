import taxburst

# define nodes structure:
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

# build XHTML:
content = taxburst.generate_html(nodes)

# save to HTML:
print("writing content to output.html")
with open("output.html", "wt") as fp:
    fp.write(content)
