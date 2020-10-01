from typing import Iterable, Sequence

from infomap import Infomap

from hypergraph.io import Node, HyperEdge
from hypergraph.links import Link


def create_network(links: Iterable[Link], nodes: Sequence[Node], edges: Sequence[HyperEdge]):
    print("[bipartite] creating bipartite... ", end="")
    bipartite_start_id = max(node.id for node in nodes) + 1

    features = [Node(bipartite_start_id + i, "Hyperedge {}".format(i + 1))
                for i in range(len(edges))]

    edge_to_feature_id = {edge.id: bipartite_start_id + i
                          for i, edge in enumerate(edges)}

    links_ = []

    for e1, u, e2, v, w in links:
        feature_id = edge_to_feature_id[e2.id]

        links_.append((u.id, feature_id, w))
        links_.append((feature_id, v.id, w))

    print("done")
    return features, links_


def run_infomap(filename, links, nodes, features):
    bipartite_start_id = min(node.id for node in features)

    print("[infomap] running infomap on bipartite network... ", end="")
    im = Infomap("-d -N5 --silent")
    im.set_names(nodes)
    im.bipartite_start_id = bipartite_start_id - 1  # FIXME Fixed in Infomap 1.2.0
    im.add_nodes(features)
    im.add_links(links)
    im.run()
    im.write_flow_tree(filename)
    print("done")
    print("[infomap] codelength {}".format(im.codelength))
    print("[infomap] num top modules {}".format(im.num_non_trivial_top_modules))


def run(filename, links: Iterable[Link], nodes: Sequence[Node], edges: Sequence[HyperEdge]):
    features, bipartite_links = create_network(links, nodes, edges)
    run_infomap(filename, bipartite_links, nodes, features)
