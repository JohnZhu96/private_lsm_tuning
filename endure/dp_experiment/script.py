import json
import numpy as np
import matplotlib.pyplot as plt

with open("endure/dp_experiment/results/robust_experiment_summary.json", "r") as f:
    results = json.load(f)

# Aggregate results by epsilon and rho
epsilons = sorted(set(entry["epsilon"] for entry in results))
rhos = sorted(set(entry["rho"] for entry in results))
avg_costs = np.zeros((len(rhos), len(epsilons)))

for i, rho in enumerate(rhos):
    for j, epsilon in enumerate(epsilons):
        costs = [
            entry["dp_metrics"]["total_cost"]
            for entry in results
            if entry["epsilon"] == epsilon and entry["rho"] == rho
        ]
        avg_costs[i, j] = np.mean(costs)

# Cost vs. Epsilon for each Rho
plt.figure(figsize=(10, 6))
for i, rho in enumerate(rhos):
    plt.plot(epsilons, avg_costs[i, :], marker='o', label=f'rho={rho}')
plt.xlabel('Epsilon')
plt.ylabel('Average Total Cost')
plt.title('Average Total Cost vs. Epsilon for Different Rho Values (ClassicSolver)')
plt.legend()
plt.grid(True)
plt.savefig('cost_vs_epsilon_by_rho_classic.png')
plt.show()