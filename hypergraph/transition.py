from collections import defaultdict
from typing import Iterable, Set, Optional, Callable

from hypergraph.network import Node, HyperEdge, Gamma


def E(edges: Iterable[HyperEdge]) -> Callable[[Node, Optional[Node]], Set[int]]:
    """
    Set of hyperedges incident to vertex v.

    .. math:: E(v) = { e \in E : v in e }

    Set of hyperedges incident to both vertices u and v.

    .. math:: E(u, v) = { e \in E : u \in e, v \in e }
    """
    edges_ = defaultdict(set)

    for edge, nodes, _ in edges:
        for node in nodes:
            edges_[node.id].add(edge)

    edges_ = dict(edges_)

    def inner(u: Node, v: Optional[Node] = None) -> Set[int]:
        if v:
            return edges_[u.id] & edges_[v.id]

        return edges_[u.id]

    return inner


def d(edges: Iterable[HyperEdge]) -> Callable[[Node], float]:
    """
    Degree of vertex v.

    .. math:: d(v) = \sum_{e \in E(v)} \omega(e)
    """
    E_ = E(edges)

    def inner(v: Node) -> float:
        return sum(omega for edge, _, omega in edges
                   if edge in E_(v))

    return inner


def delta(weights: Iterable[Gamma]) -> Callable[[HyperEdge], float]:
    """
    Degree of hyperedge e.

    .. math:: \delta(e) \sum_{v \in e} \gamma_e(v)
    """
    delta_ = defaultdict(float)

    for edge, _, gamma in weights:
        delta_[edge] += gamma

    delta_ = dict(delta_)

    def inner(e: HyperEdge) -> float:
        return delta_[e.id]

    return inner


def gamma(weights: Iterable[Gamma]) -> Callable[[HyperEdge, Node], float]:
    """
    Edge-(in)dependent vertex weight.

    .. math:: \gamma_e(v)
    """
    gamma_ = {(edge, node.id): gamma_
              for edge, node, gamma_ in weights}

    def inner(e: HyperEdge, v: Node) -> float:
        return gamma_[e.id, v.id]

    return inner


def pi(edges: Iterable[HyperEdge], weights: Iterable[Gamma]):
    E_ = E(edges)
    gamma_ = gamma(weights)
    edges_ = {edge.id: edge for edge in edges}

    def inner(u: Node) -> float:
        E_u = {edges_[edge_id] for edge_id in E_(u)}

        return sum(e.omega * gamma_(e, u)
                   for e in E_u)

    return inner


def pi_alpha(weights: Iterable[Gamma]) -> Callable[[HyperEdge, Node], float]:
    gamma_ = gamma(weights)

    def inner(e: HyperEdge, u: Node) -> float:
        if u not in e.nodes:
            return 0.0

        return e.omega * gamma_(e, u)

    return inner


def P(edges: Iterable[HyperEdge], weights: Iterable[Gamma]) -> Callable[[Node, Node, bool], float]:
    print("[transition] pre-calculating probabilities...")
    gamma_ = gamma(weights)
    delta_ = delta(weights)
    d_ = d(edges)
    E_ = E(edges)
    edges_ = {edge.id: edge for edge in edges}

    def inner(u: Node, v: Node, self_links: bool = False) -> float:
        E_u_v = (edges_[edge_id] for edge_id in E_(u, v))

        delta_e = lambda e: delta_(e) if self_links else delta_(e) - gamma_(e, u)

        return sum(e.omega / d_(u) * gamma_(e, v) / delta_e(e)
                   for e in E_u_v)

    return inner


def w(edges: Iterable[HyperEdge], weights: Iterable[Gamma]) -> Callable[[Node, Node, bool], float]:
    """
    Weight for going between vertex u to v in a unipartite representation
    of a hypergraph with edge-independent vertex weights.

    Assumes edge-independent vertex weights.

    .. math::

        w_{u,v} = \sum_{e \in E(u,v) } \frac{ \omega(e) \gamma(u) \gamma(v) }{ \delta(e) }
    """
    print("[transition] pre-calculating probabilities...")
    gamma_ = gamma(weights)
    delta_ = delta(weights)
    E_ = E(edges)
    edges_ = {edge.id: edge for edge in edges}

    def inner(u: Node, v: Node, self_links: bool = False) -> float:
        E_u_v = (edges_[edge_id] for edge_id in E_(u, v))

        delta_e = lambda e: delta_(e) if self_links else delta_(e) - gamma_(e, u)

        return sum(e.omega * gamma_(e, u) * gamma_(e, v) / delta_e(e)
                   for e in E_u_v)

    return inner
