"""
Add sites to Netbox based on a YAML file
"""
import pynetbox
import yaml

ENV_FILE = "env.yml"
DEV_ROLES_FILE = "device_roles.yml"

with open(ENV_FILE) as file:
    env_vars = yaml.safe_load(file)
    
with open(DEV_ROLES_FILE) as file:
    dev_roles_to_load = yaml.safe_load(file)
    
nb_conn = pynetbox.api(url=env_vars['netbox_url'])

token = nb_conn.create_token(env_vars['username'], env_vars['password'])

for dev_role in dev_roles_to_load:
    queried_dev_role = nb_conn.dcim.device_roles.get(name=dev_role['name'])
    if queried_dev_role:
        print(f"Device role {dev_role['name']} already exists.")
        continue
    print(f"Adding {dev_role['name']} to Netbox.")
    constructed_dev_role = {"name": dev_role['name'], "slug": dev_role['slug']}
    if "description" in dev_role.keys():
        constructed_dev_role['description'] = dev_role['description']
    result = nb_conn.dcim.device_roles.create(constructed_dev_role)
    
token.delete()