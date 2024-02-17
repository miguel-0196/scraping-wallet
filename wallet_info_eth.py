# This script is for gathering wallet eth balance with web3.

import os
import time
import datetime
import argparse
from web3 import Web3

input_file = 'input.txt'
loop_flag = False
rpc_url = f"https://api.zmok.io/mainnet/oaen6dy8ff6hju9k"

# Parse arguments
def parse_arguments():
	global input_file, loop_flag

	argParser = argparse.ArgumentParser()
	argParser.add_argument("-i", "--input", help="Wallet address list file or wallet json file directory. default: input.txt")
	argParser.add_argument("-l", "--loop", action="store_true", help="Loop iterating.")
	args = argParser.parse_args()

	input_file = args.input if args.input else 'input.txt'
	loop_flag = args.loop if args.loop else False

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


# Print usage
parse_arguments()

# connect to web3
web3 = Web3(Web3.HTTPProvider(rpc_url))
if  web3.is_connected() != True:
    print("ERROR, connecting web3...")
    exit()

target_list = []
if os.path.isdir(input_file):
	target_list = [os.path.splitext(filename)[0] for filename in os.listdir(input_file)]
elif os.path.isfile(input_file):
	target_list = read_file(input_file).split('\n')

# Main loop
timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
output_file = f'output_{timestamp}.txt'
first_loop = True
while loop_flag or first_loop:
	first_loop = False
	for wallet_address in target_list:
		try:
			if not wallet_address.startswith('0x'):
				continue

			# get balance with web3
			balance = web3.eth.get_balance(wallet_address)
			balance = web3.from_wei(balance, "ether")
			print(wallet_address, ":", balance)
			append_file(f'{wallet_address} {balance}\n', output_file)
		
		except Exception as inst:
			print("An exception occurred at", wallet_address)
			print(str(inst))

	time.sleep(3)