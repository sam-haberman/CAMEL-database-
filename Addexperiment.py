import requests as req
import pandas as pd
import re
import glob
path = ""
# Create function to pull all data from excel file, log in and add experiment with or without a given experiment id
# Also includes function to attach mutation data to an experiment


# If there are multiple entries for a field, such as having multiple species in the experiment, these entries need to
# be separated by a comma in the excel template file in order for them to be properly added

def get_data_and_add_experiment(file, eid=""):

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
    print(fielddict)

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
    if eid == "":
        answer = req.post(exp_url, headers=auth_header, json=new_experiment).json()
        # print(answer)
        exp_id = answer['id']
        added_exp__url = exp_url + "/" + str(exp_id)
    # else:
    #     exp_id = eid
    #     added_exp__url = exp_url + "/" + str(exp_id)
    #     req.post(added_exp__url, headers=auth_header, json=new_experiment).json()

    # Field value id's will not be assigned yet, until we request the complete object again
    added_experiment = req.get(added_exp__url).json()

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

    ##We upload the file to a temporary location on the server
    attachment = {'file': open(local_file_name, 'rb')}
    resp = req.post(attach_url, files=attachment, headers=auth_header)

    ##Get the temporary id of the upload
    tmp_uuid = resp.json()['uuid']

    ##Set the attachment field to the tmp id and name the file
    ##The file will be moved to the correct location
    dest_file_name = "Mutation Data"
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

#remove_experiment(756)
# Have to give file with experiment information and either leave id blank or give a number
#get_data_and_add_experiment('C:/Users/samue/Desktop/Thesis/metadatatemplateUPDATE.xlsx',)

# Adding experiments from a folder rather than individually
#  for fname in glob.glob(path):
#     get_data_and_add_experiment(fname,)

#add_mutation_to_experiment('C:/Users/samue/Desktop/Thesis/100__test_Tee.xlsx')

