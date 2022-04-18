import numpy as np
import pandas as pd
import pyomo.kernel as pyo


def solve(data, rebar_length_mm):
    """Construct and solve a simple cutting stock problem from the given DataFrame `data`.
    
    Each rod of rebar can be `rebar_length_mm` millimeters long. Prints the number of needed rods
    and saves all cuts into `results.csv`.
    """
    # Sort by rebar length.
    data.sort_values(by="Rebar Length(mm)", inplace=True, ascending=False)
    
    # Create a new (empty) Pyomo model.
    model = pyo.block()

    # Calculate an upper bound for the amount of needed rods.
    max_rods = int((data["Quantity"] / (rebar_length_mm / data["Rebar Length(mm)"]).apply(np.floor)).apply(np.ceil).sum())

    # Convert the DataFrame to a dict (for easier handling).
    bar_marks = data.set_index("Bar Mark").to_dict("index")

    # Containers for variables and constraints.
    model.rods = pyo.variable_dict()
    model.rod_cuts = pyo.variable_dict()
    model.rod_lengths = pyo.constraint_dict()
    model.bar_marks = pyo.constraint_dict()

    # Construct each rod.
    for i in range(max_rods):
        # Add a new dict for each rod.
        model.rod_cuts[i] = pyo.variable_dict()

        # Add a variable that describes whether this rod is "used".
        model.rods[i] = pyo.variable(domain=pyo.IntegerSet, lb=0, ub=1)

        # Add a variable describing how much of each bar mark is cut here.
        for bm in bar_marks:
            model.rod_cuts[(i, bm)] = pyo.variable(domain=pyo.IntegerSet, lb=0, ub=int(rebar_length_mm / bar_marks[bm]["Rebar Length(mm)"]))

        # Constraint the length of all bar marks cut from this rod.
        model.rod_lengths[i] = pyo.constraint(
            sum(model.rod_cuts[(i, bm)] * bar_marks[bm]["Rebar Length(mm)"] for bm in bar_marks) <= rebar_length_mm * model.rods[i]
        )

    # We can fix some variables for improved performance where one cut takes more than half of the bar:

    # 1. get all bar marks that are that large
    big = [bm for bm in bar_marks if bar_marks[bm]["Rebar Length(mm)"] > rebar_length_mm/2]

    # 2. fix stuff for all of them (rc keeps the current rod count)
    rc = 0
    for b in big:
        for _ in range(bar_marks[b]["Quantity"]):
            # This rod is used.
            model.rod_cuts[(rc, b)].fix(1)
            
            # All other "big" bar marks can not be cut here (since they are too large).
            for other in big:
                if other == b:
                    continue
                model.rod_cuts[(rc, other)].fix(0)

            rc += 1

        # This "big" bar mark can not be cut in other rods (since all are cut already).
        for i in range(rc, max_rods):
            model.rod_cuts[(i, b)].fix(0)

    # Each bar mark needs to be cut at least "Quantity" times.
    for bm in bar_marks:
        model.bar_marks[bm] = pyo.constraint(
            sum(model.rod_cuts[(i, bm)] for i in range(max_rods)) >= bar_marks[bm]["Quantity"]
        )

    # We minimize the total number of used rods
    model.obj = pyo.objective(sum(model.rods[i] for i in range(max_rods)))

    # Solve the model.
    opt = pyo.SolverFactory("gurobi")       # for using CBC instead: "cbc.exe"
    opt.solve(model, tee=True)

    # Analyze and print.
    opt_rods = sum(model.rods[i].value for i in range(max_rods))
    print(f"This uses <{opt_rods}> rods of rebar.")

    # Generate a CSV file containing all resulting cutting patterns.
    results = {k: v | {"scrap (mm)": rebar_length_mm - sum(bar_marks[bm]["Rebar Length(mm)"] for bm in v["pattern"])} for (k, v) in {
        i: {"pattern": [it for sl in [[bm] * int(model.rod_cuts[(i, bm)].value) for bm in bar_marks] for it in sl]}
        for i in range(max_rods)
    }.items() if len(v["pattern"]) > 0}
    pd.DataFrame.from_dict(results, orient="index").to_csv("results.csv")
