################################################################################
#
#
#
#
################################################################################


# STANDARD IMPORT STATEMENTS
import sys
import time
import datetime as dt
import argparse

# THIRD PARTY IMPORT STATEMENTS
import requests
import yaml

# LOCAL IMPORT STATEMENTS
from helpers import send_alert

# CONSTANT DECLARATIONS

# LOCAL DEFINITIONS
def argument_setup():
    """
    DESCR: gather command line arguments and return to caller as nice bundle
    INPUT: None
    OUTPUT namespace object - holds all command line argument, default or passed
    """
    # Initialize parser object
    parser = argparse.ArgumentParser()

    # Add possible command line arguments
    parser.add_argument("-test_token", action="store_true", help="Will add " \
                        "in a fake token to test that programs send text and " \
                        "ends properly")
    parser.add_argument("-test_failure_code", action="store_true", help="Will" \
                        "add in a fake response code to end program early")
    return parser.parse_args()


# MAIN DRIVER CODE
if __name__ == '__main__':
    # Consume command lines arguments
    args = argument_setup()

    # Get Configuration Set up loaded
    with open("config.yml", "r") as yaml_file:
        cfg = yaml.load(yaml_file)

    # Get the last recorded current state
    with open(cfg['current_symbol_file'], 'r') as in_file:
        symbols = [tuple(item.split(','))
                   for item in in_file.read().strip().split('\n')]
    print(f"Loaded {len(symbols)} symbols")

    with open(cfg['current_token_file'], 'r') as in_file:
        tokens = in_file.read().strip().split('\n')
    print(f"Loaded {len(tokens)} tokens")

    # All endpoints start here
    base_endpoint = "https://api.binance.com"

    # Check connectivity
    conn_test_postfix = "/api/v1/ping"
    response = requests.get(f'{base_endpoint}{conn_test_postfix}')
    if response.status_code != 200:
        print("FAILED: problem with connectivity check")
        sys.exit(-1)
    print(f'Connectivity check passed')

    # Check Server Time
    server_time_postfix = "/api/v1/time"
    response = requests.get(f'{base_endpoint}{server_time_postfix}')
    if response.status_code != 200:
        print("FAILED: problem checking server time")
        sys.exit(-2)
    print(f'Server time: {response.json()["serverTime"]}\n')

    # Exchange info
    change_found = False
    exchange_info_postfix = "/api/v1/exchangeInfo"
    response = requests.get(f'{base_endpoint}{exchange_info_postfix}')
    while response.status_code == 200 and not change_found:
        # Get the new tokens lists
        time_stamp = dt.datetime.now().strftime('%H:%M:%S')
        print(f"Checking({time_stamp})....")
        new_tokens = list(set([item['baseAsset']
                               for item in response.json()['symbols']]))
        new_symbols = [(item['symbol'], item['status'])
                       for item in response.json()['symbols']]

        # Alter for testing purposes
        if args.test_token:
            new_tokens.append("TEST")

        # See if any new tokens are found
        for token in new_tokens:
            if token not in tokens:
                time_stamp = dt.datetime.now().strftime('%H:%M:%S')
                message = f"New Token Found: {token} at {time_stamp}"
                print(message)
                send_alert(message)
                change_found = True

        # Get a new records, but dont spam endpoint
        if not change_found:
            time.sleep(cfg['ping_sleep_seconds'])
            response = requests.get(f'{base_endpoint}{exchange_info_postfix}')
        if args.test_failure_code:
            response.status_code = 666


    # If we exited for a different reason that needs to be known
    if not change_found:
        time_stamp = dt.datetime.now().strftime('%H:%M:%S')
        message = f"FAILED: returned {response.status_code} at {time_stamp}"
        print(message)
        send_alert(message)
        sys.exit(-3)
