from __future__ import annotations

import json
import hashlib
import os
import platform
import random
import sys
from pathlib import Path

import numpy as np
import torch


def configure_reproducibility(seed: int, deterministic: bool = True) -> None:
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(deterministic, warn_only=True)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = deterministic


def make_generator(seed: int, device: str = "cpu") -> torch.Generator:
    generator_device = device if str(device).startswith("cuda") else "cpu"
    generator = torch.Generator(device=generator_device)
    generator.manual_seed(int(seed))
    return generator


def environment_manifest() -> dict[str, object]:
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "torch": torch.__version__,
        "numpy": np.__version__,
        "cuda_available": torch.cuda.is_available(),
        "cuda_version": torch.version.cuda,
        "cudnn_version": torch.backends.cudnn.version() if torch.cuda.is_available() else None,
        "device_count": torch.cuda.device_count(),
        "torch_num_threads": torch.get_num_threads(),
        "torch_num_interop_threads": torch.get_num_interop_threads(),
    }


def tensor_fingerprint(values: dict[str, torch.Tensor | None]) -> str:
    """Hash actual initial tensors without consuming any random numbers."""
    digest = hashlib.sha256()
    for name, value in sorted(values.items()):
        digest.update(name.encode())
        if value is None:
            digest.update(b"None")
            continue
        data = value.detach().cpu().contiguous()
        digest.update(str((tuple(data.shape), data.dtype)).encode())
        digest.update(data.numpy().tobytes())
    return digest.hexdigest()


def save_environment(path: str | Path) -> None:
    Path(path).write_text(json.dumps(environment_manifest(), indent=2), encoding="utf-8")


def resolve_device(requested: str) -> torch.device:
    if requested == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    device = torch.device(requested)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA a été demandé mais aucun GPU CUDA n'est disponible.")
    return device


def resolve_dtype(name: str) -> torch.dtype:
    mapping = {"float32": torch.float32, "float64": torch.float64}
    if name not in mapping:
        raise ValueError(f"dtype non pris en charge : {name}")
    return mapping[name]
