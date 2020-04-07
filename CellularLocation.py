# Will add a second source of data to researchers on CAMEL by providing information on the sub-cellular location of the
# genes that are being mutated, as well as functional gene ontology annotation. CELLO2GO


import pandas as pd
import re
import mechanize
import time

# it is possible we can work with strains that are not the most popular since we just want fasta
def locations(file):
    df = pd.read_excel(file, header=4, keep_default_na=False)
    # The first thing to do is to remove all mutations that do not provide the gene that is affected as well as drop
    # duplicates
    genes = df['GEN'] != "NA"
    df = df[genes]
    df = df.drop_duplicates()
    df = df.reset_index()
    df = df.drop(columns="index")
    # only works for four strains downloaded
    strain_id = df.loc[1, "CHROM"]
    if strain_id == "NC_000913":
        reference_genome = open("C:/Users/samue/Desktop/Thesis/ReferenceGenomes/EcoliNC000913.txt", 'r', encoding='UTF-8')
    elif strain_id == "NC_007779":
        reference_genome = open("C:/Users/samue/Desktop/Thesis/ReferenceGenomes/EscherichiacoliNC007779.txt", 'r', encoding='UTF-8')
    elif strain_id == "REL606":
        reference_genome = open("C:/Users/samue/Desktop/Thesis/ReferenceGenomes/EscherichiacoliBstr.REL606.txt", 'r',
                                encoding='UTF-8')
    elif strain_id == "CP009273":
        reference_genome = open("C:/Users/samue/Desktop/Thesis/ReferenceGenomes/EColiCP009273.txt", 'r',
                                encoding='UTF-8')
    # If none of these strains are in our dataset we end the function
    else:
        print("This strain of E. coli is not available right now")
        return
    # creates dictionary for our reference strain with key gene name and value fasta sequence
    gene_dict = {}
    gene_name = None
    seq = ''
    take_seq = False
    for line in reference_genome:
        if line.startswith(">") and strain_id in line:
            if gene_name and not seq == '':
                gene_dict[gene_name.replace("-", "")] = seq
                seq = ''
            for item in line.split(" "):
                if 'gene=' in item:
                    gene_name = item.split('=')[1].strip("[]")
                    take_seq = True
        elif line.startswith(">") and strain_id not in line:
            take_seq = False
        else:
            if take_seq:
                seq += line.strip('\r\n')
    if gene_name and not seq == "":
        gene_dict[gene_name] = seq
    # collect all fasta sequences for each gene in our mutation list
    final_list = ""
    for rownumber, mutation in df.iterrows():
        for gene in re.split(', |;', mutation[6]):
            final_list += "> %s %s %s %s %s %s\n" % (mutation[3], mutation[4], mutation[5], gene, mutation[8], mutation[9])
            try:
                final_list += str(gene_dict[gene]) + "\n"
            except KeyError:
                gene_synonyms = open("C:/Users/samue/Desktop/Thesis/ReferenceGenomes/Ecoli_gene_synonyms.tab", 'r',
                                    encoding='UTF-8')
                for line in gene_synonyms:
                    if gene in line:
                        names = line.split("\t")[1]
                        for name in names.split(" "):
                            try:
                                final_list += str(gene_dict[name]) + "\n"
                                break
                            except KeyError:
                                continue
                        break
                gene_synonyms.close()
    return final_list


# Now that we have the list of genes and their annotations we submit them to the cell2go website and get the resulting
# file
def cell2go(genes):
    br = mechanize.Browser()
    br.open("http://cello.life.nctu.edu.tw/cello2go/")
    br.select_form(nr=1)
    br.form['sequence'] = genes
    br.submit()
    time.sleep(20)
    for l in br.links():
        print(l)
    return


genes = locations("C:/Users/samue/Desktop/Thesis/35_42C.csv.xlsx")
cell2go(genes)
