import glob
from MutFunc_functionality import extract_files
from MutFunc_functionality import runmutfunc
from CellularLocation import *
from Mechismo_functionality import *
import pandas as pd
path = "C:/Users/samue/Desktop/Thesis/ALEDB_conversion/Experiment_Data"


def Collect_Data(mutfile):
    mut_df = pd.read_excel(mutfile, sheet_name='Sheet1', header=4, keep_default_na=False)
    mut_func_file = runmutfunc(mutfile)
    # Update our mutation excel file with the Mutfunc results and return it as a new file with appropriately
    # detailed headers
    updated_mutation_dataframe = extract_files(mut_func_file, mut_df)
    mechismo_results = run_mechismo(mutfile)
    # Add mechismo results to complete mutation dataframe
    df = pd.merge(updated_mutation_dataframe, mechismo_results, left_on="Start POS", right_on="Start POS",
                  how='left')
    df = df.fillna('')
    list_of_genes = locations(mutfile)
    # check to see if we can run cell2go with this mutation file, if not we end here
    if list_of_genes == "False":
        return
    cell2go_results = cello2go(list_of_genes)
    df = pd.merge(df, cell2go_results, left_on="Start POS", right_on="Start POS", how='left')
    df = df.fillna('')
    # Need to drop duplicates here
    df = df.drop_duplicates()
    df.to_excel(mutfile + "updated.xlsx", index=False)


# Collect_Data("C:/Users/samue/Desktop/Thesis/ALEDB_conversion/Experiment_Data/42CTenaillonAra.csv.xlsx")
# for file in glob.glob("C:/Users/samue/Desktop/Thesis/ALEDB_conversion/Files_for_tools" + '\\*'):
#     try:
#         Collect_Data(file)
#     except:
#         continue