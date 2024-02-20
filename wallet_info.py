# This script is for gathering wallet balance and age info with scraping.
# i.e: https://debank.com/profile/0x00000000219ab540356cbb839cbe05303d7705fa")

import os
import re
import sys
import time
import json
import datetime
import argparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

input_file = 'input.txt'
loop_flag = False
base_url = 'https://debank.com/profile/'

# Parse arguments
def parse_arguments():
	global input_file, loop_flag

	argParser = argparse.ArgumentParser()
	argParser.add_argument("-i", "--input", help="Wallet address list file path or wallet json files directory path. Default: input.txt")
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
	options.add_argument('log-level=3')
	options.add_argument("disable-quic")
	return webdriver.Chrome(options=options)

# Get html content
def get_html_with_request(driver, url, xpath = None):
	# time.sleep(1)
	driver.get(url)
	if xpath != None:
		WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, xpath)))
	return driver.page_source

# Parsing wallet info
def parse_wallet_info(soup):
	# Find total balance
	el1 = soup.find('div', attrs={'class': 'HeaderInfo_totalAssetInner__HyrdC'})
	bal = re.sub(r'[\+\-].*$', '', el1.get_text().replace(',', '')) if el1 != None else '-'

	# Find active date
	el2 = soup.find('div', attrs={'class': 'db-user-tag is-age'})
	age = el2.get_text() if el2 != None else '-'
	
	return bal, age


# Print usage
parse_arguments()

target_list = []
if os.path.isdir(input_file):
	target_list = [os.path.splitext(filename)[0] for filename in os.listdir(input_file)]
elif os.path.isfile(input_file):
	target_list = read_file(input_file).split('\n')

if len(target_list) == 0:
	print("No input")
else:
	# Main loop
	timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
	output_file = f'output_{timestamp}.txt'
	first_loop = True
	count = 0
	while loop_flag or first_loop:
		first_loop = False
		for line in target_list:
			try:
				m = re.search('[0-9a-fA-F]{40}', line)
				wallet_address = m.group(0)
				if wallet_address == None:
					continue

				if count % 10 == 0:
					driver = chrome_driver()
				count += 1

				target_url = base_url + wallet_address
				html = get_html_with_request(driver, target_url, '//*[@class="UpdateButton_updateTimeNumber__9wXmw"]')

				soup = BeautifulSoup(html, 'html.parser')
				bal, age = parse_wallet_info(soup)
				print("")
				print("No", count)
				print(f"URL: {target_url}")
				print(f"Bal: {bal}")
				print(f"Age: {age}")
				append_file(f'{wallet_address}:{bal}:{age}\n', output_file)
			
			except Exception as inst:
				print("")
				print("An exception occurred at", target_url)
				save_file(html, f'err-{wallet_address}.htm')
				print(str(inst))

		time.sleep(3)