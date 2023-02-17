"""
SSHes to the devices in question and get system information. If device is not in Netbox, it will
add it with appropriate device_type and device_role. If it's in there already, it will make sure
the type and role are set.
"""
import re
import yaml
import pynetbox
from netmiko import ConnectHandler


ENV_FILE = "env.yml"
DEVICES_FILE = "devices_to_update.yml"
DEVICE_CREDS_FILE = "device_creds.yml"

def load_env_vars():
    """
    Loads the `ENV_FILE` from disk as YAML and returns a dictionary of that content. This is the
    Netbox URL, username, and pass, as well as the vault information.
    Returns:
        dict: The environment information loaded from YAML
    """
    with open(ENV_FILE, encoding="utf8") as file:
        return yaml.safe_load(file)

def load_devices():
    """
    Loads the `DEVICES_FILE` from disk as YAML and returns a dictionary of that content. This is
    the file that contains information about what devices we're going to update.
    Returns:
        dict: The devices to update loaded from YAML
    """
    with open(DEVICES_FILE, encoding="utf8") as file:
        return yaml.safe_load(file)

def load_device_creds():
    """Loads the `DEVICE_CREDS_FILE` from disk as YAML and returns a dictionary of that content.
    This is the file with the username and password for logging into the devices.
    Returns:
        dict: The device credentials loaded from YAML
    """
    with open(DEVICE_CREDS_FILE, encoding="utf8") as file:
        return yaml.safe_load(file)

def add_manufacturer(connection, manufacturer_info):
    """
    Adds a manufacturer to Netbox using the given dictionary.
    Args:
        connection (pynetbox.api): The Netbox connection
        manufacturer_info (dict): A dictionary with the manufacturer's information that will
        be loaded into Netbox

    Returns:
        pynetbox.Record: The object that was created
    """
    return connection.dcim.manufacturers.create(manufacturer_info)

def add_device_type(connection, device_type_info):
    """
    Adds a device type to Netbox
    Args:
        connection (pynetbox.api): The Netbox connection
        device_type_info (dict): A dictionary with the device type's information that will be loaded
        into Netbox

    Returns:
        pynetbox.Record: The object that was created
    """
    return connection.dcim.device_types.create(device_type_info)

def add_device(connection, device_info):
    """
    Adds a device to Netbox
    Args:
        connection (pynetbox.api): The Netbox connection
        device_info (dict): A dictionary with the device's information that will be loaded into
        Netbox

    Returns:
        pynetbox.Record: The object that was created
    """
    return connection.dcim.devices.create(device_info)

env_vars = load_env_vars()
devices_to_update = load_devices()
device_creds = load_device_creds()

nb_conn = pynetbox.api(url=env_vars['netbox_url'])
token = nb_conn.create_token(env_vars['username'], env_vars['password'])

for device in devices_to_update:
    print(f"Scraping {device['name']} for update.")
    dev_conn = {
        'device_type': 'mikrotik_routeros',
        'host': device['mgmt_ip'],
        'username': device_creds['username'],
        'password': device_creds['password']
    }
    conn = ConnectHandler(**dev_conn)
    output = conn.send_command("/system/routerboard/print")
    conn.disconnect()

    scraped_info = {}

    lines = output.split("\n")

    for line in lines:
        # Get the model
        m = re.match(r".+model: (\S+)", line)
        if m:
            scraped_info['device_type'] = m.group(1)
            continue
        # Get the serial
        m = re.match(r".+serial-number: (\S+)", line)
        if m:
            scraped_info['serial'] = m.group(1)
            continue

    queried_device = nb_conn.dcim.devices.get(name=device['name'])
    if isinstance(queried_device, type(None)):
        print(f"The device {device['name']} doesn't exist. Skipping.")
        continue

    manufacturer = {}
    queried_manufacturer = nb_conn.dcim.manufacturers.get(name=device['manufacturer'].upper())
    if isinstance(queried_manufacturer, type(None)):
        print("Didn't find the manufacturer. Adding.")
        added_manufacturer_dict = {'name': device['manufacturer'].upper(),
                                   'slug': device['manufacturer'].lower()}
        manufacturer = add_manufacturer(nb_conn, added_manufacturer_dict)
    else:
        print("Manufacturer found in Netbox.")
        manufacturer = queried_manufacturer

    device_type = []
    queried_type = nb_conn.dcim.device_types.get(model=scraped_info['device_type'].upper())
    if isinstance(queried_type, type(None)):
        print("Didn't find that device type. Adding.")
        device_type = {'model': scraped_info['device_type'].upper(),
                       'slug': scraped_info['device_type'].lower(),
                       'manufacturer': manufacturer.id}
        device_type = add_device_type(nb_conn, device_type)
    else:
        print("Device type found in Netbox.")
        device_type = queried_type

    # Update the device
    queried_device.device_type = device_type
    queried_device.serial = scraped_info['serial']
    if 'status' in device.keys():
        queried_device.status = device['status']
    queried_device.save()

token.delete()
