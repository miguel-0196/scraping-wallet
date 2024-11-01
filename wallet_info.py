# This script is for gathering wallet balance and age info with scraping.
# i.e: 
# https://debank.com/profile/0x00000000219ab540356cbb839cbe05303d7705fa
# https://tronscan.org/#/address/TNPdqto8HiuMzoG7Vv9wyyYhWzCojLeHAF
# https://solscan.io/account/39aJEtMEBVekbrFhFbTbTB2EFZffiqf43AePVDRekGL7

import os
import re
import time
import json
import datetime
import argparse

import re
from solana.rpc.api import Client
from solders.pubkey import Pubkey

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

input_file = 'input.txt'
loop_flag = False
base_url = 'https://debank.com/profile/'
tron_url = 'https://tronscan.org/#/address/'
sola_url = 'https://solscan.io/account/'

sol_price = 180.32

# Parse arguments
def parse_arguments():
    global input_file, loop_flag

    argParser = argparse.ArgumentParser()
    argParser.add_argument("-i", "--input", help="Wallet address list file path or wallet json files directory path or wallet address. Default: input.txt")
    argParser.add_argument("-l", "--loop", action="store_true", help="Keep iterating.")
    args = argParser.parse_args()

    input_file = args.input if args.input else 'input.txt'
    loop_flag = args.loop if args.loop else False

# Save as a file
def save_file(text, filename = 'test.htm'):
    if type(text) != 'str':
        text = str(text)
    file = open(filename, 'w', encoding='utf-8')
    file.write(text)
    file.close()

# Append as a file
def append_file(text, filename = 'output.txt'):
    if type(text) != 'str':
        text = str(text)
    file = open(filename, 'a', encoding='utf-8')
    file.write(text)
    file.close()

# Read file
def read_file(filename = 'test.htm'):
    file = open(filename, 'r', encoding='utf-8')
    text = file.read()
    file.close()
    return text

# Save as json
def save_json_file(json_value, file_path):
    with open(file_path, 'a') as file:
        # Write the JSON data to the file
        json.dump(json_value, file)


# Chrome driver instance
def chrome_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--log-level=3')
    options.add_argument('--silent')
    options.add_argument('--disable-quic')
    return webdriver.Chrome(options=options)

# Get html content
def get_html_with_request(driver, url, xpath = None):
    driver.get(url)
    if xpath != None:
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, xpath)))
    else:
        time.sleep(1)
    return driver.page_source

# Parsing debank info
def parse_wallet_info(soup):
    # Find total balance
    el1 = soup.find('div', attrs={'class': 'HeaderInfo_totalAssetInner__HyrdC'})
    bal = re.sub(r'[\+\-].*$', '', el1.get_text().replace(',', '')) if el1 != None else '-'

    # Find active date
    el2 = soup.find('div', attrs={'class': 'db-user-tag is-age'})
    age = el2.get_text() if el2 != None else '-'
    
    return bal, age

# Parsing tron info
def parse_tron_info(soup):
    # Find total balance
    el1 = soup.find('span', attrs={'class': 'address-asset-num'})
    bal = re.sub(r'[\+\-].*$', '', el1.get_text().replace(',', '')) if el1 != None else '-'

    # Find active date
    el2 = soup.find('span', attrs={'class': 'activity-num'})
    age = re.sub(r'[\s\:].*$', '', el2.get_text()) if el2 != None else '-'
    
    return bal, age


def is_valid_solana_address(address):
    # Regular expression to validate Solana wallet address
    return re.match(r'^[1-9A-HJ-NP-Za-km-z]{32,44}$', address) is not None

def get_sol_balance(address):
    # Connect to the Solana devnet
    client = Client("https://api.mainnet-beta.solana.com")

    # Fetch and display the wallet's balance
    balance_response = client.get_balance(Pubkey.from_string(address))
    balance = balance_response.value if hasattr(balance_response, 'value') else None

    if balance is not None:
        sol_balance = balance / 1_000_000_000
        return sol_balance
    else:
        return 0


# Print usage
parse_arguments()

target_list = []
if os.path.isdir(input_file):
    target_list = os.listdir(input_file)
elif os.path.isfile(input_file):
    target_list = read_file(input_file).split('\n')
else:
    target_list.append(input_file)

if len(target_list) == 0:
    print("No input")
else:
    # Main loop
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_file = f'addr_{timestamp}.txt'
    first_loop = True
    count = 0
    while loop_flag or first_loop:
        first_loop = False
        for line in target_list:
            try:
                if line == "" or line.startswith('#'):
                    continue
                print(f"\n\n=> {line}")

                # Find wallet addr
                wallet_address = f"@{line}" # for exception
                tron_flag = False
                m = re.search('[0-9a-fA-F]{40}', line)
                if m != None:
                    wallet_address = m.group(0)
                else:
                    n = re.search('^T[0-9A-Za-z]{33}', line)
                    if n != None:
                        wallet_address = n.group(0)
                        tron_flag = True
                    else:
                        # solana case
                        if is_valid_solana_address(line):
                            bal = get_sol_balance(line)

                            print(f"URL: {sola_url}{line}")
                            print(f"Bal: {bal} SOL")
                            append_file(f'{line}:${int(bal*sol_price)}:{bal}SOL\n', output_file)

                        continue
                
                # For avoid RAM overload
                if count % 5 == 0:
                    driver = chrome_driver()
                count += 1

                # Scraping
                if tron_flag == True:
                    target_url = tron_url + wallet_address
                    waiting_obj = '//*[@class="address-asset-num"]'
                else:
                    target_url = base_url + '0x' + wallet_address
                    waiting_obj = '//*[@class="UpdateButton_updateTimeNumber__9wXmw"]'
                    
                print(f"URL: {target_url}")
                html = get_html_with_request(driver, target_url, waiting_obj)

            except Exception as inst:
                append_file(f'{wallet_address}::ERROR1\n', output_file)
                print("ERROR1\n", str(inst))
                continue

            try:
                soup = BeautifulSoup(html, 'html.parser')
                if tron_flag == True:
                    bal, age = parse_tron_info(soup)
                else:
                    bal, age = parse_wallet_info(soup)

                print(f"Bal: {bal}")
                print(f"Age: {age}")
                append_file(f'{wallet_address}:{bal}:{age}\n', output_file)
            
            except Exception as inst:
                append_file(f'{wallet_address}::ERROR2\n', output_file)
                print("ERROR2\n", str(inst))

                if os.path.isdir('debug'):
                    save_file(html, f'debug/{wallet_address}.htm')

            time.sleep(3)

        if first_loop == True:
            time.sleep(60)