import numpy as np
from endure.lsm import Workload

def perturb_workload(workload: Workload, epsilon: float, sensitivity: float = 1.0) -> Workload:
    scale = sensitivity / epsilon
    noisy_values = np.array([workload.z0, workload.z1, workload.q, workload.w]) + \
                   np.random.laplace(0, scale, 4)

    # Ensure values are non-negative and normalized
    noisy_values = np.clip(noisy_values, 1e-6, None)
    noisy_values /= noisy_values.sum()

    return Workload(z0=noisy_values[0], z1=noisy_values[1], q=noisy_values[2], w=noisy_values[3])
