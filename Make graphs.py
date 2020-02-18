import requests
import pandas as pd
# Script to download files needed for poster creation from the API

experiments = requests.get("https://cameldatabase.com/CAMEL/api/field/17").json()

df1 = pd.DataFrame.from_dict(experiments)


df1.to_excel("Making_graphs1" + '.xlsx', index=False)