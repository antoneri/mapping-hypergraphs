from collections import defaultdict
from functools import partial
from itertools import product

from infomap import Infomap

from hypergraph.io import read, parse
from hypergraph.transition import p


def each_node_pair(edges, nodes, p):
    for e1, e2 in product(edges, edges):
        for u_id, v_id in product(e1.nodes, e2.nodes):
            if u_id == v_id:
                continue

            u = next(node for node in nodes if node.id == u_id)
            v = next(node for node in nodes if node.id == v_id)

            w = p(u, e1, v, e2)

            if w < 1e-10:
                continue

            yield e1, u, e2, v, w


def create_multilayer_network(node_pairs):
    intra = []
    inter = []

    for e1, u, e2, v, w in node_pairs:
        if e1 == e2:
            links = intra
        else:
            links = inter

        # layer_id node_id layer_id node_id weight
        links.append((e1.id, u.id, e2.id, v.id, w))

    return [((e1, u), (e2, v), w)
            for links in (intra, inter)
            for e1, u, e2, v, w in sorted(links, key=lambda link: link[0])]


def create_state_network(node_pairs):
    state_ids = defaultdict(lambda: len(state_ids) + 1)

    states = set()
    links = []

    for e1, u, e2, v, w in node_pairs:
        source_id = state_ids[(e1.id, u.id)]
        target_id = state_ids[(e2.id, v.id)]

        states.add((source_id, u.id))
        states.add((target_id, v.id))

        links.append((source_id, target_id, w))

    return states, links


def main(filename):
    with open(filename, "r") as fp:
        nodes, edges, weights = parse(read(fp.readlines()))

    P = partial(p, edges, weights, shifted=True)
    node_pairs = list(each_node_pair(edges, nodes, P))

    links = create_multilayer_network(node_pairs)

    im = Infomap("--directed -N5")
    im.set_names(nodes)
    im.add_multilayer_links(links)
    im.run()
    im.write_flow_tree("multilayer.ftree", states=True)

    states, links = create_state_network(node_pairs)

    im = Infomap("--directed -N5")
    im.set_names(nodes)
    im.add_state_nodes(states)
    im.add_links(links)
    im.run()
    im.write_flow_tree("states.ftree", states=True)


if __name__ == "__main__":
    main("data.txt")
