import matplotlib.pyplot as plt
plt.style.use('seaborn-v0_8-paper')
# ===== 你的实验数据（根据你刚刚三组结果填好的）=====

scenarios = ["Dense", "Medium", "Sparse"]

# Delivery ratio
baseline_delivery = [1.0, 0.832, 0.22]
adaptive_delivery = [1.0, 0.775, 0.21]

# Total forwards
baseline_forwards = [30.0, 24.95, 6.60]
adaptive_forwards = [26.65, 22.20, 6.25]

# Total receptions
baseline_receptions = [340.40, 111.05, 16.05]
adaptive_receptions = [300.90, 99.30, 15.55]


# ===== 图1：Delivery Ratio =====
plt.figure()
plt.plot(scenarios, baseline_delivery, marker='o', label='Baseline')
plt.plot(scenarios, adaptive_delivery, marker='s', label='Adaptive')
plt.xlabel("Network Density")
plt.ylabel("Delivery Ratio")
plt.title("Delivery Ratio vs Network Density")
plt.legend()
plt.grid()
plt.savefig("delivery_ratio.png")


# ===== 图2：Total Forwards =====
plt.figure()
plt.plot(scenarios, baseline_forwards, marker='o', label='Baseline')
plt.plot(scenarios, adaptive_forwards, marker='s', label='Adaptive')
plt.xlabel("Network Density")
plt.ylabel("Total Forwards")
plt.title("Forwarding Overhead vs Network Density")
plt.legend()
plt.grid()
plt.savefig("total_forwards.png")


# ===== 图3：Total Receptions =====
plt.figure()
plt.plot(scenarios, baseline_receptions, marker='o', label='Baseline')
plt.plot(scenarios, adaptive_receptions, marker='s', label='Adaptive')
plt.xlabel("Network Density")
plt.ylabel("Total Receptions")
plt.title("Total Receptions vs Network Density")
plt.legend()
plt.grid()
plt.savefig("total_receptions.png")


plt.show()