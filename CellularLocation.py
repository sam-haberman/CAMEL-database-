# Will add a second source of data to researchers on CAMEL by providing information on the sub-cellular location of the
# genes that are being mutated, as well as functional gene ontology annotation. CELLO2GO


import pandas as pd


# it is possible we can work with strains that are not the most popular since we just want fasta
def locations(file):
    df = pd.read_excel(file, header=4)
    # The first thing to do is to remove all mutations that do not provide the gene that is affected as well as drop
    # duplicates
    genes = df['GEN'] != "NaN"
    print(genes)
    df = df[genes]
    df.drop_duplicates()
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
                gene_dict[gene_name] = seq
                seq = ''
            for item in line.split(" "):
                if 'gene=' in item:
                    gene_name = item.split('=')[1]
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
        final_list += "> %s %s %s %s\n" % (mutation[3], mutation[4], mutation[5], mutation[6])
        print(mutation)
        print(mutation[6])
        final_list += str(gene_dict[mutation[6]]) + "\n"
    return


locations("C:/Users/samue/Desktop/Thesis/35_42C.csv.xlsx")