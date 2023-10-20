"""
Rebuild the data in Netbox based on various YAML files
"""
import pynetbox
import yaml
import logging

DEBUG_LEVEL = logging.DEBUG
ENV_FILE = "env.yml"
SITES_FILE = "sites.yml"
DEV_ROLES_FILE = "device_roles.yml"
DEVICES_FILE = "devices.yml"
INTERFACES_FILE = "interfaces.yml"
PREFIXES_FILE = "prefixes.yml"



def setup_logging(log_level = logging.DEBUG):
    logger = logging.getLogger('UPDATE')
    logger.setLevel(log_level)
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
def load_env_from_yaml():
    with open(ENV_FILE) as file:
        return yaml.safe_load(file)

def load_sites_from_yaml():
    with open(SITES_FILE) as file:
        return yaml.safe_load(file)

def load_device_roles_from_yaml():
    with open(DEV_ROLES_FILE) as file:
        return yaml.safe_load(file)


def load_devices_from_yaml():
    with open(DEVICES_FILE) as file:
        return yaml.safe_load(file)


def load_interfaces_from_yaml():
    with open(INTERFACES_FILE) as file:
        return yaml.safe_load(file)

def load_prefixes_from_yaml():
    with open(PREFIXES_FILE) as file:
        return yaml.safe_load(file)

def main():
    '''
    The main stuff
    :return: Nothing
    '''
    # Load the stuff from YAML
    env_vars = load_env_from_yaml()
    sites_to_load = load_sites_from_yaml()
    # Connect to Netbox using the user and pass in the YAML
    nb_conn = pynetbox.api(url=env_vars['netbox_url'])
    token = nb_conn.create_token(env_vars['username'], env_vars['password'])
    # Set up the logging
    logger = setup_logging(log_level=DEBUG_LEVEL)
    #####
    #
    #  Load the sites
    #
    #####
    for site in sites_to_load:
        # Make sure the "name" key is given
        if site.get('name') == None:
            logger.error(f"Site does not have a name:\n{site}")
            continue
        name = site['name'].upper()
        slug = site['name'].lower()
        # See if the site already exists
        queried_site = nb_conn.dcim.sites.get(name=name)
        if queried_site:
            logger.info(f"Site {site['name']} already exists.")
            continue
        constructed_site = {"name": name, "slug": slug}
        if "description" in site.keys():
            constructed_site['description'] = site['description']
        if "physical_address" in site.keys():
            constructed_site['physical_address'] = site['physical_address']
        result = nb_conn.dcim.sites.create(constructed_site)
        logger.debug(f"Added site to Netbox: {result}")


    #####
    #
    #  Load the device roles
    #
    #####
    dev_roles_to_load = load_device_roles_from_yaml()
    for dev_role in dev_roles_to_load:
        if dev_role.get('name') == None:
            logger.error(f"Role doesn't have a name:\n{dev_role}")
            continue
        dev_role_name = dev_role['name'].upper()
        queried_dev_role = nb_conn.dcim.device_roles.get(name=dev_role_name)
        if queried_dev_role:
            logger.info(f"Device role {dev_role['name']} already exists.")
            continue
        constructed_dev_role = {"name": dev_role_name, "slug": dev_role_name.lower()}
        if "description" in dev_role.keys():
            constructed_dev_role['description'] = dev_role['description']
        result = nb_conn.dcim.device_roles.create(constructed_dev_role)
        logger.debug(f"Added device role to Netbox: {result}")


    #####
    #
    #  Load a generic manufacturer and device type
    #
    #####
    manufacturer = {
        "name": "GENERIC",
        "slug": "generic"
    }
    dev_type = {
        "model": "GENERIC",
        "slug": "generic"
    }

    queried_manufacturer = nb_conn.dcim.manufacturers.get(name=manufacturer['name'])
    if queried_manufacturer:
        logger.info(f"Manufactuer {manufacturer['name']} already exits.")
    else:
        man_result = nb_conn.dcim.manufacturers.create(manufacturer)
        logger.debug(f"Added manufacturer to Netbox: {man_result}")


    queried_dev_type = nb_conn.dcim.device_types.get(slug=dev_type['slug'].lower())
    if queried_dev_type:
        logger.info(f"Device type {dev_type['slug'].upper()} already exists.")
    else:
        dev_type['manufacturer'] = man_result['id']
        type_result = nb_conn.dcim.device_types.create(dev_type)
        logger.debug(f"Added device type to Netbox: {dev_type}")

    #####
    #
    #  Load the devices
    #
    #####
    required_keys = ['name', 'site', 'type', 'role']

    valid_devices_status = []
    for choice in nb_conn.dcim.devices.choices()['status']:
        valid_devices_status.append(choice['value'])

    devices_to_load = load_devices_from_yaml()
    for device in devices_to_load:
        if device.get('name') == None:
            logger.error(f"Device did not have a name:\n{device}")
            continue

        name = device['name'].upper()
        slug = device['name'].lower()

        logger.debug(f"Processing {name}.")

        # See if the device already exists
        queried_device = nb_conn.dcim.devices.get(name=name)
        if queried_device:
            logger.info(f"The device {name} already exists. Skipping.")
            continue

        # See if the given device type exists
        if device.get('type') == None:
            logger.error(f"Device did not have a type:\n{device}")
            continue
        dev_type = device['type'].upper()
        queried_type = nb_conn.dcim.device_types.get(slug=device['type'].lower())
        if not queried_type:
            logger.info(f"The type {dev_type} does not exist. Skipping.\n{device}")
            continue

        # See if the given device role exists
        if device.get('role') == None:
            logger.error(f"Device did not have a role:\n{device}")
            continue
        dev_role_name = device['role'].upper()
        queried_dev_role = nb_conn.dcim.device_roles.get(name=dev_role_name)
        if not queried_dev_role:
            logger.info(f"The role {dev_role_name} does not exist. Skipping.")
            continue

        # See if the given site exists
        if device.get('site') == None:
            logger.error(f"Device did not have a site:\n{device}")
            continue
        site = device['site'].upper()
        queried_site = nb_conn.dcim.sites.get(name=site)
        # if isinstance(queried_site, type(None)):
        if not queried_site:
            logger.info(f"The site {site} does not exist. Skipping.")
            continue

        constructed_device = {"name": name, "slug": slug, "site": queried_site.id, "role": queried_dev_role.id,
                              "device_type": queried_type.id}
        if "description" in device.keys():
            constructed_device['description'] = device['description']
        if "status" in device.keys():
            if device['status'] in valid_devices_status:
                constructed_device['status'] = device['status']
            else:
                logger.error(f"The status of {device['status']} isn't valid. Skipping.")
                continue
        logger.debug(f"Adding {device['name']} to Netbox.")
        result = nb_conn.dcim.devices.create(constructed_device)


    #####
    #
    #  Load the interfaces
    #
    #####
    interfaces_to_load = load_interfaces_from_yaml()

    for device_info in interfaces_to_load:
        logger.debug(f"Querying Netbox for {device_info['device']}")
        nb_queried_devices = nb_conn.dcim.devices.get(name=device_info['device'])

        if not nb_queried_devices:
            print(f"Skipping {device_info['device']} since it doesn't exist in NB.")
            continue

        # Get all the interfaces for this device in NB
        logger.debug(f"Querying Netbox for interfaces on {nb_queried_devices.name}")


        for device_intf in device_info['interfaces']:
            nb_queried_interfaces = nb_conn.dcim.interfaces.filter(device_id=nb_queried_devices.id)
            if_already_exists = False
            logger.debug(f"Processing {device_intf['name']} on {device_info['device']}")
            for intf in nb_queried_interfaces:
                logger.debug(f"Looking at interface {intf} on NB.")
                if device_intf['name'] == intf.name:
                    logger.debug(f"Interface {intf} already exists.")
                    if_already_exists = True
                    continue
            if not if_already_exists:
                logger.info(f"Adding interface {device_intf['name']}")
                if device_intf.get('type') == None:
                    intf_type = "virtual"
                else:
                    intf_type = device_intf['type']
                added_interface = nb_conn.dcim.interfaces.create(name=device_intf['name'], device=nb_queried_devices.id, type=intf_type)
            else:
                logger.debug("Skipping")
                added_interface = None

            if device_intf.get('address') != None and added_interface != None:
                added_address = nb_conn.ipam.ip_addresses.create(address=device_intf['address'], assigned_object_type="dcim.interface", assigned_object_id=added_interface.id,
                                                                 description=f"{device_info['device']}:{added_interface.name}")


    #####
    #
    #  Load the prefixes
    #
    #####
    prefixes_to_load = load_prefixes_from_yaml()
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
            logger.error(f"Prefix {global_container['prefix']} already exists. Not adding.")
            # Punt
            continue
        # Build a dictionary to add the prefix
        prefix_to_add = {
            "status": "active",
            "prefix": global_container['prefix'],
            "description": global_container['name'].upper(),
        }
        logger.debug(f"Adding prefix {global_container['prefix']} to {global_container['name']}.")
        # Add the prefix
        new_prefix = nb_conn.ipam.prefixes.create(prefix_to_add)

    # Go through the list of `sites` in the YAML file
    for site in prefixes_to_load['sites']:
        site_name = site['name'].upper()
        queried_site = nb_conn.dcim.sites.get(name=site_name)
        if not queried_site:
            logger.error(f"Site {site['name']} does not exist. Skipping.")
            continue
        site_id = queried_site.id
        logger.debug(f"Adding prefixes for site {site_name} with ID of {site_id}.")

        for con_pre in site['container_prefixes']:
            queried_containers = nb_conn.ipam.prefixes.filter(site_id=site_id, status="container",
                                                              prefix=con_pre['prefix'])
            if len(queried_containers) > 0:
                logger.error(f"That container already exists.")
                continue
            con_pre_to_add = {
                "status": "container",
                "site": site_id,
                "prefix": con_pre['prefix']
            }
            new_con_pre = nb_conn.ipam.prefixes.create(con_pre_to_add)
            logger.info(f"Added container prefix {new_con_pre['display']} as ID {new_con_pre['id']}.")

        for vlan in site['vlans']:
            queried_vlans = nb_conn.ipam.vlans.filter(site_id=site_id)
            found_a_vlan = False
            working_vlan = ""
            for queried_vlan in queried_vlans:
                if queried_vlan.vid == vlan['vid'] and queried_vlan.name == vlan['name'].upper():
                    found_a_vlan = True
                    working_vlan = queried_vlan
            if found_a_vlan:
                logger.error(f"VLAN {vlan['vid']} in {site['name']} already exists. Not adding.")
            else:
                vlan_to_add = {
                    "site": site_id,
                    "status": "active",
                    "name": vlan['name'].upper(),
                    "vid": vlan['vid']
                }
                logger.info(f"Adding VLAN {vlan['vid']} ({vlan['name']}) to {site['name']}.")
                working_vlan = nb_conn.ipam.vlans.create(vlan_to_add)

            queried_prefixes = nb_conn.ipam.prefixes.filter(site_id=site_id)
            found_a_prefix = False
            for queried_prefix in queried_prefixes:
                if queried_prefix.prefix == vlan['prefix']:
                    found_a_prefix = True
            if found_a_prefix:
                logger.error(f"Prefix {vlan['prefix']} already exists. Not adding.")
                continue
            prefix_to_add = {
                "status": "active",
                "site": site_id,
                "vlan": working_vlan.id,
                "prefix": vlan['prefix'],
                "description": vlan['name'].upper()
            }
            logger.info(f"Adding prefix {vlan['prefix']} to {site['name']}.")
            new_prefix = nb_conn.ipam.prefixes.create(prefix_to_add)

    token.delete()

if __name__ == "__main__":
    main()