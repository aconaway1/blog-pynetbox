"""
Logs into a list of routers and gets the ARP entries. Checks Netbox to see if the entries
exists and adds them if necessary. Also makes sure the address's description field is set to
the MAC address from the ARP table.
"""
import re
import ipaddress
import requests
import yaml
import pynetbox
from netmiko import ConnectHandler

ENV_FILE = "env.yml"
DEVICES_FILE = "devices_to_update.yml"
DEVICE_CREDS_FILE = "device_creds.yml"
SUBNETS_FILE = "subnets_to_scan_for_arp.yml"

def load_env_vars() -> dict:
    """
    Loads the enviroment variables into a dictionary

    Returns:
        dict: The environment variables
    """
    with open(ENV_FILE, encoding="UTF-8") as file:
        return yaml.safe_load(file)


def load_devices() -> dict:
    """
    Loads the device variables into a dictionary

    Returns:
        dict: The device variable
    """
    with open(DEVICES_FILE, encoding="UTF-8") as file:
        return yaml.safe_load(file)


def load_device_creds() -> dict:
    """
    Loads the device creds into a dictionary

    Returns:
        dict: The device creds
    """
    with open(DEVICE_CREDS_FILE, encoding="UTF-8") as file:
        return yaml.safe_load(file)


def load_subnet_info() -> dict:
    """
    Loads the subnet info into a dictionary

    Returns:
        dict: The subnet info
    """
    with open(SUBNETS_FILE, encoding="UTF-8") as file:
        return yaml.safe_load(file)


def connect_to_device(address: str, username: str, password: str,
                      device_type:str="mikrotik_routeros") -> ConnectHandler:
    """
    Connect to the device via Netmiko using the info provided

    Args:
        address (str): The address of the device
        username (str): The username
        password (str): The password
        device_type (str, optional): The Netmiko device type to use.
          Defaults to "mikrotik_routeros".

    Returns:
        ConnectHandler: The Netmiko ConnectionHandler object to use to run commands
    """
    dev_conn = {
        'device_type': device_type,
        'host': address,
        'username': username,
        'password': password,
    }
    return ConnectHandler(**dev_conn)


def mikrotik_get_arp_entries(connection: ConnectHandler, subnets_info: dict) -> dict:
    """
    Get the ARP entries from a Mikrotik device

    Args:
        connection (ConnectHandler): The Netmiko ConnectionHandler object to use
        subnets_info (dict): The subnets to check against the device

    Returns:
        dict: A dict of the ARP entries with keys 'ip' and 'mac'
    """
    matched_arps = []
    arp_table = connection.send_command("/ip/arp/print without-paging proplist=address,mac-address")
    arp_lines = arp_table.split("\n")
    search_string = r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+"\
        r"(\w{2}\:\w{2}\:\w{2}\:\w{2}\:\w{2}\:\w{2})"
    for arp_line in arp_lines:
        match = re.search(search_string, arp_line)
        if match:
            for subnet in subnets_info:
                target_host = ipaddress.IPv4Address(match.group(1))
                if target_host in ipaddress.IPv4Network(subnet['subnet']).hosts():
                    matched_arps.append({'ip': match.group(1), 'mac': match.group(2)})
                    continue
    return matched_arps

def send_to_slack(message: str, slack_url: str):
    """
    Send a message to Slack

    Args:
        message (str): The message text
        slack_url (str): The URL to post to

    Returns:
        bool: Whether or not the message was sent successfully
    """
    headers = {"text": message}
    post_result = requests.post(url=slack_url, json=headers, timeout=10)
    if post_result.status_code == 200:
        return True
    return False

def main():
    """
    Run this stuff!
    """
    env_vars = load_env_vars()
    devices_to_update = load_devices()
    device_creds = load_device_creds()
    subnets_info = load_subnet_info()

    for device in devices_to_update:
        if 'device_type' in device.keys():
            conn = connect_to_device(device['mgmt_ip'], device_creds['username'],
                                 device_creds['password'], device_type=device['device_type'])
        else:
            conn = connect_to_device(device['mgmt_ip'], device_creds['username'],
                                     device_creds['password'])

        # Ping everything in the subnets
        # for subnet in subnets_info:
        #     nodes = list(ipaddress.ip_network(subnet['subnet']).hosts())
        #     for node in nodes:
        #         output = conn.send_command(f"ping count=1 {format(node)}")

        # Get the ARP table

        matched_arps = mikrotik_get_arp_entries(conn, subnets_info)
        conn.disconnect()

        # Tell Slack what you found
        arp_message = f"Found these addresses in the ARP table on {device['name']}.\n```"
        for arp in matched_arps:
            arp_message = arp_message + f"{arp['ip']}\n"
        arp_message = arp_message + "```"
        send_to_slack(arp_message, device_creds['slack_url'])

        # Check Netbox for those IPs.
        nb_conn = pynetbox.api(url=env_vars['netbox_url'])
        token = nb_conn.create_token(env_vars['username'], env_vars['password'])

        # Update Netbox
        for arp_entry in matched_arps:
            queried_addr = nb_conn.ipam.ip_addresses.get(address=arp_entry['ip'])
            if queried_addr:
                if not queried_addr.description == arp_entry['mac']:
                    queried_addr.update({'description': arp_entry['mac']})
                    send_to_slack(f"IP address `{arp_entry['ip']}`" \
                        f"updated with MAC `{arp_entry['mac']}`.",
                                  device_creds['slack_url'])
            else:
                added_address = nb_conn.ipam.ip_addresses.create({"address": arp_entry['ip'],
                                                                  "description": arp_entry['mac']})
                if added_address:
                    send_to_slack(f"Adding `{arp_entry['ip']}` to Netbox.",
                                  device_creds['slack_url'])
                else:
                    send_to_slack(f"Couldn't add address {arp_entry['ip']} for some reason.",
                                  device_creds['slack_url'])

        token.delete()

if __name__ == "__main__":
    main()
