import random
import statistics as stats
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pywisim import EventLoop, Node, WirelessNetwork

plt.style.use('seaborn-v0_8-paper')
class AdaptiveNode(Node):
    def __init__(self, nid, decision_delay=0.45, jitter=0.10):
        super().__init__(nid)
        self.seen = set()
        self.recv_count = defaultdict(int)
        self.forwarded = set()
        self.pending = {}
        self.forward_count = 0
        self.decision_delay = decision_delay
        self.jitter = jitter

    def _forward_prob(self, origin):
        deg = len(self.net.neighbors(self.nid))
        count = self.recv_count[origin]

        if deg <= 2:
            base = 0.98
        elif deg <= 4:
            base = 0.82
        else:
            base = 0.62

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

        count = self.recv_count[origin]
        p = self._forward_prob(origin)

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

        if origin in self.forwarded:
            return

        if origin not in self.pending:
            self.pending[origin] = msg
            delay = self.decision_delay + random.uniform(0.0, self.jitter)
            self.schedule(delay, self._decide_forward, origin)

    def flood(self, payload):
        self.seen.add(self.nid)
        self.forwarded.add(self.nid)
        self.forward_count += 1
        self.broadcast(("FLOOD", self.nid, payload))


def build_random_network(decision_delay, jitter, n=30, area_size=10, tx_range=2.2, seed=42):
    loop = EventLoop()
    net = WirelessNetwork(loop, tx_range=tx_range, seed=seed, verbose=False)

    rng = random.Random(seed)
    for i in range(n):
        x = rng.uniform(0, area_size)
        y = rng.uniform(0, area_size)
        net.add_node(AdaptiveNode(str(i), decision_delay=decision_delay, jitter=jitter), x, y)

    return loop, net


def run_once(decision_delay, seed=42, n=30, area_size=10, tx_range=2.2, until=20.0, jitter=0.10):
    random.seed(seed)
    loop, net = build_random_network(
        decision_delay=decision_delay,
        jitter=jitter,
        n=n,
        area_size=area_size,
        tx_range=tx_range,
        seed=seed,
    )

    source = "0" if "0" in net.nodes else sorted(net.nodes)[0]
    loop.schedule(1.0, net.nodes[source].flood, "hello!")
    loop.run(until=until)

    delivered = sum(1 for nid in net.nodes if len(net.nodes[nid].seen) > 0)
    total_forwards = sum(net.nodes[nid].forward_count for nid in net.nodes)

    return delivered / len(net.nodes), total_forwards


def main():
    delays = [0.10, 0.20, 0.30, 0.40, 0.45, 0.50, 0.60]
    seeds = list(range(1, 21))

    mean_delivery = []
    mean_forwards = []

    for d in delays:
        drs = []
        fws = []
        for seed in seeds:
            dr, fw = run_once(decision_delay=d, seed=seed, n=30, area_size=10, tx_range=2.2, until=20.0)
            drs.append(dr)
            fws.append(fw)

        mean_delivery.append(stats.mean(drs))
        mean_forwards.append(stats.mean(fws))

    fig, ax1 = plt.subplots(figsize=(7, 5))

    ax1.plot(delays, mean_delivery, marker='o', color='#1f77b4', label='Delivery Ratio')
    ax1.set_xlabel("Decision Delay")
    ax1.set_ylabel("Delivery Ratio")
    ax1.set_ylim(0, 1.05)
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()
    ax2.plot(delays, mean_forwards, marker='s', color='#ff7f0e', linewidth=2, label='Total Forwards')
    ax2.set_ylabel("Total Forwards")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='best')

    plt.title("Sensitivity to Decision Delay")
    plt.tight_layout()
    plt.savefig("decision_delay_sensitivity.png", dpi=300)
    plt.show()


if __name__ == "__main__":
    main()