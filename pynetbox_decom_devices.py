"""
Deletes devices from Netbox after an indicated date in the description field
"""
import re
from datetime import datetime
import pynetbox
import yaml

ENV_FILE = "env.yml"

# Load the environment information
with open(ENV_FILE, encoding="UTF-8") as file:
    env_vars = yaml.safe_load(file)
# Connect to Netbox and get a token
nb_conn = pynetbox.api(url=env_vars['netbox_url'])
my_token = nb_conn.create_token(env_vars['username'], env_vars['password'])
# Get a list of all the devices with a status of "decommission"
decommed_devices = nb_conn.dcim.devices.filter(status="decommissioning")
# Get today's date to do some math on later
todays_date = datetime.now()
# Go through the list of devices returned
for decommed_device in decommed_devices:
    # Do a regex search for "delete after " with some text
    date_search = re.search("delete after (.+)", decommed_device.description)
    # If you found a match to the regex
    if date_search:
        # Format the "delete after" date
        delete_date = datetime.strptime(date_search.group(1), '%d %b %Y')
        # If today's date is after the "delete after" date
        if todays_date > delete_date:
            # Tell us we're going to delete stuff
            print(f"Deleting the device {decommed_device.name}...", end="")
            # Delete the device. You should get a True back
            result = decommed_device.delete()
            # If everything went fine
            if result:
                print("...deleted.")
            # If it didn't delete
            else:
                print("failed.")
# Delete the token we're using to work with Netbox
my_token.delete()
