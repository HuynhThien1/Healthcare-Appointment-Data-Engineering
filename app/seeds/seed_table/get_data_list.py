import pandas as pd
from pathlib import Path

file_path = Path(__file__).resolve().parents[1] / "data" / "dim_doctor.csv"
df = pd.read_csv(file_path, encoding="utf-8-sig")
print(list(df["specialty"].unique()))