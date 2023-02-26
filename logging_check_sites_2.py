import yaml
import logging

SITES_FILE = "sites.yml"
LOG_FILE = "check_sites.log"
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

logging.basicConfig(filename=LOG_FILE,
                    level=logging.DEBUG,
                    format=LOG_FORMAT)

with open(SITES_FILE) as file:
    sites_to_load = yaml.safe_load(file)
    
for site in sites_to_load:
    if not "name" in site.keys():
        logging.critical(f"Found a site with no name:{site}")
        continue
    logging.debug(f"Checking config for {site['name']}.")
    if not "physical_address" in site.keys():
        logging.error(f"The site {site['name']} does not have a physical address configured.")
    else:
        logging.debug(f"Site {site['name']} has a physical address configured.")
    if not "time_zone" in site.keys():
        logging.error(f"The site {site['name']} does not have a time zone configured.")
    else:
        logging.debug(f"Site {site['name']} has a time zone configured.")