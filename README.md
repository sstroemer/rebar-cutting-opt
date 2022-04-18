# rebar-cutting-opt
A small pyomo.kernel example based on a [Reddit post](https://www.reddit.com/r/Python/comments/u5sisg/use_python_to_optimize_the_rebar_lost_in/).
The original data from [u/tomyumm](https://www.reddit.com/user/tomyumm/) was added for easy reproducability. This, solved using Gurobi in roughly 10 secs,
results in 238 rods of rebar being used. The exact cutting patterns for each rod are given in results.csv

> Important remark: "Minimizing waste" is not possible, since this does not have a unique solution. Why? As soon as the demand for every
bar mark is covered, all "left over" space on any rods can be assigned to **any** fitting bar mark to further reduce the overall waste.
We therefore just minimize the amount of rods used - the remaining parts can be cut into anything.

## Running this

Follow these rough steps:
1. Make sure to have a compatible solver installed (like Gurobi, CPLEX; CBC works too - don't know how fast though)
2. Install the conda (e.g. [miniconda](https://docs.conda.io/en/latest/miniconda.html))
3. Setup the environment using
    1. `conda env create -f environment.yml`
    2. `conda activate rebar-cutting`
4. Run `python .\rebar.py`

## Changing the solver

Modify line 81 in `opt.py` - see the [Pyomo doc](https://pyomo.readthedocs.io/en/stable/solving_pyomo_models.html).