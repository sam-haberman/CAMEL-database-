import glob
import pandas as pd
path = "C:/Users/samue/Desktop/Thesis/ALEDB_conversion/Experiment_Data"


df = pd.DataFrame()
for file in glob.glob(path + '\\*'):
    data = pd.read_excel(file, "Sheet1")
    df = df.append(data)

print(df)