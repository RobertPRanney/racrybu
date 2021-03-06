################################################################################
#
#
#
#
################################################################################

# IMPORT STATEMENTS
from twilio.rest import Client
import yaml

# Load the needed config that has credentials
with open("config.yml", "r") as yaml_file:
    cfg = yaml.load(yaml_file)


def send_alert(message, to_number=cfg['my_number']):
    client = Client(cfg['twilio_account_sid'], cfg['twilio_auth_token'])
    client.messages.create(to=to_number,
                           from_=cfg['twilio_number'],
                           body=message)
