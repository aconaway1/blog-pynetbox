"""
Add prefixes to Netbox based on a YAML file
"""
import pynetbox
import yaml

ENV_FILE = "env.yml"
PREFIXES_FILE = "prefixes.yml"

with open(ENV_FILE) as file:
    env_vars = yaml.safe_load(file)
    
with open(PREFIXES_FILE) as file:
    prefixes_to_load = yaml.safe_load(file)

# Log in to Netbox and create a token based on creds    
nb_conn = pynetbox.api(url=env_vars['netbox_url'])
token = nb_conn.create_token(env_vars['username'], env_vars['password'])

# Go through all the prefixes in the `global` dictionary
for global_container in prefixes_to_load['global']:
    # Track if the prefix already exists
    found_a_prefix = False
    # Ask Netbox if it already exists
    queried_prefixes = nb_conn.ipam.prefixes.filter(prefix=global_container['prefix'])
    # Go through the search results
    for queried_prefix in queried_prefixes:
        # If there's anything at all in here, say we found something.
        # If the prefix doesn't exist, this won't fire off.
        found_a_prefix = True
    # If the prefix already exists
    if found_a_prefix:
        print(f"Prefix {global_container['prefix']} already exists. Not adding.")
        # Punt
        continue
    # Build a dictionary to add the prefix
    prefix_to_add = {
        "status": "active",
        "prefix": global_container['prefix'],
        "description": global_container['name'].upper(),
    }
    print(f"Adding prefix {global_container['prefix']} to {global_container['name']}.")
    # Add the prefix
    new_prefix = nb_conn.ipam.prefixes.create(prefix_to_add)

# Go through the list of `sites` in the YAML file
for site in prefixes_to_load['sites']:
    site_name = site['name'].upper()
    queried_site = nb_conn.dcim.sites.get(name=site_name)
    if not queried_site:
        print(f"Site {site['name']} does not exist. Skipping.")
        continue
    site_id = queried_site.id
    print(f"Adding prefixes for site {site_name} with ID of {site_id}.")
    
    for con_pre in site['container_prefixes']:
        queried_containers = nb_conn.ipam.prefixes.filter(site_id=site_id, status="container", prefix=con_pre['prefix'])
        if len(queried_containers) > 0:
            print(f"That container already exists.")
            continue
        con_pre_to_add = {
            "status": "container",
            "site": site_id,
            "prefix": con_pre['prefix']
        }
        new_con_pre = nb_conn.ipam.prefixes.create(con_pre_to_add)
        print(f"Added container prefix {new_con_pre['display']} as ID {new_con_pre['id']}.")
    
    for vlan in site['vlans']:
        queried_vlans = nb_conn.ipam.vlans.filter(site_id=site_id)
        found_a_vlan = False
        working_vlan = ""
        for queried_vlan in queried_vlans:
            if queried_vlan.vid == vlan['vid'] and queried_vlan.name == vlan['name'].upper():
                found_a_vlan = True
                working_vlan = queried_vlan
        if found_a_vlan:
            print(f"VLAN {vlan['vid']} in {site['name']} already exists. Not adding.")
        else:
            vlan_to_add = {
                "site": site_id,
                "status": "active",
                "name": vlan['name'].upper(),
                "vid": vlan['vid']
            }
            print(f"Adding VLAN {vlan['vid']} ({vlan['name']}) to {site['name']}.")
            working_vlan = nb_conn.ipam.vlans.create(vlan_to_add)
            
        queried_prefixes = nb_conn.ipam.prefixes.filter(site_id=site_id)
        found_a_prefix = False
        for queried_prefix in queried_prefixes:
            if queried_prefix.prefix == vlan['prefix']:
                found_a_prefix = True
        if found_a_prefix:
            print(f"Prefix {vlan['prefix']} already exists. Not adding.")
            continue
        prefix_to_add = {
            "status": "active",
            "site": site_id,
            "vlan": working_vlan.id,
            "prefix": vlan['prefix'],
            "description": vlan['name'].upper()
        }
        print(f"Adding prefix {vlan['prefix']} to {site['name']}.")
        new_prefix = nb_conn.ipam.prefixes.create(prefix_to_add)
# Delete your Netbox token on the way out
token.delete()