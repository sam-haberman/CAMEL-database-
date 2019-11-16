# Script to take data from API and export to Excel so I can get relevant information rather than hand searching through
# the database
import json

result = json.loads("https://cameldatabase.com/CAMEL/api/experiment?1=Saccharomyces%20cerevisiae")
print(result['name'])