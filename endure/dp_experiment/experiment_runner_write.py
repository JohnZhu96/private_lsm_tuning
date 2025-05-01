import os
import sys
import json
import numpy as np
from pprint import pprint
from datetime import datetime
from scipy.special import rel_entr

# Make Endure importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from endure.lsm import (
    Cost, ClassicGen, LSMBounds, Workload
)
from endure.solver import ClassicSolver
from endure.dp_experiment.dp_utils import perturb_workload
import endure.lsm.lsm_cost_model as CostModel


def kl_div(w_hat: Workload, w_init: Workload, smooth=1e-8):
    a = np.array([w_hat.z0, w_hat.z1, w_hat.q, w_hat.w]) + smooth
    b = np.array([w_init.z0, w_init.z1, w_init.q, w_init.w]) + smooth
    a /= a.sum()
    b /= b.sum()
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


# === Experiment Config ===
EPSILON_VALUES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]
NUM_TRIALS = 100

# Define workload profiles
read_profiles = [
    {"z0": 0.3, "z1": 0.58, "q": 0.12, "w": 0.0},  # Profile 1
    {"z0": 0.07, "z1": 0.10, "q": 0.84, "w": 0.0},  # Profile 2
    {"z0": 0.86, "z1": 0.09, "q": 0.04, "w": 0.0},  # Profile 3
    {"z0": 0.08, "z1": 0.86, "q": 0.06, "w": 0.0},  # Profile 4
    {"z0": 0.3, "z1": 0.58, "q": 0.12, "w": 0.0},  # Profile 5 (repeat for symmetry)
    {"z0": 0.3, "z1": 0.58, "q": 0.12, "w": 0.0},  # Profile 6
]

# Add write-heavy workload profile
write_profile = {"z0": 0.01, "z1": 0.01, "q": 0.01, "w": 0.97}

# Combine all profiles 
all_profiles = read_profiles + [write_profile]
profile_names = ["read1", "read2", "read3", "read4", "read5", "read6", "write"]

bounds = LSMBounds()
gen = ClassicGen(bounds, seed=42)
cost_calc = Cost(bounds.max_considered_levels)
solver = ClassicSolver(bounds)

# Create output directory
os.makedirs("endure/dp_experiment/results", exist_ok=True)

# Sample system (same for all profiles to make comparisons fair)
system = gen.sample_system()

# Run experiment for each profile
for profile_idx, (profile, profile_name) in enumerate(zip(all_profiles, profile_names), 1):
    print(f"\n=== Running experiment for {profile_name.capitalize()} Profile ===")
    
    # Create workload from profile
    true_workload = Workload(
        z0=profile["z0"], 
        z1=profile["z1"], 
        q=profile["q"], 
        w=profile["w"]
    )
    
    # Get baseline configuration
    baseline_config, _ = solver.get_nominal_design(system, true_workload)
    
    results = []
    
    for epsilon in EPSILON_VALUES:
        print(f"  Processing epsilon={epsilon}")
        for trial in range(NUM_TRIALS):
            entry = {
                "epsilon": epsilon,
                "trial": trial + 1,
            }

            dp_workload = perturb_workload(true_workload, epsilon)
            dp_config, _ = solver.get_nominal_design(system, dp_workload)

            # Serialize base info
            entry["true_workload"] = serialize_workload(true_workload)
            entry["dp_workload"] = serialize_workload(dp_workload)
            entry["kl_divergence"] = kl_div(dp_workload, true_workload)
            entry["baseline_config"] = serialize_config(baseline_config)
            entry["dp_config"] = serialize_config(dp_config)

            # Cost breakdowns
            entry["baseline_metrics"] = get_cost_components(baseline_config, system, true_workload, cost_calc)
            entry["dp_metrics"] = get_cost_components(dp_config, system, true_workload, cost_calc)

            results.append(entry)

    # Save results for this profile
    out_path = f"endure/dp_experiment/results/{profile_name}.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"✅ Results for {profile_name.capitalize()} Profile saved to: {out_path}")

print("\n🎉 All experiments completed successfully!")