These are files to support a series of blog posts on Pynetbox.

# Blog Python Files

* **pynetbox_query_filter_1.py** : This file shows all the devices in Netbox grouped by site. It queries Netbox for all sites, then queries devices by those sites using `filter`.
* **pynetbox_query_filter_2.py** : This does the same as _1 but only shows those devices with a `planned` status.
* **pynetbox_query_filter_3.py** : This prints shipping labels for all planned devices. The exercise here is the difference between `filter` and `get` when querying Netbox.
* **pynetbox_update_sites.py** : Updates site information based on the `sites.yml`.
* **pynetbox_update_device_serial.py** : Updates device serial numbers by logging into the device, scraping that informatin, then pushing that to Netbox.
* **catalog_ip_addresses.py** : Logs into a device, checks the ARP table, then makes sure they are all in Netbox. It has some commented-out code to ping everything before getting the ARP entries to make sure you got everything.
* **pynetbox_gen_diagram.py** : Queries Netbox for prefixes and IP addresses to create a dynamic network diagram.

# YAML Files

* **env.yml** : This contains environment variables such as Netbox URL, username, and password.
* **sites.yml** : This file contains the list of sites that Netbox should include. See `rebuild_netbox_data.py`.
* **devices.yml** : This is where you'll find the devices that should be in Netbox. See `rebuild_netbox_data.py`.
* **device_creds.yml** : This contains the user/pass for the network gear and is used by anything that logs into a router/swtich/firewall to get data or make config changes.
* **device_roles.yml** : This contains the names and slugs of the device roles to add to Netbox. See `rebuild_netbox_data.py`.
* **devices_to_update.yml** : This is a list of device names and IPs to be used by `pynetbox_update_device_serial.py` (and others) to update the serial number.
* **interfaces.yml** : The list of interfaces to add to Netbox. See `rebuild_netbox_data.py`.
* **prefixes.yml** : Used by `rebuild_netbox_data.py` to get prefixes and VLANs configured. Something like this.
* **subnets_to_scan_for_arp.yml** : This is used by `catalog_ip_addresses.py` to determine which subnets to care about. Mostly, it's used when the "ping everything" code is uncommented.
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

* **rebuild_netbox_data.py**: When you break Netbox and need to start over, run this to put all the data back in there. You'll need to make sure the user/pass for Netbox is valid.
* **pynetbox_get_choices.py**: Gets a list of valid statuses for devices in Netbox. This is used to validate input from a YAML file (or wherever).
* **pynetbox_get_token.py**: Logs into Netbox with a user/pass, get an API token, prints it, then deletes it. This is to show how tokens can be generated dynamically.
* **pynetbox_clear_all_tokens.py**: When your script dies a horrible death, the Netbox API tokens may linger. This scripts nukes all tokens except for the one generated when this script runs. It's the only way to be sure.
* **pynetbox_clear_old_tokens.py**: Delete all the keys that are older than TOKEN_AGE_LIMIT
* **pynetbox_environment_report.py**: Print a summary of the Python and Netbox versions to include in a blog post
* **vault_reference.py**: A quick-and-dirty script to do some Hashicorp Vault stuff for POC.