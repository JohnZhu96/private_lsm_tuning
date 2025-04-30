
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

1. **Generate true workload Ω** and system configuration **S** using Endure's `ClassicGen`.
2. **Apply Laplace noise** to the 4 workload components (`z0`, `z1`, `q`, `w`) using:

   ```
   Laplace(μ = 0, b = sensitivity / ε), where sensitivity = 1.0
   ```

3. Use `solver.get_nominal_design(...)`:
   - On **Ω** to get the baseline configuration Φ.
   - On **Ω<sub>ε</sub>** to get the private configuration Φ<sub>ε</sub>.

4. Evaluate both configurations on the original workload Ω.
5. Repeat for multiple ε values and trials to capture variability.

---

## 🔁 Epsilon Values Used

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

## Project Structure

```
private_lsm_tuning/
├── endure/
│   ├── lsm/                       # Endure's core LSM classes and cost models
│   └── dp_experiment/
│       ├── dp_utils.py           # Applies Laplace noise to workloads
│       ├── experiment_runner.py  # Main experiment pipeline
│       └── results/              # JSON output directory
```

---

## ⚙️ How to Run

1. **Set up virtual environment**:
   ```bash
   python3 -m venv lsm_env
   source lsm_env/bin/activate
   pip install numpy scipy numba
   ```

2. **Run experiment**:
   ```bash
   python endure/dp_experiment/experiment_runner.py
   ```

3. **View output**:
   Results will be saved to:
   ```
   endure/dp_experiment/results/experiment_summary_YYYYMMDD_HHMMSS.json
   ```

---

## 📈 Metrics in Output JSON

Each record contains:

### Global Metadata
- `epsilon`: The privacy budget used for perturbation.
- `trial`: The trial number (1-based).
- `kl_divergence`: Divergence between Ω and Ω<sub>ε</sub>.

### Workloads & Configurations
- `true_workload`: Original workload {z0, z1, q, w}.
- `dp_workload`: Perturbed workload.
- `baseline_config`: Tuned on true workload.
- `dp_config`: Tuned on perturbed workload.

### Performance Metrics (under `baseline_metrics` and `dp_metrics`)
| Field                  | Description                                      |
|------------------------|--------------------------------------------------|
| `total_cost`           | Aggregated cost over all query/write types.     |
| `empty_point_cost`     | Cost of false-positive point lookups.           |
| `non_empty_point_cost` | Cost of successful point lookups.               |
| `range_query_cost`     | Cost from range queries.                        |
| `write_cost`           | Cost for insertions and compactions.            |
| `ingestion_throughput` | Approximated as `1 / write_cost`.               |

---

## Interpretation Guide

- Compare `baseline_metrics` vs `dp_metrics` to assess degradation from privacy.
- Observe how increasing ε improves `dp_metrics` (e.g., lowers total cost).
- Use `kl_divergence` to understand how much noise was added.


---

## Contact

Linfeng Zhu (linfengzhu@brandeis.edu)
