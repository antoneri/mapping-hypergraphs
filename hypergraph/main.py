from hypergraph import bipartite as bipartite_, multilayer as multilayer_
from hypergraph.io import read, parse
from hypergraph.links import create_links


def main(file,
         outdir,
         network=False,
         no_infomap=False,
         shifted=False,
         multilayer=False,
         multilayer_self_links=False,
         bipartite=False,
         bipartite_non_backtracking=False):
    print("[main] starting...")

    print("[main] ", end="")
    args = locals()
    for key, value in args.items():
        if key == "file":
            value = value.name
        if value:
            print("{}={} ".format(key, value), end="")
    print()

    nodes, edges, weights = parse(read(file.readlines()))

    links = create_links(edges, weights, multilayer_self_links, shifted)

    if multilayer or multilayer_self_links:
        multilayer_.run("multilayer", outdir, network, no_infomap, links, nodes, multilayer_self_links, shifted)

    if bipartite or bipartite_non_backtracking:
        bipartite_.run("bipartite", outdir, network, no_infomap, links, nodes, edges, bipartite_non_backtracking)
