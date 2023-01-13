import pynetbox
import yaml
import sys
import pprint

ENV_FILE = "env.yml"

with open(ENV_FILE) as file:
    env_vars = yaml.safe_load(file)
    
# Print my Python version
print(f"{'Python':<15}: {sys.version.split()[0]:^8}")
# Print pynetbox version
print(f"{'Pynetbox':<15}: {pynetbox.__version__:^8}")
    
nb_conn = pynetbox.api(url=env_vars['netbox_url'])
token = nb_conn.create_token(env_vars['username'], env_vars['password'])

print(f"{'Netbox version':<15}: {nb_conn.status()['netbox-version']:^8}")



token.delete()