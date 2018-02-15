################################################################################
#
#
#
#
################################################################################


# STANDARD IMPORT STATEMENTS
import sys

# THIRD PARTY IMPORT STATEMENTS
import requests
import yaml

# CONSTANT DECLARATIONS



# MAIN DRIVER CODE
if __name__ == '__main__':
    # Get Configuration Set up loaded
    with open("config.yml", "r") as yaml_file:
        cfg = yaml.load(yaml_file)

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
    exchange_info_postfix = "/api/v1/exchangeInfo"
    response = requests.get(f'{base_endpoint}{exchange_info_postfix}')
    if response.status_code != 200:
        print("FAILED: problem getting exchange info")
        sys.exit(-3)

    # Get all symbols into a text file
    tokens = set([item['baseAsset'] for item in response.json()['symbols']])
    symbols = [(item['symbol'], item['status']) for item in response.json()['symbols']]

    # Analyze current state
    print(f"Unique tokens: {len(tokens)}")
    print(f"Unique Trading Pairs: {len(symbols)}")

    # Write symbols to file
    with open(cfg['current_symbol_file'], 'w') as out_file:
        for symbol, status in symbols:
            out_file.write(f'{symbol},{status}\n')
    print(f"{len(symbols)} symbols written to {cfg['current_symbol_file']}")

    with open(cfg['current_token_file'], 'w') as out_file:
        for token in tokens:
            out_file.write(f'{token}\n')
    print(f"{len(tokens)} tokens written to {cfg['current_symbol_file']}")
