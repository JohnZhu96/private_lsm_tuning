
# Differentially Private LSM Tree Tuning with Endure

This project evaluates how tuning frameworks like **Endure** perform when the input **workload statistics are protected using differential privacy (DP)**. It simulates a scenario where the tuning service only receives **noisy versions** of the actual workload due to privacy concerns.

---

## Motivation

In real-world systems, organizations often optimize LSM-tree-based databases (e.g., RocksDB) using third-party tuning frameworks like Endure. However, **revealing precise workload distributions may leak sensitive information** about user access patterns or business logic.

To preserve privacy, this project applies **differential privacy** to workload vectors before tuning and evaluates the impact on configuration quality and estimated performance.

---

## Experiment Design

### Roles
- **Party A** owns the database and generates a true workload vector (Ω).
- **Party B** (e.g., Endure) tunes the system using noisy statistics Ω<sub>ε</sub> for privacy protection.

### Step-by-Step Workflow

1. Define representative workloads (e.g., uniform, read-heavy, write-heavy, point-heavy).
2. For each workload:
   - Generate a true workload Ω and system S using `ClassicGen`.
   - Apply Laplace noise to Ω:
     ```
     Laplace(μ = 0, b = sensitivity / ε)
     ```
   - Tune Endure on both Ω and Ω<sub>ε</sub> (with and without robustness via ρ).
3. Evaluate both configurations on the true workload.
4. Repeat for multiple ε and ρ values, across 100 trials each.

---

## Epsilon and Rho Values Used

```python
EPSILON_VALUES = [0.1, 0.2, ..., 2.0]
RHO_VALUES = [0.0, 0.2, 0.5, 1.0, 2.0, 5.0]
```

- **ε** controls the strength of privacy (lower = stronger privacy).
- **ρ** controls Endure’s robustness to workload uncertainty.

---

## Workload Profiles

The following profiles were used:

| Type         | z0   | z1   | q    | w    |
|--------------|------|------|------|------|
| Uniform      | 0.25 | 0.25 | 0.25 | 0.25 |
| Read-heavy   | 0.33 | 0.33 | 0.33 | 0.01 |
| Write-heavy  | 0.01 | 0.01 | 0.01 | 0.97 |
| Point-heavy  | 0.3  | 0.58 | 0.12 | 0.0  |
| Range-heavy  | 0.07 | 0.10 | 0.84 | 0.0  |

---

## Project Structure

```
private_lsm_tuning/
├── endure/
│   ├── lsm/                       # Endure core modules
│   └── dp_experiment/
│       ├── dp_utils.py           # Perturb workload with Laplace noise
│       ├── experiment_runner.py  # Uniform workload experiment
│       ├── experiment_runner2.py # Robust tuning (ε × ρ)
│       ├── read_profile_experiment.py  # Read profile tuning
│       ├── run_read_profiles.py  # Generates read{1..6}.json
│       └── results/              # Output directory
```

---

## How to Run

```bash
python3 -m venv lsm_env
source lsm_env/bin/activate
pip install numpy scipy numba

# Run for uniform or read/write heavy workloads
python endure/dp_experiment/experiment_runner.py

# Run robust tuning (ε × ρ grid)
python endure/dp_experiment/experiment_runner2.py

# Run read profile tuning
python endure/dp_experiment/read_profile_experiment.py
```

---

## Output JSON Structure

Each trial records:

### Metadata
- `epsilon`, `rho`, `trial`
- `kl_divergence`: KL between true and noisy workload

### Workloads & Configs
- `true_workload`: The original workload
- `dp_workload`: The perturbed workload
- `baseline_config`: From tuning on true workload
- `dp_config`: From tuning on Ω<sub>ε</sub>

### Performance Metrics
| Metric               | Description                                |
|----------------------|--------------------------------------------|
| `total_cost`         | Aggregate query/write cost                 |
| `*_point_cost`       | Cost for false vs. true lookups            |
| `range_query_cost`   | Cost for range queries                     |
| `write_cost`         | Write/compaction cost                      |
| `ingestion_throughput` | Defined as `1 / write_cost` or ∞ if w=0 |

---

## Interpretation Guide

- **Baseline vs. DP Configs** → Utility loss due to privacy
- **KL Divergence** → Measures distortion from noise
- **Epsilon trend** → High ε preserves utility; low ε sacrifices it
- **Ingestion Throughput** → ∞ when no writes (w = 0), expected behavior

---

## Contact

Linfeng Zhu (linfengzhu@brandeis.edu)

GitHub Repository: [github.com/linfengzhu/private_lsm_tuning](https://github.com/linfengzhu/private_lsm_tuning)
