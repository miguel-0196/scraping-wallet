import os
import re
import sys
import time
import json
import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Description:
#     Scraping debank.com
#     i.e: https://debank.com/profile/0x00000000219ab540356cbb839cbe05303d7705fa
#
#     Input: wallet address list file [default: input.txt]
#     Output: wallets' balance and age [output.txt]
# 
#     Usage: --help 

base_url = 'https://debank.com/profile/'


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

# Get html content
def get_html_with_request(url):
	# time.sleep(1)
	driver = webdriver.Chrome()
	driver.get(url)
	WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="Wallet"]')))
	return driver.page_source

# Parsing wallet info
def parse_wallet_info(soup):
	# Find total balance
	el1 = soup.find('div', attrs={'class': 'HeaderInfo_totalAssetInner__HyrdC'})
	bal = re.sub(r'\+.*$', '', el1.get_text().replace('$', '').replace(',', '')) if el1 != None else ''

	# Find active date
	el2 = soup.find('div', attrs={'class': 'db-user-tag is-age'})
	age = el2.get_text().replace(' days', '') if el2 != None else ''
	
	return bal, age


# Print usage
if len(sys.argv) == 2 and sys.argv[1] == '--help':
	print(f'Usage: python {os.path.basename(sys.argv[0])} <wallet-address-list-file>')
	sys.exit(1)

# Check argument
target_file = sys.argv[1] if len(sys.argv) == 2 else 'input.txt'
if not os.path.isfile(target_file):
	print("Can't find the file:", target_file)
	sys.exit(1)    


# Main loop
timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
output_file = f'output_{timestamp}.txt'
while True:
	target_list = read_file(target_file)
	for wallet_address in target_list.split('\n'):
		assert wallet_address.startswith('0x'), f'\nWallet address must start with 0x: {wallet_address}'

		target_url = base_url + wallet_address
		html = get_html_with_request(target_url)

		soup = BeautifulSoup(html, 'html.parser')
		bal, age = parse_wallet_info(soup)
		print("URL:", target_url)
		print(wallet_address, bal, age)
		append_file(f'{wallet_address} {bal} {age}\n', output_file)
	
	time.sleep(3)