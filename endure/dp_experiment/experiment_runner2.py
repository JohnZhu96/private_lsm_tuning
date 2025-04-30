import os
import sys
import json
import numpy as np
from datetime import datetime
from scipy.special import rel_entr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from endure.lsm import (
    Cost, ClassicGen, LSMBounds, Workload
)
from endure.solver import ClassicSolver
from endure.dp_experiment.dp_utils import perturb_workload
import endure.lsm.lsm_cost_model as CostModel

def kl_div(w_hat: Workload, w_init: Workload):
    a = np.array([w_hat.z0, w_hat.z1, w_hat.q, w_hat.w])
    b = np.array([w_init.z0, w_init.z1, w_init.q, w_init.w])
    return float(np.sum(rel_entr(a, b)))

def serialize_workload(w: Workload):
    return {
        "z0": float(w.z0),
        "z1": float(w.z1),
        "q": float(w.q),
        "w": float(w.w)
    }

def serialize_config(design_obj):
    d = vars(design_obj).copy()
    if 'policy' in d:
        d['policy'] = str(d['policy'])
    return {k: float(v) if isinstance(v, np.generic) else v for k, v in d.items()}

def get_cost_components(design, system, workload, cost_calc):
    k_list = cost_calc.create_k_list(design, system)
    c_z0, c_z1, c_q, c_w = CostModel.calc_individual_cost(
        design.bits_per_elem,
        design.size_ratio,
        k_list,
        workload.z0,
        workload.z1,
        workload.q,
        workload.w,
        system.entries_per_page,
        system.selectivity,
        system.entry_size,
        system.mem_budget,
        system.num_entries,
        system.phi,
    )
    total = c_z0 + c_z1 + c_q + c_w
    ingestion_throughput = float("inf") if c_w == 0 else 1.0 / c_w
    return {
        "total_cost": total,
        "empty_point_cost": c_z0,
        "non_empty_point_cost": c_z1,
        "range_query_cost": c_q,
        "write_cost": c_w,
        "ingestion_throughput": ingestion_throughput
    }

# experiment config
EPSILON_VALUES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]
RHO_VALUES = [0.0, 0.2, 0.5, 1.0, 2.0, 5.0]  # workload uncertainty
NUM_TRIALS = 100

# Initialize ENDURE components
bounds = LSMBounds()
gen = ClassicGen(bounds, seed=42)
cost_calc = Cost(bounds.max_considered_levels)
solver = ClassicSolver(bounds)

# Sample true workload and system
true_workload = gen.sample_workload()
system = gen.sample_system()
baseline_config, _ = solver.get_nominal_design(system, true_workload)

results = []

# run experiments for each epsilon and rho combination
for epsilon in EPSILON_VALUES:
    for rho in RHO_VALUES:
        for trial in range(NUM_TRIALS):
            entry = {
                "epsilon": epsilon,
                "rho": rho,
                "trial": trial + 1,
            }

            # perturb workload
            dp_workload = perturb_workload(true_workload, epsilon, seed=trial)

            # perform robust tuning with the perturbed workload and rho
            dp_config, _ = solver.get_robust_design(
                system=system,
                workload=dp_workload,
                rho=rho
            )

            entry["true_workload"] = serialize_workload(true_workload)
            entry["dp_workload"] = serialize_workload(dp_workload)
            entry["kl_divergence"] = kl_div(dp_workload, true_workload)
            entry["baseline_config"] = serialize_config(baseline_config)
            entry["dp_config"] = serialize_config(dp_config)

            # cost breakdowns
            entry["baseline_metrics"] = get_cost_components(baseline_config, system, true_workload, cost_calc)
            entry["dp_metrics"] = get_cost_components(dp_config, system, true_workload, cost_calc)

            results.append(entry)

os.makedirs("endure/dp_experiment/results", exist_ok=True)
out_path = f"endure/dp_experiment/results/robust_experiment_summary.json"
with open(out_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"\n✅ Results saved to: {out_path}")