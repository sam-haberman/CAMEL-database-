import requests
import pandas as pd
# Script to download files needed for poster creation from the API

experiments = requests.get("https://cameldatabase.com/CAMEL/api/experiment/1").json()

print(experiments.get("fields").get("1"))
for key, value in experiments.get("fields").get("1").items():
    if "Acinetobacter baumannii" in value:
        print("yes")
# df1 = pd.DataFrame.from_dict(experiments)


#df1.to_excel("Making_graphs1" + '.xlsx', index=False)