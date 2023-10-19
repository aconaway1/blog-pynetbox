"""
Add devices to Netbox based on a YAML file
"""
import pynetbox
import yaml

ENV_FILE = "env.yml"
DEVICES_FILE = "devices.yml"

with open(ENV_FILE) as file:
    env_vars = yaml.safe_load(file)
    
with open(DEVICES_FILE) as file:
    devices_to_load = yaml.safe_load(file)
    
nb_conn = pynetbox.api(url=env_vars['netbox_url'])

token = nb_conn.create_token(env_vars['username'], env_vars['password'])

valid_devices_status = []
for choice in nb_conn.dcim.devices.choices()['status']:
    valid_devices_status.append(choice['value'])

for device in devices_to_load:
    name = device['name'].upper()
    slug = device['name'].lower()
    
    # See if the device already exists
    queried_device = nb_conn.dcim.devices.get(name=name)
    if queried_device:
        print(f"The device {name} already exists. Skipping.")
        continue
    
    # See if the given device type exists
    dev_type = device['type'].upper()
    queried_type = nb_conn.dcim.device_types.get(model=dev_type)
    if isinstance(queried_type, type(None)):
        print(f"The type {dev_type} does not exist. Skipping.")
        continue
    
    # See if the given device role exists
    dev_role = device['role'].upper()
    queried_role = nb_conn.dcim.device_roles.get(name=dev_role)
    if isinstance(queried_role, type(None)):
        print(f"The role {dev_role} does not exist. Skipping.")
        continue
    
    # See if the given site exists
    site = device['site'].upper()
    queried_site = nb_conn.dcim.sites.get(name=site)
    if isinstance(queried_site, type(None)):
        print(f"The site {site} does not exist. Skipping.")
        continue
    
    
    constructed_device = {"name": name, "slug": slug, "site": queried_site.id, "role": queried_role.id, "device_type": queried_type.id}
    if "description" in device.keys():
        constructed_device['description'] = device['description']
    if "status" in device.keys():
        if device['status'] in valid_devices_status:
            constructed_device['status'] = device['status']
        else:
            print(f"The status of {device['status']} isn't valid. Skipping.")
            continue
    print(f"Adding {device['name']} to Netbox.")
    result = nb_conn.dcim.devices.create(constructed_device)
    
token.delete()