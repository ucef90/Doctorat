from .allen_cahn import AllenCahnProblem
from .burgers import BurgersProblem
from .helmholtz import HelmholtzProblem
from .wave import WaveProblem


PROBLEMS = {
    "burgers": BurgersProblem,
    "allen_cahn": AllenCahnProblem,
    "helmholtz": HelmholtzProblem,
    "wave": WaveProblem,
}


def make_problem(config, device, dtype):
    name = str(config["name"]).lower()
    try:
        return PROBLEMS[name](config, device, dtype)
    except KeyError as error:
        raise ValueError(f"Problème inconnu {name!r}; choix : {sorted(PROBLEMS)}") from error


__all__ = [
    "AllenCahnProblem", "BurgersProblem", "HelmholtzProblem", "WaveProblem",
    "make_problem",
]
