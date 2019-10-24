import requests as req
#Thomas' script to refer to how the api works
'''
This is a simple script to demonstrate the editing API 
of CAMEL. If you run it one line at a time, you can see
how different entities are added, updated and removed.
At the end of the script, the db should be back in its original
state.
Request types:
'GET': retrieve one or more entities as described in the README
'POST': inserts a new experiment or field
'PUT': update an existing experiment or field given the id
'DELETE': remove an existing experiment, field or reference given the id
References can be added and updated as a part of an experiment.
Removing a field will automatically remove all data of that type, just like
removing an experiment will also delete its field data. Orphan references
(references that are not linked to any experiment anymore) are
automatically removed as well.
'''
# URLS

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

#WE need to know the id of the experiment that we want to update

exp_id = ""

added_exp__url = exp_url + "/" + str(exp_id)

# Field value id's will not be assigned yet, until we request the complete object again
added_experiment = req.get(added_exp__url).json()

# Lets update the Species field. We only need the changing fields and the ids of their values.
species_value_ids = list(added_experiment['fields']['1'].keys())

update_experiment = {
    'fields': {
        '1': {
            species_value_ids[0]: 'We update this species',
            species_value_ids[1]: {'action': 'delete'},  # we delete the second value
            'new_1': 'Adding yet another species'
        }
    }
}


# Send the updates
req.put(added_exp__url, headers=auth_header, json=update_experiment)
