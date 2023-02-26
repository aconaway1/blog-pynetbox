import yaml
import logging

SITES_FILE = "sites.yml"

logging.basicConfig(level=logging.DEBUG)

with open(SITES_FILE) as file:
    sites_to_load = yaml.safe_load(file)
    
for site in sites_to_load:
    if not "time_zone" in site.keys():
        logging.error(f"The site {site['name']} does not have a time zone configured.")