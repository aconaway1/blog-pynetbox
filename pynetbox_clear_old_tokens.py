"""
Checks the last_used time on the Netbox API tokens and deletes those not used in the last TOKEN_AGE_LIMIT seconds.

Watch out for timezone mismatches between the NB server and the local host!    
"""
import pynetbox
import yaml
from datetime import datetime


ENV_FILE = "env.yml"

TOKEN_AGE_LIMIT = 1209600  # 2 weeks in seconds
NOW_TIME = datetime.now()

with open(ENV_FILE) as file:
    env_vars = yaml.safe_load(file)

nb_conn = pynetbox.api(url=env_vars['netbox_url'])

my_token = nb_conn.create_token(env_vars['username'], env_vars['password'])

all_tokens = nb_conn.users.tokens.all()

for token in all_tokens:
    if token.id == my_token.id:
        print("Don't delete your own token, silly person!")
        continue
    print(f"Token {token.id} ", end="")
    if isinstance(token.last_used, type(None)):
        print("has never been used...skipping.")
        continue
    time_diff = NOW_TIME - datetime.strptime(token.last_used, "%Y-%m-%dT%H:%M:%S.%fZ")
    print(f"used {time_diff.seconds} seconds ago...", end="")
    if time_diff.seconds > TOKEN_AGE_LIMIT:
        print("deleting.")
        token.delete()
    else:
        print("skipping.")

my_token.delete()