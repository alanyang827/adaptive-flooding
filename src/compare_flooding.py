"""Compare baseline flooding vs delayed-decision adaptive flooding."""

import random
import statistics as stats
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pywisim import EventLoop, Node, WirelessNetwork


class BaseFloodNode(Node):
    def __init__(self, nid):
        super().__init__(nid)
        self.seen = set()
        self.recv_count = defaultdict(int)
        self.forwarded = set()
        self.forward_count = 0

    def flood(self, payload):
        self.seen.add(self.nid)
        self.forwarded.add(self.nid)
        self.forward_count += 1
        self.broadcast(("FLOOD", self.nid, payload))


class BaselineNode(BaseFloodNode):
    def on_receive(self, msg, sender):
        _, origin, payload = msg

        self.recv_count[origin] += 1

        if origin not in self.seen:
            self.seen.add(origin)

        if origin in self.forwarded:
            return

        self.forwarded.add(origin)
        self.forward_count += 1
        self.broadcast(msg)


class AdaptiveNode(BaseFloodNode):
    DECISION_DELAY = 0.45
    JITTER = 0.10

    def __init__(self, nid):
        super().__init__(nid)
        self.pending = {}  # origin -> msg

    def _forward_prob(self, origin):
        deg = len(self.net.neighbors(self.nid))
        count = self.recv_count[origin]

        # Sparse regions need more help; dense regions produce more redundancy
        if deg <= 2:
            base = 0.98
        elif deg <= 4:
            base = 0.82
        else:
            base = 0.62

        # Do not suppress too aggressively for first two receptions
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

        # For first two receptions, favor forwarding to ensure coverage
        if count <= 2:
            p = max(p, 0.99)

        if random.random() < p:
            self.forwarded.add(origin)
            self.forward_count += 1
            self.broadcast(msg)

    def on_receive(self, msg, sender):
        _, origin, payload = msg

        self.recv_count[origin] += 1

        if origin not in self.seen:
            self.seen.add(origin)

        # Already forwarded, just count and skip
        if origin in self.forwarded:
            return

        # First time seeing this origin: buffer and schedule delayed decision
        if origin not in self.pending:
            self.pending[origin] = msg
            delay = self.DECISION_DELAY + random.uniform(0.0, self.JITTER)
            self.schedule(delay, self._decide_forward, origin)


def build_random_network(node_cls, n=30, area_size=10, tx_range=2.2, seed=42, verbose=False):
    loop = EventLoop()
    net = WirelessNetwork(loop, tx_range=tx_range, seed=seed, verbose=verbose)

    rng = random.Random(seed)
    for i in range(n):
        x = rng.uniform(0, area_size)
        y = rng.uniform(0, area_size)
        net.add_node(node_cls(str(i)), x, y)

    return loop, net


def run_once(node_cls, seed=42, n=30, area_size=10, tx_range=2.2, until=20.0, source="0"):
    random.seed(seed)

    loop, net = build_random_network(
        node_cls=node_cls,
        n=n,
        area_size=area_size,
        tx_range=tx_range,
        seed=seed,
        verbose=False,
    )

    if source not in net.nodes:
        source = sorted(net.nodes)[0]

    loop.schedule(1.0, net.nodes[source].flood, "hello!")
    loop.run(until=until)

    delivered = sum(1 for nid in net.nodes if len(net.nodes[nid].seen) > 0)
    total_forwards = sum(net.nodes[nid].forward_count for nid in net.nodes)
    total_receptions = sum(sum(node.recv_count.values()) for node in net.nodes.values())

    return {
        "delivered": delivered,
        "nodes": len(net.nodes),
        "delivery_ratio": delivered / len(net.nodes),
        "total_forwards": total_forwards,
        "total_receptions": total_receptions,
    }


def summarize(name, results):
    dr = [r["delivery_ratio"] for r in results]
    fw = [r["total_forwards"] for r in results]
    rx = [r["total_receptions"] for r in results]

    print(f"\n{name}")
    print(f"  delivery_ratio: mean={stats.mean(dr):.3f}, stdev={stats.pstdev(dr):.3f}")
    print(f"  total_forwards: mean={stats.mean(fw):.2f}, stdev={stats.pstdev(fw):.2f}")
    print(f"  total_receptions: mean={stats.mean(rx):.2f}, stdev={stats.pstdev(rx):.2f}")


def main():
    seeds = list(range(1, 21))
    n = 30
    area_size = 15
    tx_range = 1.8
    until = 20.0

    baseline_results = []
    adaptive_results = []

    for seed in seeds:
        baseline_results.append(
            run_once(
                BaselineNode,
                seed=seed,
                n=n,
                area_size=area_size,
                tx_range=tx_range,
                until=until,
            )
        )
        adaptive_results.append(
            run_once(
                AdaptiveNode,
                seed=seed,
                n=n,
                area_size=area_size,
                tx_range=tx_range,
                until=until,
            )
        )

    summarize("Baseline flooding", baseline_results)
    summarize("Adaptive flooding", adaptive_results)

    print("\nPer-seed comparison:")
    print("seed | baseline_forwards | adaptive_forwards | baseline_delivery | adaptive_delivery")
    for i, seed in enumerate(seeds):
        b = baseline_results[i]
        a = adaptive_results[i]
        print(
            f"{seed:>4} | {b['total_forwards']:>17} | {a['total_forwards']:>17} | "
            f"{b['delivery_ratio']:.3f} | {a['delivery_ratio']:.3f}"
        )


if __name__ == "__main__":
    main()