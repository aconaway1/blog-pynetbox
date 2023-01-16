"""
Create a shipping label for planned devices
"""
import pynetbox
import yaml

ENV_FILE = "env.yml"

with open(ENV_FILE) as file:
    env_vars = yaml.safe_load(file)

nb_conn = pynetbox.api(url=env_vars['netbox_url'])
token = nb_conn.create_token(env_vars['username'], env_vars['password'])

devices = nb_conn.dcim.devices.filter(status='planned')

for device in devices:
    site = nb_conn.dcim.sites.get(id=device.site.id)
    print(f"Ship {device.name} to:\n{site.physical_address}\n")
        
token.delete()