"""
Show planned devices in Netbox grouped by site
"""
import pynetbox
import yaml
import requests

ENV_FILE = "env.yml"

with open(ENV_FILE) as file:
    env_vars = yaml.safe_load(file)

nb_conn = pynetbox.api(url=env_vars['netbox_url'])
token = nb_conn.create_token(env_vars['username'], env_vars['password'])

choices = nb_conn.dcim.devices.choices()['status']

valid_statuses = []
for status in choices:
    valid_statuses.append(status['value'])
    
print (valid_statuses)

token.delete()