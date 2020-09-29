from typing import Iterable

from hypergraph.types import Node, HyperEdge, Weight


def E_v(v: Node, edges: Iterable[HyperEdge]):
    return {edge.id for edge in edges
            if v.id in edge.nodes}


def E_uv(v: Node, u: Node, edges: Iterable[HyperEdge]):
    return {edge.id for edge in edges
            if {u.id, v.id} <= edge.nodes}


def d(v: Node, edges: Iterable[HyperEdge]):
    E = lambda v: E_v(v, edges)

    return sum(edge.omega for edge in edges
               if edge.id in E(v))


def delta(e: HyperEdge, weights: Iterable[Weight]):
    return sum(weight.gamma for weight in weights
               if weight.edge == e.id)


def gamma(e: HyperEdge, v: Node, weights: Iterable[Weight]):
    return next((weight.gamma for weight in weights
                 if weight.edge == e.id
                 and weight.node == v.id), 0)


def p(u: Node, e1: HyperEdge,
      v: Node, e2: HyperEdge,
      weights: Iterable[Weight],
      edges: Iterable[HyperEdge]):
    gamma_ev = lambda e, v: gamma(e, v, weights)
    delta_e = lambda e: delta(e, weights)
    d_v = lambda v: d(v, edges)
    omega = lambda e: e.omega

    step_1 = gamma_ev(e1, v) / (delta_e(e1) - gamma_ev(e1, u))
    step_2 = omega(e2) / d_v(v)

    return step_1 * step_2


if __name__ == "__main__":
    nodes = [Node(id=1, name='a'),
             Node(id=2, name='b'),
             Node(id=3, name='c'),
             Node(id=4, name='d'),
             Node(id=5, name='f')]
    edges = [HyperEdge(id=1, nodes={1, 2, 3}, omega=10),
             HyperEdge(id=2, nodes={3, 4, 5}, omega=20)]
    weights = [Weight(edge=1, node=1, gamma=1),
               Weight(edge=1, node=2, gamma=1),
               Weight(edge=1, node=3, gamma=2),
               Weight(edge=2, node=3, gamma=1),
               Weight(edge=2, node=4, gamma=1),
               Weight(edge=2, node=5, gamma=2)]

    print("E")
    print(E_v(nodes[1], edges))
    print(E_v(nodes[2], edges))
    print(E_uv(nodes[2], nodes[3], edges))

    print("d")
    print(d(nodes[1], edges))
    print(d(nodes[2], edges))
    print(d(nodes[3], edges))

    print("delta")
    print(delta(edges[0], weights))
    print(delta(edges[1], weights))

    print("gamma")
    print(gamma(edges[0], nodes[0], weights))
    print(gamma(edges[0], nodes[2], weights))

    print("P")
    u = nodes[1]
    e1 = edges[0]
    v = nodes[2]
    e2 = edges[1]
    print(p(u, e1, v, e2, weights, edges))
