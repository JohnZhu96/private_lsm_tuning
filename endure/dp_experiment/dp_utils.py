import numpy as np
from endure.lsm import Workload

def perturb_workload2(workload: Workload, epsilon: float, sensitivity: float = 4.0) -> Workload:
    scale = sensitivity / epsilon
    noisy_values = np.array([workload.z0, workload.z1, workload.q, workload.w]) + \
                   np.random.laplace(0, scale, 4)

    # Ensure values are non-negative and normalized
    noisy_values = np.clip(noisy_values, 1e-6, None)
    noisy_values /= noisy_values.sum()

    return Workload(z0=noisy_values[0], z1=noisy_values[1], q=noisy_values[2], w=noisy_values[3])


def perturb_workload(workload: Workload, epsilon: float, sensitivity: float = 2.0, seed: int = None) -> Workload:
    """
    Applies Laplace noise to workload components to simulate differentially private workload.

    Parameters:
    - workload: The original Workload object (with z0, z1, q, w).
    - epsilon: Privacy budget (larger = less noise).
    - sensitivity: Global sensitivity (default = 2.0).
    - seed: Optional seed for reproducibility.

    Returns:
    - A new Workload object with perturbed (and normalized) parameters.
    """

    # Ensure reproducibility
    if seed is not None:
        np.random.seed(seed)

    # Extract original workload components
    original_values = np.array([workload.z0, workload.z1, workload.q, workload.w])

    # Add Laplace noise to each component
    scale = sensitivity / epsilon
    noise = np.random.laplace(loc=0.0, scale=scale, size=4)
    noisy_values = original_values + noise

    # Avoid negative components (min threshold 1e-6 to preserve normalization)
    noisy_values = np.maximum(noisy_values, 1e-6)

    # Normalize so the four parameters sum to 1
    noisy_values /= noisy_values.sum()

    # Return new Workload instance
    return Workload(
        z0=noisy_values[0],
        z1=noisy_values[1],
        q=noisy_values[2],
        w=noisy_values[3],
    )
