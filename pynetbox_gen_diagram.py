"""
Creates a dynamic network diagram from subnet and IP address information in Netbox

TODO:
    - Fix edge arrows
    - Fix font size on edges
    - Fix node/edge addition for name of device
"""

import pynetbox
import yaml
import graphviz
import logging

ENV_FILE = "env.yml"
CREDS_FILE = "device_creds.yml"

def main():
    """
    Main
    :return: None
    """
    logger = logging.getLogger('Log diagram gen')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Load the environment
    with open(ENV_FILE, encoding="UTF-8") as file:
        env_vars = yaml.safe_load(file)
    # Load the creds
    with open(CREDS_FILE, encoding="UTF-8") as file:
        creds = yaml.safe_load(file)
    # Connect to NB
    nb_conn = pynetbox.api(url=env_vars['netbox_url'])
    # Create a token
    my_token = nb_conn.create_token(env_vars['username'], env_vars['password'])

    # The graph
    graph = graphviz.Graph("Network Diagram", engine="neato")
    graph.graph_attr['overlap'] = "False"
    graph.graph_attr['splines'] = "curved"

    # The prefixes in NB
    nb_prefixes = nb_conn.ipam.prefixes.all()

    for prefix in nb_prefixes:
        if prefix.status.value == "container":
            logger.debug(f"Skipping {prefix} since it's a container.")
            continue
        prefix_addresses = nb_conn.ipam.ip_addresses.filter(parent=prefix.prefix)
        if len(prefix_addresses) < 1:
            logger.debug(f"{prefix} doesn't have any children. Skipping.")
            continue
        else:
            logger.debug(f"Adding {prefix} to the diagram.")
            # graph.node(prefix.prefix, label=prefix.prefix, name=prefix.prefix)
            graph.node(prefix.prefix, style="filled", fillcolor="brown")
        for address in prefix_addresses:
            logger.debug(f"Adding {address} as a node.")
            graph.node(address.assigned_object.device.name, shape="rectangle", style="filled", fillcolor="green")
            logger.debug(f"Adding an edge from {address.address} to {prefix.prefix}")
            # graph.edge(address.assigned_object.device.name, prefix.prefix, taillabel=address.address, arrowhead="none", fontsize="8pt")
            graph.edge(address.assigned_object.device.name, prefix.prefix, taillabel=address.address, fontsize="8pt")

    logger.debug(graph.source)
    graph.render(view=True)

    # Delete the token we created
    my_token.delete()


if __name__ == "__main__":
    main()

