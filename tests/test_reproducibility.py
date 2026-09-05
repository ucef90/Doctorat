import torch

from recoa_pinn.model import MLP
from recoa_pinn.reproducibility import configure_reproducibility, make_generator


def test_same_seed_produces_same_parameters_and_samples():
    configure_reproducibility(123)
    first = MLP(2, 8)
    first_parameters = torch.cat([parameter.detach().flatten() for parameter in first.parameters()])
    first_samples = torch.rand(10, generator=make_generator(999))

    configure_reproducibility(123)
    second = MLP(2, 8)
    second_parameters = torch.cat([parameter.detach().flatten() for parameter in second.parameters()])
    second_samples = torch.rand(10, generator=make_generator(999))

    assert torch.equal(first_parameters, second_parameters)
    assert torch.equal(first_samples, second_samples)

