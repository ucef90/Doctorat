from __future__ import annotations

import torch
from torch import nn


class MLP(nn.Module):
    def __init__(self, hidden_layers: int, hidden_width: int, activation: str = "tanh") -> None:
        super().__init__()
        activations = {"tanh": nn.Tanh, "silu": nn.SiLU}
        if activation not in activations:
            raise ValueError(f"Activation inconnue : {activation}")
        layers: list[nn.Module] = [nn.Linear(2, hidden_width), activations[activation]()]
        for _ in range(hidden_layers - 1):
            layers.extend([nn.Linear(hidden_width, hidden_width), activations[activation]()])
        layers.append(nn.Linear(hidden_width, 1))
        self.network = nn.Sequential(*layers)
        self.reset_parameters()

    def reset_parameters(self) -> None:
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_normal_(module.weight)
                nn.init.zeros_(module.bias)

    def forward(self, tx: torch.Tensor) -> torch.Tensor:
        return self.network(tx)

