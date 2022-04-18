import pandas as pd
import opt


# Load the CSV file (and drop the unnecessary columns).
df = pd.read_csv("04-BBS-Beams Rebar Python problem.csv", skiprows=1)
df.drop(["Unnamed: 5", "Unnamed: 6", "Unnamed: 7", "Unnamed: 8"], axis="columns", inplace=True)

# Solve the CSP.
model = opt.solve(data=df, rebar_length_mm=10000)