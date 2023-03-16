"""
Deletes all API tokens from Netbox
"""
import yaml
import requests
import pynetbox

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

ENV_FILE = "env.yml"
CREDS_FILE = "device_creds.yml"

def main():
    """
    Run this
    """
    with open(ENV_FILE, encoding="UTF-8") as file:
        env_vars = yaml.safe_load(file)

    with open(CREDS_FILE, encoding="UTF-8") as file:
        creds = yaml.safe_load(file)

    nb_conn = pynetbox.api(url=env_vars['netbox_url'])

    my_token = nb_conn.create_token(env_vars['username'], env_vars['password'])

    all_tokens = nb_conn.users.tokens.all()

    send_to_slack(message="Looking for old tokens in Netbox.",
                                 slack_url=creds['slack_url'])
    found_old_tokens = False

    for token in all_tokens:
        if token.id == my_token.id:
            send_to_slack(message="Don't delete your own token, silly person!",
                                         slack_url=creds['slack_url'])
            continue
        send_to_slack(message=f"Deleting token {token.id}",
                                     slack_url=creds['slack_url'])
        token.delete()
        found_old_tokens = True

    my_token.delete()

    if not found_old_tokens:
        send_to_slack(message="Found no old tokens to delete.",
                      slack_url=creds['slack_url'])

if __name__ == "__main__":
    main()
