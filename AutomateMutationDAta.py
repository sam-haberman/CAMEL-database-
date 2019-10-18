# Script that will take in a mutation csv from AleDb and convert it to the Camel Mutation format
# Starting by just doing one file
# Then move to go through all files in a folder

import csv
import re
import pandas as pd
# Starting with just opening one file
f = open('C:/Users/samue/Desktop/Thesis/ALEDB_conversion/FilestoConvert/Tee', 'r', encoding='UTF-8')

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
    data[j].insert(4,"")
    if data[j][2] == "SNP":
        temp = data[j][3]
        splitter = re.split("→", temp)
        data[j][3] = splitter[0]
        data[j][4] = splitter[1]
    j += 1
# Loop to do multiple mutations per line
j = 0
while j < len(data):
    o = 7
    k = len(header) + 1
    while o < k :
        if data[j][o] == "1.00":
            stors.append([data[j][0],data[j][1],data[j][2],data[j][3],data[j][4],data[j][5],data[j][6].split(' ')[0],str(Groups[o-7]).split(" ")[0][3:],str(Groups[o-7]).split(" ")[2][1:], "", "", "",""])
            o+=1
        else:
            o+=1
    j+=1
# Final loop to clean up last columns
j = 0
while j < len(stors):
    if stors[j][6] == "coding":
        stors[j][6] = ""
    elif stors[j][6] == "intergenic":
        stors[j][5] = "NA"
        stors[j][6] = ""
    j += 1
df = pd.DataFrame(stors, columns = ["CHROM", "POS", 'TYPE', 'REF', 'ALT', 'GEN', '∆AA', 'POP', 'CLON', 'TIME', 'FREQ', 'COM', "Measure of Time"])
print(df)
df.to_excel('output7.xlsx', index = False)
f.close()
