import pynetbox
import yaml

ENV_FILE = "env.yml"

with open(ENV_FILE) as file:
    env_vars = yaml.safe_load(file)

nb_conn = pynetbox.api(url=env_vars['netbox_url'])

my_token = nb_conn.create_token(env_vars['username'], env_vars['password'])

all_tokens = nb_conn.users.tokens.all()

for token in all_tokens:
    if token.id == my_token.id:
        print("Don't delete your own token, silly person!")
        continue
    print(f"Deleting token {token.id}")
    token.delete()

my_token.delete()