These are files to support a series of blog posts on Pynetbox.

# Blog Python Files

* pynetbox_query_filter_1.py : This file shows all the devices in Netbox grouped by site. It queries Netbox for all sites, then queries devices by those sites using `filter`.

# YAML Files

* env.yml : This contains environment variables such as Netbox URL, username, and password.
* sites.yml : This file contains the list of sites that Netbox should include. See `pynetbox_populate_sites.py`.
* devices.yml : This is where you'll find the devices that should be in Netbox. See `pynetbox_populate_devices.py`.

# Utility Python Files

* pynetbox_populate_sites.py
* pynetbox_populate_devices.py
* pynetbox_get_token.py
* pynetbox_clear_all_tokens.py