import requests as req
import pandas as pd

# Create function to pull all data from excel file, log in and add experiment with or without a given experiment id


def get_data_and_add_experiment(file,eid):

    df = pd.read_excel(file, skiprows=4)
    df = df.fillna("")
    # Take each value that was included as part of the metadata and is not left blank
    val = df.loc[0, :].values.tolist()
    # Create fields dictionary
    start = 1
    fielddict = {}
    counter = 1
    while start < len(val)-3:
        if val[start] != '':
            fielddict[str(start)] = {'new_' + str(counter): val[start]}
            counter += 1
        start += 1

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
        #     {
        #     '1': {
        #         'new_1': "My new species",
        #         'new_2': "Another new species"
        #     },
        #     '2': {
        #         'new_3': "The goal of this experiment"
        #     },
        #     '34': {
        #         'new_4': "The major outcome of this experiment can be described here"
        #     },
        #     '10': {
        #         'new_5': 0  # no, there is NO changing environment
        #     }
        # },
        # list of linked references
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
                'pubmed_id': val[-2],
                'url': val[-1]
            }
        ]
    }

    # Send the new experiment data
    # It will be added to the database
    # The JSON answer will be the same experiment, but with an assigned ID
    if eid == "":
        answer = req.post(exp_url, headers=auth_header, json=new_experiment).json()
        exp_id = answer['id']
        added_exp__url = exp_url + "/" + str(exp_id)
    else:
        exp_id = eid
        added_exp__url = exp_url + "/" + str(exp_id)

    # Field value id's will not be assigned yet, until we request the complete object again
    added_experiment = req.get(added_exp__url).json()

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

#remove_experiment(id)
# Have to give file with experiment information and either leave id blank or give a number
get_data_and_add_experiment('C:/Users/samue/Desktop/Thesis/metadatatemplate.xlsx',)
