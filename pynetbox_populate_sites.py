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
    name = site['name'].upper()
    slug = site['name'].lower()
    queried_site = nb_conn.dcim.sites.get(name=name)
    if queried_site:
        print(f"Site {site['name']} already exists.")
        continue
    print(f"Adding {site['name']} to Netbox.")
    constructed_site = {"name": name, "slug": slug}
    if "description" in site.keys():
        constructed_site['description'] = site['description']
    if "physical_address" in site.keys():
        constructed_site['physical_address'] = site['physical_address']
    result = nb_conn.dcim.sites.create(constructed_site)
    
token.delete()