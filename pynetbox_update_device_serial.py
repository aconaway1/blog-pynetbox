import pynetbox
import yaml
from netmiko import ConnectHandler
import re

ENV_FILE = "env.yml"
DEVICES_FILE = "devices_to_update.yml"
DEVICE_CREDS_FILE = "device_creds.yml"

def load_env_vars():
    with open(ENV_FILE) as file:
        return yaml.safe_load(file)

def load_devices():
    with open(DEVICES_FILE) as file:
        return yaml.safe_load(file)
    
def load_device_creds():
    with open(DEVICE_CREDS_FILE) as file:
        return yaml.safe_load(file)

env_vars = load_env_vars()
devices_to_update = load_devices()
device_creds = load_device_creds()

nb_conn = pynetbox.api(url=env_vars['netbox_url'])
token = nb_conn.create_token(env_vars['username'], env_vars['password'])

for device in devices_to_update:
    print(f"Scraping {device['name']} for update.")
    # Build a dictionary for Netmiko to use to connect to the devices
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
        m = re.match(".+serial-number: (\S+)", line)
        if m:
            scraped_info['serial'] = m.group(1)
            
    queried_device = nb_conn.dcim.devices.get(name=device['name'])
    if isinstance(queried_device, type(None)):
        print(f"The device {device['name']} doesn't exist. Skipping.")
        continue
    if queried_device['serial'] == scraped_info['serial']:
        print(f"The serials match. No changes.")
    else:
        print(f"Updating the serial number for {device['name']}.")
        queried_device.update({"serial": scraped_info['serial']})


token.delete()