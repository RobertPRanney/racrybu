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
    parser.add_argument('symbol')
    return parser.parse_args()


# MAIN DRIVER CODE
if __name__ == '__main__':
    # Get Configuration Set up loaded
    with open("config.yml", "r") as yaml_file:
        cfg = yaml.load(yaml_file)
    args = argument_setup()

    # Set to wait for a symbol to track
    if args.symbol == 'FILE':
        print("Waiting for symbol to track...")
        with open(cfg['symbol_write_file']) as in_file:
            args.symbol = in_file.read().strip()
        while args.symbol == "":
            time.sleep(5)
            with open(cfg['symbol_write_file']) as in_file:
                args.symbol = in_file.read().strip()


    print(f"Tracking Symbol: {args.symbol}")

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

    # Get Exchange Info
    exchange_info_postfix = "/api/v1/exchangeInfo"
    symbol_price_postfix = "/api/v3/ticker/price"
    response = requests.get(f'{base_endpoint}{exchange_info_postfix}')
    if response.status_code != 200:
        print("FAILED: problem getting exchange info")
        sys.exit(-3)
    pairs = [(item['symbol'], item['status'])
             for item in response.json()['symbols']
             if item['baseAsset'] == args.symbol]
    print(f"PAIRS FOUND")
    for symbol, status in pairs:
        print(f"Symbol: {symbol:<8}   Status: {status}")

    # Need to now track these pairs
    print("|{:>10}|{:>10}|{:>10}|{:>10}|".format(*['SYMBOL',
                                                  'STATUS',
                                                  'PRICE',
                                                  'TIME']))
    while True:
        symbol_price_postfix = "/api/v3/ticker/price"
        response = requests.get(f'{base_endpoint}{exchange_info_postfix}')
        if response.status_code != 200:
            print("FAILED: problem getting exchange info")
            sys.exit(-3)
        pairs = [(item['symbol'], item['status'])
                 for item in response.json()['symbols']
                 if item['baseAsset'] == args.symbol]
        for symbol, status in pairs:
            payload = {'symbol': symbol}
            response = requests.get(f'{base_endpoint}{symbol_price_postfix}',
                                    params=payload)
            if response.status_code != 200:
                code = response.status_code
                print(f"FAILED: problem getting price info on {symbol}: {code}")
                sys.exit(-4)
            price = response.json()['price']
            time_stamp = dt.datetime.now().strftime('%H:%M:%S')
            print(f"|{symbol:>10}|{status:>10}|{price:>10}|{time_stamp:>10}|")
        time.sleep(cfg['price_sleep_seconds'])

    #
    #
    #
    # while response.status_code == 200 and not change_found:
    #     # Get the new tokens lists
    #     time_stamp = dt.datetime.now().strftime('%H:%M:%S')
    #     print(f"Checking({time_stamp})....")
    #     new_tokens = list(set([item['baseAsset']
    #                            for item in response.json()['symbols']]))
    #     new_symbols = [(item['symbol'], item['status'])
    #                    for item in response.json()['symbols']]
    #
    #     # Alter for testing purposes
    #     if args.test_token:
    #         new_tokens.append("TEST")
    #
    #     # See if any new tokens are found
    #     for token in new_tokens:
    #         if token not in tokens:
    #             time_stamp = dt.datetime.now().strftime('%H:%M:%S')
    #             message = f"New Token Found: {token} at {time_stamp}"
    #             print(message)
    #             send_alert(message)
    #             change_found = True
    #
    #     # Get a new records, but dont spam endpoint
    #     if not change_found:
    #         time.sleep(cfg['ping_sleep_seconds'])
    #         response = requests.get(f'{base_endpoint}{exchange_info_postfix}')
    #     if args.test_failure_code:
    #         response.status_code = 666
    #
    #
    # # If we exited for a different reason that needs to be known
    # if not change_found:
    #     time_stamp = dt.datetime.now().strftime('%H:%M:%S')
    #     message = f"FAILED: returned {response.status_code} at {time_stamp}"
    #     print(message)
    #     send_alert(message)
    #     sys.exit(-3)
