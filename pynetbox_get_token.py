"""
Demonstrates getting a new token from Netbox
"""
import pynetbox
import pprint
import yaml

ENV_FILE = "env.yml"

with open(ENV_FILE) as file:
    env_vars = yaml.safe_load(file)

nb_conn = pynetbox.api(url=env_vars['netbox_url'])

token = nb_conn.create_token(env_vars['username'], env_vars['password'])

pprint.pprint(dict(token))

token.delete()