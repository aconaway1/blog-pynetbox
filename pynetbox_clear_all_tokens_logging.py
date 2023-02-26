"""
Deletes all API tokens from Netbox
"""
import pynetbox
import yaml
import logging

ENV_FILE = "env.yml"
LOGFILE = "clear_token.log"
LOG_FORMAT = '%(asctime)s - %(module)s - %(message)s'

logging.basicConfig(filename=LOGFILE,
                    level=logging.DEBUG,
                    format=LOG_FORMAT)

with open(ENV_FILE) as file:
    env_vars = yaml.safe_load(file)

nb_conn = pynetbox.api(url=env_vars['netbox_url'])

my_token = nb_conn.create_token(env_vars['username'], env_vars['password'])

all_tokens = nb_conn.users.tokens.all()

for token in all_tokens:
    if token.id == my_token.id:
        logging.debug(f"Skipping {token.id} since it the one I'm using right now.")
        continue
    logging.debug(f"Deleting token {token.id}")
    token.delete()

my_token.delete()