These are files to support a series of blog posts on Pynetbox.

# Blog Python Files

* **pynetbox_query_filter_1.py** : This file shows all the devices in Netbox grouped by site. It queries Netbox for all sites, then queries devices by those sites using `filter`.
* **pynetbox_query_filter_2.py** : This does the same as _1 but only shows those devices with a `planned` status.
* **pynetbox_query_filter_3.py** : This prints shipping labels for all planned devices. The exercise here is the difference between `filter` and `get` when querying Netbox.
* **pynetbox_update_sites.py** : Updates site information based on the `sites.yml`.
* **pynetbox_update_device_serial.py** : Updates device serial numbers by logging into the device, scraping that informatin, then pushing that to Netbox.
* **catalog_ip_addresses.py** : Logs into a device, pings the IPs in question, checks the ARP table, then makes sure they are all in Netbox.
* **pynetbox_gen_diagram.py** : Queries Netbox for prefixes and IP addresses to create a dynamic network diagram.

# YAML Files

* **env.yml** : This contains environment variables such as Netbox URL, username, and password.
* **sites.yml** : This file contains the list of sites that Netbox should include. See `pynetbox_populate_sites.py`.
* **devices.yml** : This is where you'll find the devices that should be in Netbox. See `pynetbox_populate_devices.py`.
* **device_roles.yml** : This contains the names and slugs of the device roles to add to Netbox. See `pynetbox_populate_device_roles.py`.
* **devices_to_update.yml** : This is a list of device names and IPs to be used by `pynetbox_update_device_serial.py` (and others) to update the serial number.
* **prefixes.yml** : Used by `pynetbox_populate_prefixes.py` to get prefixes and VLANs configured. Something like this.
* **subnets.yml** : Used by `catalog_ip_addresses.py` to limit the subnets that script cares about.

```
{'global': [{'name': 'WAN', 'prefix': '172.16.0.0/24'}],
 'sites': [{'container_prefixes': [{'prefix': '10.0.0.0/16'}],
            'name': 'NYC',
            'vlans': [{'name': 'mgmt', 'prefix': '10.0.0.0/24', 'vid': 100},
                      {'name': 'users', 'prefix': '10.0.1.0/24', 'vid': 101},
                      {'name': 'servers',
                       'prefix': '10.0.2.0/24',
                       'vid': 102}]},
           {'container_prefixes': [{'prefix': '10.1.0.0/16'}],
            'name': 'CHI',
            'vlans': [{'name': 'mgmt', 'prefix': '10.1.0.0/24', 'vid': 100},
                      {'name': 'users', 'prefix': '10.1.1.0/24', 'vid': 101},
                      {'name': 'servers',
                       'prefix': '10.1.2.0/24',
                       'vid': 102}]},
<SNIP>
```
# Utility Python Files

* **pynetbox_populate_sites.py**: Pulls in site info from YAML and adds them to Netbox if needed.
* **pynetbox_populate_devices.py**: Pulls in device info from YAML and adds them to Netbox if needed.
* **pynetbox_populate_device_roles.py**: Pulls in device role into from YAML and adds them to Netbox if needed.
* **pynetbox_populate_device_types.py**: Just puts a manufacturer called `GENERIC` in Netbox with a model of `GENERIC`. This is all hardcoded.
* **pynetbox_populate_prefixes.py**: VLAN and prefixes go from YAML to Netbox. Includes a way to have global prefixes (i.e., to what location and VLAN does the WAN belong?) and site-specific container prefixes.
* **pynetbox_populate_interfaces.py**: Adds interfaces and IP addresses (optinally) to Netbox via YAML file.
* **pynetbox_get_choices.py**: Gets a list of valid statuses for devices in Netbox. This is used to validate input from a YAML file (or wherever).
* **pynetbox_get_token.py**: Logs into Netbox with a user/pass, get an API token, prints it, then deletes it. This is to show how tokens can be generated dynamically.
* **pynetbox_clear_all_tokens.py**: When your script dies a horrible death, the Netbox API tokens may linger. This scripts nukes all tokens except for the one generated when this script runs. It's the only way to be sure.
* **pynetbox_clear_old_tokens.py**: Delete all the keys that are older than TOKEN_AGE_LIMIT
* **pynetbox_environment_report.py**: Print a summary of the Python and Netbox versions to include in a blog post
* **vault_reference.py**: A quick-and-dirty script to do some Hashicorp Vault stuff for POC.