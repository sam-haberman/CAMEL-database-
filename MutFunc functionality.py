# Goal is to take a file of mutation data, retrieve all the unique SNPs from it and run them through
# MutFunc(http://www.mutfunc.com/ to provide extra information to the data providers about their mutations

import pandas as pd

# requires an excel file of mutations that should be obtained from the Camel database experiment page. Since MutFunc
# only works on SNPs the first thing we have to do is remove all non SNPs and only keep unique values

def runmutfunc(file):
    df = pd.read_excel(file)
    # Here we filter to only keep SNP mutations
    is_SNP = df['TYPE'] == "SNP"
    df = df[is_SNP]
    # drop duplicates
    df.drop_duplicates()
    # Take only data from the SNPs that we want for checking in MutFunc
    # Merge all parts together so they can be added as one entry per line
    SNP_list = pd.DataFrame()
    SNP_list["SNPs"] = df["CHROM"] + " " + df["START POS"].astype(str) + " " + df["REF"] + " " + df["ALT"]
    SNP_list.to_csv(file + ".csv")
 # time now to learn how to acess the website through python, looking at the mechanize package


runmutfunc("C:/Users/samue/Desktop/Thesis/ALEDB_conversion/Experiment_Data/42C.csv.xlsx")
