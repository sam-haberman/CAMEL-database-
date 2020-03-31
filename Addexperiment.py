import urllib

import requests as req
import pandas as pd
import re
import os
import time
import mechanize
import win32com.client

from MutFunc_functionality import extract_files
from MutFunc_functionality import runmutfunc
import zipfile
path = ""
# Create function to pull all data from excel file, log in and add experiment
# Also includes function to attach mutation data to an experiment


# If there are multiple entries for a field, such as having multiple species in the experiment, these entries need to
# be separated by a comma in the excel template file in order for them to be properly added

# We need to update script so that you can also include a mutation file with it and that file joins the mutation field
def get_data_and_add_experiment(file, mutfile =""):

    df = pd.read_excel(file, skiprows=4)
    df = df.fillna("")
    # Take each value that was included as part of the metadata and is not left blank
    val = df.loc[0, :].values.tolist()
    # Convert data to proper type for updating to database (making everything JSON serializable)
    integer_fields = [3, 16, 17, 25, 27, 28, 29, 32, 33]
    bool_fields = [8, 10, 12, 14, 19, 23, 40]
    double_fields = [30]
    entry = 0
    while entry < len(val):
        if val[entry] != "":
            if entry in integer_fields:
                val[entry] = int(val[entry])
            elif entry in bool_fields:
                val[entry] = bool(val[entry])
            elif entry in double_fields:
                val[entry] = float(val[entry])
        entry += 1

    # Create fields dictionary and check for multiple entries by looking for a semicolon
    start = 1
    fielddict = {}
    counter = 1
    while start < len(val)-3:
        if val[start] != '':
            fielddict[str(start)] = {}
            if isinstance(val[start], str):
                comma_check = re.split(";", val[start])
                for element in comma_check:
                    fielddict[str(start)]['new_' + str(counter)] = element
                    counter += 1
            else:
                fielddict[str(start)] = {'new_' + str(counter): val[start]}
                counter += 1
        start += 1
    # print(fielddict)

    # Get Reference information
    pubmed_id = val[-2]
    if pubmed_id == "":
        pubmed_id = None
    pubmed_url = val[-1]
    # Add a new experiment
    '''
    Adding or updating an element needs a dict that mimics
    the JSON format like a GET request would return

    Field values key/value pairs that do not have a generated ID yet, use a
    random id that is prefixed with 'new_'.
    '''

    base_url = "https://cameldatabase.com/CAMEL/"
    api_url = base_url + "api"
    auth_url = base_url + "auth"
    exp_url = api_url + "/experiment"
    field_url = api_url + "/field"
    ref_url = api_url + "/reference"
    attach_url = api_url + '/attachment'
    # Credentials

    login = ''
    password = ''

    if not password:
        import getpass
        password = getpass.getpass()

    # Get an authentication token
    '''
    All editing operations require a header containing a valid AuthToken.
    A token stays valid for one day.
    '''
    auth_request = req.get(auth_url, auth=(login, password))
    token = auth_request.headers['AuthToken']

    # Create the header we are going to send along
    auth_header = {'AuthToken': token}

    new_experiment = {
        'name': df["NAME"][0],  # the only required attribute
        # key value pairs with field id as key
        'fields': fielddict,
        'references': [
            # {
            #     # By default, references need a reference ID and the complete reference data
            #     # with __all reference fields__ (see get results) to do an UPDATE
            #     # This behavior can be changed by the 'action' attribute: 'new' (post, without ref id)
            #     # or 'link' or 'delete' (with existing ref id)
            #     'id': '11954',
            #     'action': 'link'  # link existing paper to this experiment
            # },
            {
                'action': 'new',  # a completely new paper
                'authors': "a list of authors goes here",
                'title': 'this is the title of the new paper',
                'journal': 'Journal Abbr.',
                'year': '2019',
                'pages': '',
                'pubmed_id': pubmed_id,
                'url': pubmed_url
            }
        ]
    }

    # Send the new experiment data
    # It will be added to the database
    # The JSON answer will be the same experiment, but with an assigned ID
    answer = req.post(exp_url, headers=auth_header, json=new_experiment).json()
    exp_id = answer['id']
    added_exp_url = exp_url + "/" + str(exp_id)

    # we check to see if there is a mutation file attached so we can upload it after the experiment is added, file needs
    # to be .xlsx
    if mutfile != "":
        ##We upload the file to a temporary location on the server
        attachment = {'file': open(mutfile, 'rb')}
        resp = req.post(attach_url, files=attachment, headers=auth_header)

        ##Get the temporary id of the upload
        tmp_uuid = resp.json()['uuid']

        ##Set the attachment field to the tmp id and name the file
        ##The file will be moved to the correct location
        dest_file_name = "Mutation Data.xlsx"
        attach_exp = {
            'fields': {
                '36': {
                    'new_1': {
                        'uuid': tmp_uuid,
                        'filename': dest_file_name}
                }
            }
        }
        resp = req.put(added_exp_url, headers=auth_header, json=attach_exp)
    # Field value id's will not be assigned yet, until we request the complete object again
    added_experiment = req.get(added_exp_url).json()

    # Last we check to see if a mutation file was attached and then if it qualifies, we have to check the Species
    # to see if it is E. Coli or Yeast(eventually) and then also check to see what the strain is since we only work on
    # the standard most popular strain for both
    # First we have to check the species(starting with just E. Coli)
    if val[1] == "Escherichia coli" and mutfile != "":
        # check the strain of E. Coli, need to add Yeast or update so its more than just the E. Coli NC number
        mut_df = pd.read_excel(mutfile, sheet_name='Sheet1')
        if mut_df.loc[1, "CHROM"] == "NC_000913":
            mut_func_file = runmutfunc(mutfile)
            # Update our mutation excel file with the Mutfunc results and return it as a new file
            updated_mutation_dataframe = extract_files(mut_func_file, mut_df)
            updated_mutation_dataframe.to_excel("Mutation_results.xlsx", index=False)
            print(os.getcwd())
            print(os.listdir())
            # testing code to add comments
            xl = win32com.client.Dispatch("Excel.Application")
            xl.Visible = 1
            wb = xl.Workbooks.Open(r'C:/Users/samue/PycharmProjects/Thesis/Mutation_results.xlsx')
            sheet = wb.ActiveSheet
            # add comments
            sheets = ["P1", "Q1", "R1", "S1", "T1", "U1", "V1", "W1", "X1", "Y1", "Z1", "AA1", "AB1",
                      "AC1", "AD1", "AE1"]
            comments = ["Reference amino acid", "Mutated amino acid",
                        "Is the mutation predicted to impact function? '1' if yes, '0' if no",
                        "Sift score, any mutation with a score below 0.05 is considered deleterious ",
                        "Information content at this position of the alignment (a high value indicates strong conservation, where the maximum value is 4.32)",
                        "Predicted change in free energy of unfolding, where a value above 0 indicates a destabilising mutation",
                        "Pdb identifier or homology model identifier of the structure containing the mutation",
                        "Sequence of the linear motif", "ELM accession for the linear motif",
                        "Type of post-translational modifications", "Function of this phosphorylation site, if any",
                        "Evidence of site function, if any", "Kinase predicted to lose phosphorylation at this site",
                        "Probability of kinase losing phosphorylation at this site",
                        "P-value of over or under-expression for the downstream gene when the transcription factor is knocked out",
                        "Transcription factor predicted to bind this binding site"]
            for column, comment in zip(sheets, comments):
                sheet.Range(column).AddComment()
                sheet.Range(column).Comment.Visible = False
                sheet.Range(column).Comment.Text(comment)
            wb.SaveAs(r'C:\Users\samue\PycharmProjects\Thesis\Mutation_results_complete.xlsx')
            wb.Close()
            xl.Quit()

            # add this file to the zip file of mutation results
            zip_open = zipfile.ZipFile(mut_func_file, 'a')
            zip_open.write("Mutation_results_complete.xlsx")
            zip_open.close()
            # We upload the file to a temporary location on the server (STUCK HERE)
            attachment = {'file': open(mut_func_file, 'rb')}
            resp = req.post(attach_url, files=attachment, headers=auth_header)

            # Get the temporary id of the upload
            tmp_uuid = resp.json()['uuid']

            # Set the attachment field to the tmp id and name the file
            # The file will be moved to the correct location
            dest_file_name = "Complete MutFunc Results.gz"
            attach_exp = {
                'fields': {
                    '44': {
                        'new_1': {
                            'uuid': tmp_uuid,
                            'filename': dest_file_name}
                    }
                }
            }
            resp = req.put(added_exp_url, headers=auth_header, json=attach_exp)
# Function to add mutation data to experiments, needs to be .xlsx

def add_mutation_to_experiment(mutation_file):
    ## URLS
    base_url = "https://cameldatabase.com/CAMEL/"
    api_url = base_url + "api"
    auth_url = base_url + "auth"

    exp_url = api_url + "/experiment"
    attach_url = api_url + '/attachment'

    ## Credentials
    login = ''
    password = ''

    if not password:
        import getpass
        password = getpass.getpass()

    ## Get an authentication token
    '''
    All editting operations require a header containing a valid AuthToken.
    A token stays valid for one day.
    '''
    auth_request = req.get(auth_url, auth=(login, password))
    token = auth_request.headers['AuthToken']

    # Create the header we're going to send along
    auth_header = {'AuthToken': token}

    # Get experiment ID from the given file, always needs to be experimentID double _ then file name which should be
    # name of experiment
    file_name = re.split("/", mutation_file)
    file_name = file_name[-1]
    eid = re.split("_", file_name)
    eid = eid[0]

    local_file_name = mutation_file
    exp_id = eid
    added_exp_url = exp_url + '/' + str(exp_id)

    # We upload the file to a temporary location on the server
    attachment = {'file': open(local_file_name, 'rb')}
    resp = req.post(attach_url, files=attachment, headers=auth_header)

    # Get the temporary id of the upload
    tmp_uuid = resp.json()['uuid']

    # Set the attachment field to the tmp id and name the file
    # The file will be moved to the correct location
    dest_file_name = "Mutation Data.xlsx"
    attach_exp = {
        'fields': {
            '36': {
                'new_1': {
                    'uuid': tmp_uuid,
                    'filename': dest_file_name}
            }
        }
    }
    resp = req.put(added_exp_url, headers=auth_header, json=attach_exp)
    if resp.ok:
        print("Upload successful")
    else:
        print("Upload failed")

    # Now that we attached the mutation data we want to add mutFunc
    # first we have to check the species to see if it is E. coli
    # To do so we use the api and pull the experiment information
    # to check if E. coli or Escherichia coli is a listed species
    experiments = req.get("https://cameldatabase.com/CAMEL/api/experiment/" + eid).json()
    for key, value in experiments.get("fields").get("1").items():
        if "Escherichia coli" in value:
            # check the strain of E. Coli, need to add Yeast or update so its more than just the E. Coli NC number
            mut_df = pd.read_excel(mutation_file, sheet_name='Sheet1')
            if mut_df.loc[1, "CHROM"] == "NC_000913":
                mut_func_file = mut_func_info(mutation_file)
                # We upload the file to a temporary location on the server
                attachment = {'file': open(mut_func_file, 'rb')}
                resp = req.post(attach_url, files=attachment, headers=auth_header)

                # Get the temporary id of the upload
                tmp_uuid = resp.json()['uuid']

                # Set the attachment field to the tmp id and name the file
                # The file will be moved to the correct location
                dest_file_name = "Complete MutFunc Results.gz"
                attach_exp = {
                    'fields': {
                        '44': {
                            'new_1': {
                                'uuid': tmp_uuid,
                                'filename': dest_file_name}
                        }
                    }
                }
                resp = req.put(added_exp_url, headers=auth_header, json=attach_exp)

def remove_experiment(eid):

    ## URLS
    base_url = "https://cameldatabase.com/CAMEL/"
    api_url = base_url + "api"
    auth_url = base_url + "auth"

    exp_url = api_url + "/experiment"
    field_url = api_url + "/field"
    ref_url = api_url + "/reference"

    ## Credentials
    login = ''
    password = ''

    if not password:
        import getpass
        password = getpass.getpass()

    ## Get an authentication token
    '''
    All editting operations require a header containing a valid AuthToken.
    A token stays valid for one day.
    '''
    auth_request = req.get(auth_url, auth=(login, password))
    token = auth_request.headers['AuthToken']

    ## Create the header we're going to send along
    auth_header = {'AuthToken': token}

    exp_id = eid
    added_exp_url = exp_url + '/' + str(exp_id)
    req.delete(added_exp_url, headers=auth_header)

# function that if an experiment is added/updated with mutation data it checks to see if the species is E. Coli (Yeast
# eventually) and if it is the standard strain. If so we add the MutFunc prediction results to the field and eventually
# we want to add a button that gives live results too to the experiment page.
def mut_func_info(mutfile):
    df = pd.read_excel(mutfile)
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
    # cannot figure out how to have the url updated from the wait page to the results page, even though it is redirected
    # so we will just set an arbitrarily long wait time where we then assume that the loading as finished and we move to
    # the export page which lets us download the files
    # Here we pause for 3 minutes (can be changed) before switching our page to the results
    time.sleep(40)
    new_url = str(base_url).replace("wait", "export")
    urllib.request.urlretrieve(new_url, mutfile + ".gz")
    mut_func_file = mutfile + ".gz"
    # Here we then want to save this file so that it can be added to the field when experiments are added or mutation
    # data is attached
    return mut_func_file


# remove_experiment(780)
# Have to give file with experiment information and either leave id blank or give a number
get_data_and_add_experiment('C:/Users/samue/Desktop/Thesis/metadatatemplateUPDATE.xlsx',
                            "C:/Users/samue/Desktop/Thesis/42C.csv.xlsx")
#get_data_and_add_experiment('C:/Users/samue/Desktop/Thesis/metadatatemplateUPDATE.xlsx')
# Adding experiments from a folder rather than individually
#  for fname in glob.glob(path + '\\*'):
#     get_data_and_add_experiment(fname,)

#add_mutation_to_experiment('C:/Users/samue/Desktop/Thesis/35_42C.csv.xlsx')

