These are files to support a series of blog posts on Pynetbox.

# Blog Python Files

* **pynetbox_query_filter_1.py** : This file shows all the devices in Netbox grouped by site. It queries Netbox for all sites, then queries devices by those sites using `filter`.
* **pynetbox_query_filter_2.py** : This does the same as _1 but only shows those devices with a `planned` status.
* **pynetbox_query_filter_3.py** : This prints shipping labels for all planned devices. The exercise here is the difference between `filter` and `get` when querying Netbox.

# YAML Files

* **env.yml** : This contains environment variables such as Netbox URL, username, and password.
* **sites.yml** : This file contains the list of sites that Netbox should include. See `pynetbox_populate_sites.py`.
* **devices.yml** : This is where you'll find the devices that should be in Netbox. See `pynetbox_populate_devices.py`.
* **device_roles.yml** : This contains the names and slugs of the device roles to add to Netbox. See `pynetbox_populate_device_roles.py`.

# Utility Python Files

* **pynetbox_populate_sites.py**: Pulls in site info from YAML and adds them to Netbox if needed.
* **pynetbox_populate_devices.py**: Pulls in device info from YAML and adds them to Netbox if needed.
* **pynetbox_populate_device_roles.py**: Pulls in device role into from YAML and adds them to Netbox if needed.
* **pynetbox_populate_device_types.py**: Just puts a manufacturer called `GENERIC` in Netbox with a model of `GENERIC`. This is all hardcoded.
* **pynetbox_get_choices.py**: Gets a list of valid statuses for devices in Netbox. This is used to validate input from a YAML file (or wherever).
* **pynetbox_get_token.py**: Logs into Netbox with a user/pass, get an API token, prints it, then deletes it. This is to show how tokens can be generated dynamically.
* **pynetbox_clear_all_tokens.py**: When your script dies a horrible death, the Netbox API tokens may linger. This scripts nukes all tokens except for the one generated when this script runs. It's the only way to be sure.
* **pynetbox_clear_old_tokens.py**: Delete all the keys that are older than TOKEN_AGE_LIMIT
* **pynetbox_environment_report.py**: Print a summary of the Python and Netbox versions to include in a blog post
* **vault_reference.py**: A quick-and-dirty script to do some Hashicorp Vault stuff for POC.