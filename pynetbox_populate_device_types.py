"""
Add sites to Netbox based on a YAML file
"""
import pynetbox
import yaml

ENV_FILE = "env.yml"
MANUFACTURER = {
    "name": "GENERIC",
    "slug": "generic"
}
DEV_TYPE = {
    "model": "GENERIC",
    "slug": "generic"
}

with open(ENV_FILE) as file:
    env_vars = yaml.safe_load(file)
    
nb_conn = pynetbox.api(url=env_vars['netbox_url'])

token = nb_conn.create_token(env_vars['username'], env_vars['password'])

man_result = nb_conn.dcim.manufacturers.create(MANUFACTURER)

DEV_TYPE['manufacturer'] = man_result['id']
type_result = nb_conn.dcim.device_types.create(DEV_TYPE)
    
token.delete()