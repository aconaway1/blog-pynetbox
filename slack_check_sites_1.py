import yaml
import logging
import requests

SITES_FILE = "sites.yml"
LOG_FILE = "check_sites.log"
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"
CREDS_FILE = "device_creds.yml"
SLACK_LEVEL = logging.DEBUG


def send_to_slack(message: str, message_level: int):
    """
    Send a message to Slack

    Args:
        message (str): The message text
        message_level (int): The message level (based on the Python logging module)

    Returns:
        bool: Whether or not the message was sent successfully
    """
    logging.debug(f"Posting to {creds['slack_url']}")
    headers = {"text": message}
    post_result = requests.post(url=creds['slack_url'], json=headers)
    if post_result.status_code == 200:
        return True
    return False


def log_the_message(message: str, message_level: int, local_logging: bool = True, slack: bool = True) -> None:
    """
    Log the message to the local logging handle and to Slack

    Args:
        message (str): The message text
        message_level (int): The message level (based on the Python logging module)
        local_logging (bool, optional): Bool to log locally. Defaults to True.
        slack (bool, optional): Bool to log to Slack. Defaults to True.
    """
    if local_logging:
        if message_level == logging.CRITICAL:
            logging.critical(message)
        elif message_level == logging.ERROR:
            logging.error(message)
        elif message_level == logging.WARNING:
            logging.warning(message)
        elif message_level == logging.INFO:
            logging.info(message)
        elif message_level == logging.DEBUG:
            logging.debug(message)
    
    if slack and message_level >= SLACK_LEVEL:
        send_to_slack(message=message, message_level=logging.DEBUG)

logging.basicConfig(filename=LOG_FILE,
                    level=logging.DEBUG,
                    format=LOG_FORMAT)

with open(CREDS_FILE, encoding='UTF-8') as file:
    creds = yaml.safe_load(file)

with open(SITES_FILE, encoding='UTF-8') as file:
    sites_to_load = yaml.safe_load(file)
    
for site in sites_to_load:
    if not "name" in site.keys():
        log_the_message(f"Found a site with no name:{site}", logging.CRITICAL)
        continue
    log_the_message(f"Checking config for {site['name']}.", logging.DEBUG)
    if not "physical_address" in site.keys():
        log_the_message(f"The site {site['name']} does not have a physical address configured.", logging.ERROR)
    else:
        log_the_message(f"Site {site['name']} has a physical address configured.", logging.DEBUG)
    if not "time_zone" in site.keys():
        log_the_message(f"The site {site['name']} does not have a time zone configured.", logging.ERROR)
    else:
        log_the_message(f"Site {site['name']} has a time zone configured.", logging.DEBUG)