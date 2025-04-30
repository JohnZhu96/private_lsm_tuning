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


def perturb_workload2(workload: Workload, epsilon: float, sensitivity: float = 2.0, seed: int = None) -> Workload:
    # set random seed for reproducibility
    if seed is not None:
        np.random.seed(seed)
    
    # extract workload parameters
    original_values = np.array([workload.z0, workload.z1, workload.q, workload.w])
    
    # laplace noise
    scale = sensitivity / epsilon
    noise = np.random.laplace(0, scale, 4)
    noisy_values = original_values + noise
    
    noisy_values = np.maximum(noisy_values, 0)  # make sure of non-negativity by setting negative values to 0
    if noisy_values.sum() == 0:  # avoid division by zero
        noisy_values = np.ones_like(noisy_values) / 4  # uniform distribution as backup
    else:
        noisy_values /= noisy_values.sum()  # normalize to sum to 1
    
    return Workload(z0=noisy_values[0], z1=noisy_values[1], q=noisy_values[2], w=noisy_values[3])