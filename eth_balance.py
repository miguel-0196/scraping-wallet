# define variables
target_addr = "0x00000000219ab540356cBB839Cbe05303d7705Fa"
rpc_url = f"https://api.zmok.io/mainnet/oaen6dy8ff6hju9k"

# import libraries
from web3 import Web3

# connect to web3
web3 = Web3(Web3.HTTPProvider(rpc_url))
if  web3.is_connected() != True:
    print("ERROR, connecting web3...")
    exit()

# get balance
balance = web3.eth.get_balance(target_addr)
balance = web3.from_wei(balance, "ether")
print(target_addr, ":", balance)