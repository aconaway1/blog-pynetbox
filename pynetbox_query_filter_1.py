"""
Show all devices in Netbox grouped by site
"""
import pynetbox
import yaml

ENV_FILE = "env.yml"

with open(ENV_FILE) as file:
    env_vars = yaml.safe_load(file)

nb_conn = pynetbox.api(url=env_vars['netbox_url'])
token = nb_conn.create_token(env_vars['username'], env_vars['password'])

sites = nb_conn.dcim.sites.all()

for site in sites:
    site_header = f"\nDevices at site {site.name} ({site.description})"
    print(site_header)
    print("-" * len(site_header))
    devices = nb_conn.dcim.devices.filter(site_id=site.id)
    if len(devices) < 1:
        print("No devices.")
        continue
    for device in devices:
        print(f"{device.name:^20} {device.device_role.name:^20}")
        
token.delete()