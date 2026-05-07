import matplotlib.pyplot as plt
plt.style.use('seaborn-v0_8-paper')
# 三个网络场景的平均结果
scenarios = ["Dense", "Medium", "Sparse"]

baseline_delivery = [1.000, 0.832, 0.220]
adaptive_delivery = [1.000, 0.775, 0.210]

baseline_forwards = [30.00, 24.95, 6.60]
adaptive_forwards = [26.65, 22.20, 6.25]

# 也可以改成 total_receptions 做另一张图
baseline_receptions = [340.40, 111.05, 16.05]
adaptive_receptions = [300.90, 99.30, 15.55]

plt.figure(figsize=(7, 5))

# 画每个场景从 baseline 到 adaptive 的箭头
for i, s in enumerate(scenarios):
    x1, y1 = baseline_forwards[i], baseline_delivery[i]
    x2, y2 = adaptive_forwards[i], adaptive_delivery[i]

    plt.scatter(x1, y1, marker='o', s=80, label='Baseline' if i == 0 else "")
    plt.scatter(x2, y2, marker='s', s=80, label='Adaptive' if i == 0 else "")

    plt.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(arrowstyle="->", lw=1.5)
    )

    plt.text(x1 + 0.15, y1 + 0.01, s, fontsize=9)

plt.xlabel("Total Forwards")
plt.ylabel("Delivery Ratio")
plt.title("Efficiency-Reliability Tradeoff")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig("tradeoff.png", dpi=300)
plt.show()