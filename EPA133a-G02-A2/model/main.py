import pandas as pd
import random

from simulation import clean_file
from simulation import run_simulation_main

roads = pd.read_csv('../data/_roads3.csv')
bmms = pd.read_excel('../data/BMMS_overview.xlsx')

clean_file(roads, bmms)

df = run_simulation_main()
print(df)