import sys
import os

print("Running test_dp_utils.py...")
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from endure.lsm import Workload
from endure.dp_experiment.dp_utils import perturb_workload

w = Workload(z0=0.2, z1=0.3, q=0.4, w=0.1)
w_perturbed = perturb_workload(w, epsilon=0.5)
print(w_perturbed)
