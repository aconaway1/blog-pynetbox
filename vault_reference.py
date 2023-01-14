"""
Connects to the vault to get the KVs
"""
import hvac
import yaml

ENV_FILE = "env.yml"
VAULT_PATH = "test_path"

with open(ENV_FILE) as file:
    env_vars = yaml.safe_load(file)

client = hvac.Client(url=env_vars['vault_url'], token=env_vars['vault_token'])

print(f" Authenticated? {client.is_authenticated()}")

response = client.secrets.kv.v2.create_or_update_secret(VAULT_PATH, secret=dict(user="foo"))

print(f"WRITING: {response}")

response = client.secrets.kv.v2.read_secret_version(path=VAULT_PATH)

print(f"READING: {response}")