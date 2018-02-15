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

# THIRD PARTY IMPORT STATEMENTS
import requests
import yaml

# CONSTANT DECLARATIONS



# MAIN DRIVER CODE
if __name__ == '__main__':
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
        print("Checking....")
        new_tokens = set([item['baseAsset'] for item in response.json()['symbols']])
        new_symbols = [(item['symbol'], item['status']) for item in response.json()['symbols']]

        for token in new_tokens:
            if token not in tokens:
                print(f"New Token Found: {token}")
                change_found = True

        time.sleep(5)
        response = requests.get(f'{base_endpoint}{exchange_info_postfix}')


    if not change_found:
        time_stamp = dt.datetime.now().strftime('%H:%M:%S')
        print(f"FAILED: returned {response.status_code} at {time_stamp}")
        sys.exit(-3)
