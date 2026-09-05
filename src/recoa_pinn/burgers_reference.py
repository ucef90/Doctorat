"""Independent Cole-Hopf quadrature for the standard sine Burgers benchmark.

u(0,x)=-sin(pi*x), x in [-1,1], homogeneous boundary values.
The periodic Cole-Hopf heat solution has the symmetries needed for these
Dirichlet values. This implementation evaluates its Gaussian convolution;
it does not evolve the finite-volume solver or interpolate its output.
See BURGERS_REFERENCE_VALIDATION_V10.md for derivation and attribution.
"""
from functools import lru_cache

import numpy as np


@lru_cache(maxsize=8)
def _quadrature(order):
    nodes, weights = np.polynomial.hermite.hermgauss(order)
    return nodes, np.log(weights)


def cole_hopf(points, viscosity=0.01 / np.pi, order=128, chunk_size=2048):
    """Return u(t,x), using float64 Gauss-Hermite quadrature, shape (n,1).

    Orders 16..256 are supported; convergence must be checked for the domain
    and viscosity of interest. Initial values are evaluated analytically.
    """
    points = np.asarray(points, dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 2:
        raise ValueError("Expected an (n,2) array of (t,x)")
    if not np.isfinite(points).all() or np.any(points[:, 0] < 0):
        raise ValueError("Finite points and nonnegative times are required")
    if not np.isfinite(viscosity) or viscosity <= 0:
        raise ValueError("Viscosity must be finite and positive")
    if not isinstance(order, int) or not 16 <= order <= 256:
        raise ValueError("Quadrature order must be an integer in [16,256]")
    if chunk_size < 1:
        raise ValueError("chunk_size must be positive")
    nodes, log_weights = _quadrature(order)
    result = np.empty((len(points), 1), dtype=np.float64)
    for start in range(0, len(points), chunk_size):
        block = points[start:start + chunk_size]
        t, x = block[:, :1], block[:, 1:2]
        phase = np.pi * (x - 2 * np.sqrt(viscosity * t) * nodes)
        log_mass = log_weights - np.cos(phase) / (2 * np.pi * viscosity)
        mass = np.exp(log_mass - log_mass.max(axis=1, keepdims=True))
        values = -(mass * np.sin(phase)).sum(axis=1) / mass.sum(axis=1)
        initial = block[:, 0] == 0
        values[initial] = -np.sin(np.pi * block[initial, 1])
        result[start:start + len(block), 0] = values
    return result
