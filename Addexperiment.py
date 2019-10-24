import requests as req
import pandas as pd
import numpy as np
#first we pull data from our excel file
df = pd.read_excel('C:/Users/samue/Desktop/Thesis/metadatatemplate.xlsx', skiprows= 4)
df = df.fillna("")
print(df)
print(df['NAME'][0])

val = df.loc[0,:].values.tolist()
print(val)
start = 1
fielddict = {}
while start < len(val):
    if val[start] != '':
        fielddict[str(start)] = val[start]
    start +=1
print(fielddict)
def makefields(alist):
    tet = 'fields'

# # URLS
#
# base_url = "https://cameldatabase.com/CAMEL/"
# api_url = base_url + "api"
# auth_url = base_url + "auth"
#
# exp_url = api_url + "/experiment"
# field_url = api_url + "/field"
# ref_url = api_url + "/reference"
#
# # Credentials
#
# login = ''
# password = ''
#
# if not password:
#     import getpass
#     password = getpass.getpass()
#
# # Get an authentication token
# '''
# All editing operations require a header containing a valid AuthToken.
# A token stays valid for one day.
# '''
# auth_request = req.get(auth_url, auth=(login, password))
# token = auth_request.headers['AuthToken']
#
# # Create the header we are going to send along
# auth_header = {'AuthToken': token}
#

# Add a new experiment
'''
Adding or updating an element needs a dict that mimics
the JSON format like a GET request would return

Field values key/value pairs that do not have a generated ID yet, use a
random id that is prefixed with 'new_'.
'''



new_experiment = {
    'name': df["NAME"][0],  # the only required attribute
    # key value pairs with field id as key
    'fields': {
        '1': {
            'new_1': "My new species",
            'new_2': "Another new species"
        },
        '2': {
            'new_3': "The goal of this experiment"
        },
        '34': {
            'new_4': "The major outcome of this experiment can be described here"
        },
        '10': {
            'new_5': 0  # no, there is NO changing environment
        }
    },
    # list of linked references
    'references': [
        {
            # By default, references need a reference ID and the complete reference data
            # with __all reference fields__ (see get results) to do an UPDATE
            # This behavior can be changed by the 'action' attribute: 'new' (post, without ref id)
            # or 'link' or 'delete' (with existing ref id)
            'id': '11954',
            'action': 'link'  # link existing paper to this experiment
        },
        {
            'action': 'new',  # a completely new paper
            'authors': "a list of authors goes here",
            'title': 'this is the title of the new paper',
            'journal': 'Journal Abbr.',
            'year': '2019',
            'pages': '',
            'pubmed_id': '',
            'url': ''
        }
    ]
}
