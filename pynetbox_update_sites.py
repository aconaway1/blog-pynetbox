"""
Add sites to Netbox based on a YAML file
"""
import pynetbox
import yaml

ENV_FILE = "env.yml"
SITES_FILE = "sites.yml"

with open(ENV_FILE) as file:
    env_vars = yaml.safe_load(file)
    
with open(SITES_FILE) as file:
    sites_to_load = yaml.safe_load(file)
    
nb_conn = pynetbox.api(url=env_vars['netbox_url'])

token = nb_conn.create_token(env_vars['username'], env_vars['password'])

for site in sites_to_load:
    are_they_different = False
    print(f"Checking {site['name']} for updates...", end="")
    queried_site = nb_conn.dcim.sites.get(name=site['name'].upper())
    if not queried_site:
        print(f"Site {site['name']} does not exist. I'm choosing not to add it.")
        continue
    for key in site.keys():
        if site[key] != queried_site[key]:
            are_they_different = True
    if are_they_different:
        print("looks like it's different. Will update.")
        queried_site.update(site)
    else:
        print("seems to be the same.")
        continue
    
token.delete()