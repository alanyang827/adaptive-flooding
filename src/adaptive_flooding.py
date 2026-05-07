"""Adaptive flooding / delayed-decision controlled broadcast over a multi-hop wireless network."""

import argparse
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pywisim import EventLoop, Node, WirelessNetwork


class FloodNode(Node):
    DECISION_DELAY = 0.45
    JITTER = 0.10

    def __init__(self, nid):
        super().__init__(nid)
        self.seen = set()
        self.recv_count = defaultdict(int)   # origin -> number of receptions
        self.forwarded = set()               # origin -> already forwarded?
        self.pending = {}                    # origin -> buffered msg
        self.forward_count = 0

    def _forward_prob(self, origin):
        deg = len(self.net.neighbors(self.nid))
        count = self.recv_count[origin]

        # Sparse regions need more help; dense regions need more suppression.
        if deg <= 2:
            base = 0.98
        elif deg <= 4:
            base = 0.82
        else:
            base = 0.62

        # Do not over-suppress the first two copies.
        if count <= 2:
            p = base
        else:
            p = base * (0.75 ** (count - 2))

        return max(0.20, p)

    def _decide_forward(self, origin):
        if origin in self.forwarded:
            self.pending.pop(origin, None)
            return

        msg = self.pending.pop(origin, None)
        if msg is None:
            return

        _, _, payload = msg
        count = self.recv_count[origin]
        p = self._forward_prob(origin)

        # For the first two receptions, strongly favor forwarding to preserve reachability.
        if count <= 2:
            p = max(p, 0.99)

        if random.random() < p:
            self.forwarded.add(origin)
            self.forward_count += 1
            self.net.log(
                f"{self.nid} forwards '{payload}' from {origin} "
                f"after window (count={count}, p={p:.2f})"
            )
            self.broadcast(msg)
        else:
            self.net.log(
                f"{self.nid} suppresses '{payload}' from {origin} "
                f"after window (count={count}, p={p:.2f})"
            )

    def on_receive(self, msg, sender):
        _, origin, payload = msg

        self.recv_count[origin] += 1
        count = self.recv_count[origin]

        if origin not in self.seen:
            self.seen.add(origin)
            self.net.log(
                f"{self.nid} first got '{payload}' from {origin} (via {sender})"
            )

        if origin in self.forwarded:
            return

        # First time we see this origin: buffer it and schedule a decision.
        if origin not in self.pending:
            self.pending[origin] = msg
            delay = self.DECISION_DELAY + random.uniform(0.0, self.JITTER)
            self.net.log(
                f"{self.nid} buffers '{payload}' from {origin} "
                f"(via {sender}); decide in {delay:.2f}s, count={count}"
            )
            self.schedule(delay, self._decide_forward, origin)
        else:
            self.net.log(
                f"{self.nid} hears duplicate '{payload}' from {origin} "
                f"(via {sender}), count={count}"
            )

    def flood(self, payload):
        self.seen.add(self.nid)
        self.forwarded.add(self.nid)
        self.net.log(f"{self.nid} starts adaptive flood: '{payload}'")
        self.broadcast(("FLOOD", self.nid, payload))
        self.forward_count += 1


def build_line_topology(net):
    for nid, x, y in [("A", 0, 0), ("B", 1, 0), ("C", 2, 0), ("D", 3, 0), ("E", 4, 0)]:
        net.add_node(FloodNode(nid), x, y)


def build_random_topology(net, n=30, area_size=10, seed=42):
    rng = random.Random(seed)
    for i in range(n):
        x = rng.uniform(0, area_size)
        y = rng.uniform(0, area_size)
        net.add_node(FloodNode(str(i)), x, y)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topology", choices=["line", "random"], default="random")
    parser.add_argument("--nodes", type=int, default=30)
    parser.add_argument("--area", type=float, default=10.0)
    parser.add_argument("--tx-range", type=float, default=2.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--source", type=str, default="0")
    parser.add_argument("--until", type=float, default=20.0)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    random.seed(args.seed)

    loop = EventLoop()
    net = WirelessNetwork(loop, tx_range=args.tx_range, seed=args.seed, verbose=args.verbose)

    if args.topology == "line":
        build_line_topology(net)
        source = "A"
    else:
        build_random_topology(net, n=args.nodes, area_size=args.area, seed=args.seed)
        source = args.source if args.source in net.nodes else sorted(net.nodes)[0]

    print("Topology:", {n: net.neighbors(n) for n in sorted(net.nodes)})

    loop.schedule(1.0, net.nodes[source].flood, "hello!")
    loop.run(until=args.until)

    delivered = [n for n in sorted(net.nodes) if len(net.nodes[n].seen) > 0]
    total_forwards = sum(net.nodes[n].forward_count for n in net.nodes)
    total_receptions = sum(sum(node.recv_count.values()) for node in net.nodes.values())

    print("\nDelivered to:", delivered)
    print(f"Delivery ratio: {len(delivered)}/{len(net.nodes)}")
    print(f"Total forwards: {total_forwards}")
    print(f"Total receptions: {total_receptions}")

    print("\nPer-node stats:")
    for nid in sorted(net.nodes):
        node = net.nodes[nid]
        print(
            f"  Node {nid}: "
            f"seen_origins={len(node.seen)}, "
            f"forwards={node.forward_count}, "
            f"recv_events={sum(node.recv_count.values())}"
        )


if __name__ == "__main__":
    main()