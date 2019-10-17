# Script that will take in a mutation csv from AleDb and convert it to the Camel Mutation format
# Starting by just doing one file
# Then move to go through all files in a folder

import csv
import re
import pandas as pd
# Starting with just opening one file
f = open('C:/Users/samue/Desktop/Thesis/ALEDB_conversion/FilestoConvert/Mundhada_H_2017', 'r', encoding='UTF-8')

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
data.insert(4, "")
stors = []
temp = data[0][3]
splitter = re.split("→", temp)
data[0][3] = splitter[0]
data[0][4] = splitter[1]
print(data[0])
# # Loop to do Type of Mutation
# j = 0
# while j < len(data):
#     if data[j][2] == "SNP":
#         temp = data[j][3]
#         splitter = re.split("→", temp)
#         data[j][3] = splitter[0]
#         data[j].insert(splitter[1], 3)

# Loop to do multiple mutations per line
j = 0
while j < len(data):
    o = 7
    k = len(header)
    while o < k:
        if data[j][o] == "1.00":
            stors.append([data[j][0],data[j][1],data[j][2],data[j][3],data[j][4],data[j][5],data[j][6],str(Groups[o-7]), "", "", "", "",""])
            o+=1
        else:
            o+=1
    j+=1

df = pd.DataFrame(stors, columns = ["CHROM", "POS", 'TYPE', 'REF', 'ALT', 'GEN', '∆AA', 'POP', 'CLON', 'TIME', 'FREQ', 'COM', "Measure of Time"])
print(df)
df.to_excel('output4.xlsx', index = False)
f.close()
