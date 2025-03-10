from web3 import Web3

web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

contract_address = "0xYourContractAddress"
contract_abi = [...]  # ABI from Remix IDE

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

def store_data_on_blockchain():
    vehicle_id = "V-1234"
    encrypted_data = "SampleEncryptedData"

    txn_hash = contract.functions.addData(vehicle_id, encrypted_data).transact({'from': web3.eth.accounts[0]})
    return {"Transaction Hash": txn_hash.hex()}
