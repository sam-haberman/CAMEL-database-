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
# print(Isolates)
Groups = []
for i in range(len(Isolates)):
    Groups.append(re.findall("[A-Z].*[1-9]", Isolates[i]))
#print(Groups)
data = []
for row in csv_f:
    data.append(row)
print(data)
df = pd.DataFrame(columns = ["CHROM", "POS", 'TYPE', 'REF', 'ALT', 'GEN', '∆AA', 'POP'])
j = 0
while j < len(data):
    if data[j][6]

print(df)
f.close()
