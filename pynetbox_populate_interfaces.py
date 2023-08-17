"""
Add devices to Netbox based on a YAML file

TODO:
    - Local debug logging
"""
import pynetbox
import yaml
import logging

ENV_FILE = "env.yml"
INTERFACES_FILE = "interfaces.yml"

def main():
    logger = logging.getLogger('Log diagram gen')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.debug("Loading environment file")
    with open(ENV_FILE) as file:
        env_vars = yaml.safe_load(file)
    logger.debug("Loading interfaces file")
    with open(INTERFACES_FILE) as file:
        interfaces_to_load = yaml.safe_load(file)

    logger.debug("Connecting to Netbox")
    nb_conn = pynetbox.api(url=env_vars['netbox_url'])

    token = nb_conn.create_token(env_vars['username'], env_vars['password'])

    # valid_devices_status = []
    # for choice in nb_conn.dcim.devices.choices()['status']:
    #     valid_devices_status.append(choice['value'])

    for device_info in interfaces_to_load:
        logger.debug(f"Querying Netbox for {device_info['device']}")
        nb_queried_devices = nb_conn.dcim.devices.get(name=device_info['device'])

        if isinstance(nb_queried_devices, type(None)):
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
                    print(f"Interface {intf} already exists.")
                    if_already_exists = True
                    continue
            if not if_already_exists:
                print(f"Adding interface {device_intf['name']}")
                if device_intf.get('type') == None:
                    intf_type = "virtual"
                else:
                    intf_type = device_intf['type']
                added_interface = nb_conn.dcim.interfaces.create(name=device_intf['name'], device=nb_queried_devices.id, type=intf_type)
                print(f"{added_interface.id=}")
            else:
                logger.debug("Skipping")
                added_interface = None
                # if_already_exists = False

            if device_intf.get('address') != None and added_interface != None:
                added_address = nb_conn.ipam.ip_addresses.create(address=device_intf['address'], assigned_object_type="dcim.interface", assigned_object_id=added_interface.id,
                                                                 description=f"{device_info['device']}:{added_interface.name}")

    token.delete()

if __name__ == "__main__":
    main()