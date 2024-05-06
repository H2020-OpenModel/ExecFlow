from __future__ import annotations

import sys

from aiida import load_profile
from aiida.orm import load_node
from aiida.tools.visualization import Graph

load_profile()


def graph_node(node):
    graph = Graph(graph_attr={"size": "8,8!", "rankdir": "LR"})
    graph.recurse_descendants(
        node.uuid,
        origin_style=None,
        include_process_inputs=True,
        annotate_links="both",
        # link_types=('input_work', 'input_calc', 'call_calc', 'create')
    )
    graph.graphviz.render("out")


if __name__ == "__main__":
    graph_node(load_node(sys.argv[1]))
