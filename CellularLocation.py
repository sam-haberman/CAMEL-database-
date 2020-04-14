# Will add a second source of data to researchers on CAMEL by providing information on the sub-cellular location of the
# genes that are being mutated, as well as functional gene ontology annotation. CELLO2GO


import pandas as pd
import re
import time
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pyperclip
import os
from zipfile import ZipFile
import pyautogui
import shutil


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
        return "False"
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
# file, mechanize doesn't work so going to try selenium
# Depending on the browser you use you need to add an executable such as geckodriver (firefox) or chrome driver(chrome)
# to PATH, have to download file from https://github.com/mozilla/geckodriver/releases/tag/v0.26.0 (firefox)
# or https://sites.google.com/a/chromium.org/chromedriver/home (chrome) use
# this executable file in the path, Firefox wouldn't automatically save the file so switched to Chrome
# Throughout the function we use time.sleep to have the function wait for pages to load
def cell2go(genes):
    # first we open up our webpage
    path = "C:/Users/samue/Desktop/Thesis/geckodriver/chromedriver.exe"
    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": r"C:\Users\samue\PycharmProjects\Thesis",
        "download.directory_upgrade": "true",
        "download.prompt_for_download": "false",
        "disable-popup-blocking": "true"
    }
    options.add_experimental_option("prefs", prefs)
    browser = webdriver.Chrome(executable_path=path, service_log_path='nul', options=options)
    browser.get("http://cello.life.nctu.edu.tw/cello2go/")
    # Then we clear the content and paste in our string of headers and FASTA sequences before running the search
    paste_sequence = browser.find_element_by_name("sequence")
    paste_sequence.clear()
    pyperclip.copy(genes)
    paste_sequence.send_keys(Keys.CONTROL + "v")
    submit_button = browser.find_element_by_id("do-blast")
    submit_button.click()
    # Now we wait for the page to finish loading before clicking the download button
    wait(browser, 200).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "<div class=loadmask>")))
    download = False
    while not download:
        try:
            download_button = browser.find_element_by_id("Bacteria-mdlbtn")
            download_button.click()
            download = True
            # this gives the website enough time to download the entire file
            time.sleep(20)
            pyautogui.hotkey('ctrl', 's')
            time.sleep(3)
            pyautogui.typewrite("Complete_Location_Results.html")
            pyautogui.hotkey('enter')
            time.sleep(10)
        except ElementClickInterceptedException:
            time.sleep(50)
    browser.close()
    browser.quit()
    Zip_file_results = ZipFile("C:\\Users\\samue\\PycharmProjects\\Thesis\\Cellular_Location_Results.zip", "w")
    current_path = os.getcwd()
    # Have to change this to the default download location of user
    os.chdir("C:\\Users\\samue\\Downloads")
    Zip_file_results.write("Complete_Location_Results.html")
    Zip_file_results.write("Complete_Location_Results_files")
    # File is named weirdly, so renaming it
    os.rename("C:\\Users\\samue\\PycharmProjects\\Thesis\\cello2go_reuslt.txt",
              "C:\\Users\\samue\\PycharmProjects\\Thesis\\cello2go_results.txt")
    os.chdir(current_path)
    Zip_file_results.write("cello2go_results.txt")
    Zip_file_results.close()
    # clean up files after downloading
    os.remove("C:\\Users\\samue\\PycharmProjects\\Thesis\\cello2go_results.txt")
    os.remove("C:\\Users\\samue\\Downloads\\Complete_Location_Results.html")
    shutil.rmtree("C:\\Users\\samue\\Downloads\\Complete_Location_Results_files")
    return "C:\\Users\\samue\\PycharmProjects\\Thesis\\Cellular_Location_Results.zip"


genes = locations("C:/Users/samue/Desktop/Thesis/35_42C.csv.xlsx")
cell2go(genes)