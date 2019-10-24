# Script that will take in a mutation csv from AleDb and convert it to the Camel Mutation format
# Starting by just doing one file
# Then move to go through all files in a folder

import csv
import re
import pandas as pd

import glob
path = "C:/Users/samue/Desktop/Thesis/ALEDB_conversion/FilestoConvert/*"

def mutationtransfer(csvfile):

    f = open(csvfile, 'r', encoding='UTF-8')

    csv_f = csv.reader(f)

    Isolates = []
    header = next(csv_f)
    index = 6
    while index < len(header):
        Isolates.append(header[index])
        index += 1
    Groups = []
    for i in range(len(Isolates)):
        Groups.append(re.findall("[A-Z].*[1-9]", Isolates[i]))
    data = []
    for row in csv_f:
        data.append(row)
    stors = []

    # # Loop to do Type of Mutation
    j = 0
    while j < len(data):
        data[j].insert(4, "")
        data[j].insert(2, "")
        if data[j][3] == "SNP":
            temp = data[j][4]
            splitter = re.split("→", temp)
            data[j][4] = splitter[0]
            data[j][5] = splitter[1]
            data[j][2] = int(data[j][1].replace(',', "")) + 1
        if data[j][3] == "DEL":
            if data[j][4][0] == "Δ":
                temp = re.split('Δ', data[j][4])
                newtemp = re.split(" ", temp[1])
                data[j][2] = int(data[j][1].replace(",", "")) + int(newtemp[0].replace(",", ""))
                data[j][4] = ""
                data[j][5] = ""
        if data[j][3] == "INS":
            if data[j][4][0] == "+":
                data[j][5] = re.split("[+]", data[j][4])[1]
                data[j][4] = ""
                data[j][2] = int(data[j][1].replace(',', "")) + len(data[j][5])
            else:
                valuesplit = re.split("→", re.split("[(]|[)]", data[j][4])[2])
                vali = int(valuesplit[1]) - int(valuesplit[0])
                data[j][5] = re.split("[(]|[)]", data[j][4])[1] * vali
                data[j][4] = ""
                data[j][2] = int(data[j][1].replace(',', "")) + len(data[j][5]) * vali
        if data[j][3] == "MOB":
            temp = re.split(" [+]", data[j][4])
            data[j][4] = ""
            data[j][5] = temp[0]
            data[j][2] = int(data[j][1].replace(",", "")) + int(temp[1].split(" ")[0])
        j += 1
    # Loop to do multiple mutations per line
    j = 0
    while j < len(data):
        o = 7
        k = len(header) + 1
        while o < k:
            if data[j][o] == "1.00":
                stors.append(
                    [data[j][0], data[j][1].replace(",", ""), data[j][2], data[j][3], data[j][4], data[j][5], data[j][6],
                     data[j][7].split(' ')[0], str(Groups[o - 7]).split(" ")[0][3:], str(Groups[o - 7]).split(" ")[2][1:],
                     "", "", "", ""])
                o += 1
            else:
                o += 1
        j += 1
    # Final loop to clean up last columns
    j = 0
    while j < len(stors):
        if stors[j][7] == "coding":
            stors[j][7] = ""
        elif stors[j][7] == "intergenic":
            stors[j][6] = "NA"
            stors[j][7] = ""
        elif (stors[j][3] == "DEL") and (stors[j][7] != ""):
            stors[j][12] = stors[j][7]
            stors[j][7] = ""
        j += 1
    df = pd.DataFrame(stors,
                      columns=["CHROM", "START POS", "END POS", 'TYPE', 'REF', 'ALT', 'GEN', '∆AA', 'POP', 'CLON', 'TIME',
                               'FREQ', 'COM', "Measure of Time"])
    #print(df)
    df.to_excel(fname +'.xlsx', index=False)
    f.close()


for fname in glob.glob(path):
    mutationtransfer(fname)
