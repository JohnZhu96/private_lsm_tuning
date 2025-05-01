# Differentially Private LSM Tree Tuning with Endure

This project evaluates how tuning frameworks like **Endure** perform when the input **workload statistics are protected using differential privacy (DP)**. It simulates a scenario where the tuning service only receives **noisy versions** of the actual workload due to privacy concerns.

---

## Motivation

In many real-world systems, organizations may want to optimize their LSM-tree-based database configurations (e.g., compaction strategy, memory allocation) using third-party tuning services like Endure. However, **exposing exact access patterns or workload characteristics may leak sensitive information**.

To preserve privacy, this project applies **differential privacy** to the workload before tuning and evaluates the impact on performance.

---

## Experiment Design

### Roles
- **Party A** owns the database and generates a real workload (Ω).
- **Party B** (e.g. Endure) tunes the database configuration based on shared workload statistics.

### Problem
Due to privacy constraints, Party A cannot share Ω directly. Instead, Party A applies **differential privacy** by perturbing the workload using **Laplace noise** and sends the result Ω<sub>ε</sub> to Party B.

### Step-by-Step Workflow

1. Define six representative **read profiles** (e.g., range-heavy, empty-lookup-heavy).
2. For each read profile:
   - Generate a true workload Ω and system configuration S using `ClassicGen`.
   - Apply **Laplace noise** to Ω to produce Ω<sub>ε</sub>, using:
     ```
     Laplace(μ = 0, b = sensitivity / ε)
     ```
   - Tune Endure using Ω<sub>ε</sub> to get Φ<sub>ε</sub>; compare with Φ (tuned on Ω).
3. Evaluate **both configurations on the original workload Ω**.
4. Repeat the above for **multiple ε values and 100 trials per ε**.

---

## Epsilon Values Used

```python
EPSILON_VALUES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]
```

### What Does Epsilon (ε) Mean?

- **ε (epsilon)** is the privacy budget in differential privacy.
- **Smaller ε**:
  - Adds more noise
  - Provides stronger privacy
  - Reduces tuning accuracy
- **Larger ε**:
  - Adds less noise
  - Provides weaker privacy
  - Preserves workload fidelity better

This experiment quantifies the **privacy-utility trade-off**.

---

## Read Profiles

Workloads were constructed with a fixed write weight of zero to isolate **read pattern behavior**. Example profiles:

| Profile Type           | z0   | z1   | q    | w   |
|------------------------|------|------|------|-----|
| Point heavy            | 0.3  | 0.58 | 0.12 | 0.0 |
| Range heavy            | 0.07 | 0.10 | 0.84 | 0.0 |
| Empty-read dominant    | 0.86 | 0.09 | 0.04 | 0.0 |
| Non-empty lookup heavy | 0.08 | 0.86 | 0.06 | 0.0 |

---

## Project Structure

```
private_lsm_tuning/
├── endure/
│   ├── lsm/                       # Endure's core LSM classes and cost models
│   └── dp_experiment/
│       ├── dp_utils.py           # Applies Laplace noise to workloads
│       ├── experiment_runner.py  # DP tuning using uniform workload
│       ├── experiment_runner2.py # DP tuning across epsilon × rho grid
│       ├── run_read_profiles.py  # Nominal vs robust design comparison
│       ├── read_profile_experiment.py  # DP tuning on read profiles
│       └── results/              # JSON output directory
```

---

## How to Run

1. **Set up virtual environment**:
   ```bash
   python3 -m venv lsm_env
   source lsm_env/bin/activate
   pip install numpy scipy numba
   ```

2. **Run the experiment**:
   ```bash
   python endure/dp_experiment/experiment_runner.py
   # or:
   python endure/dp_experiment/read_profile_experiment.py
   ```

3. **View output**:
   ```
   endure/dp_experiment/results/read1.json
   ...
   read6.json
   ```

---

## Metrics in Output JSON

Each record contains:

### Metadata
- `epsilon`: Privacy budget for workload perturbation.
- `trial`: Trial index.
- `kl_divergence`: KL divergence between true and DP workload (with smoothing applied to avoid log(0)).

### Workload & Configurations
- `true_workload`: The clean workload {z0, z1, q, w}.
- `dp_workload`: The perturbed version with Laplace noise.
- `baseline_config`: Endure-tuned config based on the true workload.
- `dp_config`: Config tuned on the DP workload.

### Performance Metrics (`*_metrics`)
| Field                  | Description                                      |
|------------------------|--------------------------------------------------|
| `total_cost`           | Combined cost from all operations.               |
| `empty_point_cost`     | False positive read cost.                        |
| `non_empty_point_cost` | Successful read cost.                            |
| `range_query_cost`     | Cost of range queries.                           |
| `write_cost`           | Write/compaction overhead.                       |
| `ingestion_throughput` | Defined as `1 / write_cost` (∞ if `w=0`).        |

---

## Interpretation Guide

- Compare `baseline_metrics` vs `dp_metrics` to assess performance loss from privacy.
- Track trends across ε to understand the robustness of tuning.
- Check `kl_divergence` as a measure of distortion — higher means more noise.
- Watch for `ingestion_throughput = ∞` when `w=0` — this is expected.

---

## Contact

Linfeng Zhu (linfengzhu@brandeis.edu)
