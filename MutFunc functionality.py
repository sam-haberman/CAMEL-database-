# Goal is to take a file of mutation data, retrieve all the unique SNPs from it and run them through
# MutFunc(http://www.mutfunc.com/ to provide extra information to the data providers about their mutations
# This script is ideally attached to the button the experiment page that will return fresh data to the user on demand
import pandas as pd
import re
import mechanize



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
    SNP_list["SNPs"] = "chr" + " " + df["START POS"].astype(str) + " " + df["REF"] + " " + df["ALT"]
    # time now to learn how to access the website through python, looking at the mechanize package
    br = mechanize.Browser()
    br.open("http://www.mutfunc.com/submit#")
    br.select_form(nr=0)
    species = br.form.find_control("tax_id")
    for item in species.items:
        if item.name == "2":
            item.selected = True
    mutations = ""
    for i in range(len(SNP_list)):
        mutations = mutations + SNP_list["SNPs"].iloc[i] + "\n"
    br.form['muts_text'] = mutations
    br.submit()
    base_url = br.geturl()
    print(base_url)




runmutfunc("C:/Users/samue/Desktop/Thesis/ALEDB_conversion/Experiment_Data/42C.csv.xlsx")
