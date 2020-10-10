from os import path
from typing import Callable, Optional

from infomap import Infomap

from hypergraph import representation
from hypergraph.io import read, parse
from hypergraph.network import Network

InfomapCallback = Callable[[Infomap], None]

_DEFAULT_SEED = 123
_DEFAULT_TELEPORTATION_PROB = 0.15


def run_infomap(basename: str,
                outdir: str,
                callback: InfomapCallback,
                args: Optional[str] = None,
                directed: bool = True,
                self_links: bool = False,
                no_infomap: bool = False,
                two_level: bool = False,
                seed: int = _DEFAULT_SEED,
                teleportation_probability: float = _DEFAULT_TELEPORTATION_PROB,
                **kwargs):
    if no_infomap:
        return

    filename = basename + "_seed_{}".format(seed) if seed != _DEFAULT_SEED else ""

    default_args = "--num-trials 10 --silent"
    default_args += " --directed" if directed else ""
    default_args += " --include-self-links" if self_links else ""
    default_args += " --two-level" if two_level else ""
    default_args += " --seed {}".format(seed)
    default_args += " --teleportation-probability {}".format(teleportation_probability)
    default_args += " --out-name {} ".format(filename)
    default_args += outdir

    print("[infomap] running infomap...")
    im = Infomap("{} {}".format(default_args, args if args else ""))
    callback(im)
    im.run()
    im.write_flow_tree(path.join(outdir, filename) + ".ftree", states=True)
    print("[infomap] codelength {}".format(im.codelength))
    print("[infomap] num top modules {}".format(im.num_non_trivial_top_modules))


def run(file,
        outdir="output",
        outfile=None,
        multilayer=False,
        bipartite=False,
        bipartite_non_backtracking=False,
        clique_graph=False,
        directed_clique=False,
        self_links=False,
        write_network=False,
        **kwargs) -> Optional[Network]:
    hypergraph = parse(read(file.readlines()))

    if multilayer:
        network = representation.multilayer(hypergraph, self_links)

        basename = outfile if outfile else "multilayer"
        basename += "_self_links" if self_links else ""

        def set_network(im: Infomap):
            im.set_names(network.nodes)
            im.add_multilayer_links(network.links)

    elif bipartite or bipartite_non_backtracking:
        network = representation.bipartite(hypergraph, bipartite_non_backtracking)

        basename = outfile if outfile else "bipartite"
        basename += "_non_backtracking" if bipartite_non_backtracking else ""

        def set_network(im: Infomap):
            im.set_names(network.nodes)
            im.set_names(network.features)
            # FIXME Fixed in Infomap 1.2.0
            im.bipartite_start_id = network.bipartite_start_id - 1
            if network.states:
                im.add_state_nodes(network.states)
            im.add_links(network.links)

    elif clique_graph or directed_clique:
        network = representation.clique(hypergraph, directed_clique, self_links)

        basename = outfile if outfile else "clique"
        basename += "_directed" if directed_clique else ""
        basename += "_self_links" if self_links else ""

        def set_network(im: Infomap):
            im.add_nodes(network.nodes)
            im.add_links(network.links)

    else:
        return

    if write_network:
        network.write(path.join(outdir, basename) + ".net")

    run_infomap(basename,
                outdir,
                set_network,
                directed=not clique_graph,
                self_links=self_links,
                **kwargs)

    return network


def main():
    from argparse import ArgumentParser, FileType, RawDescriptionHelpFormatter
    from textwrap import dedent
    import sys

    description = dedent("""
    Create maps from hypergraps with edge-dependent vertex weights.

    First, represent the hypergraph as any of
    the formats specified under "representation".

    Then, Infomap finds the community structure in the network
    representation and outputs the result in "outdir".

    For hypergraph input format, see: data/example.txt
    """)

    # noinspection PyTypeChecker
    parser = ArgumentParser(prog="hypergraph",
                            description=description,
                            formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument("file", type=FileType("r"), default=sys.stdin, help="the hypergraph file")
    parser.add_argument("outdir", nargs="?", default="output", help="directory to write output to")

    parser.add_argument("-w", "--write-network", action="store_true", help="write network representation to file")
    parser.add_argument("-k", "--self-links", action="store_true",
                        help="include self links (does not apply to bipartite representations)")
    parser.add_argument("-2", "--two-level", action="store_true",
                        help="only search for two-level partitions")
    parser.add_argument("--no-infomap", action="store_true", help="do not run Infomap")
    parser.add_argument("-s", "--seed", default=_DEFAULT_SEED, type=int, help="random seed")
    parser.add_argument("-p", "--teleportation-probability", default=_DEFAULT_TELEPORTATION_PROB,
                        type=float, help="probability to teleport in each step")
    parser.add_argument("-o", "--outfile")

    output = parser.add_argument_group("representation")
    options = output.add_mutually_exclusive_group(required=True)
    options.add_argument("-m", "--multilayer", action="store_true")
    options.add_argument("-b", "--bipartite", action="store_true")
    options.add_argument("-B", "--bipartite-non-backtracking", action="store_true")
    options.add_argument("-c", "--clique-graph", action="store_true")
    options.add_argument("-C", "--directed-clique", action="store_true")

    args = parser.parse_args()

    run(**vars(args))


if __name__ == "__main__":
    main()
