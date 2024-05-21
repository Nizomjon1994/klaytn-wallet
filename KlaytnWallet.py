import json
from web3 import Web3
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from web3.exceptions import TransactionNotFound, BlockNotFound, TooManyRequests, ProviderConnectionError, \
    CannotHandleRequest


class KlaytnWallet:

    def __init__(self, provider_url):
        self.web3 = Web3(Web3.HTTPProvider(provider_url))  # init web3
        self.wallets = {}  # init wallet map

    def validate_address(self, address):
        if not self.web3.is_address(address):
            raise ValueError("Invalid address")

    def validate_private_key(self, private_key):
        try:
            self.web3.eth.account.from_key(private_key)
        except ValueError:
            raise ValueError("Invalid private key")

    def create_wallet(self):
        account = self.web3.eth.account.create()
        self.wallets[account.address] = account.key.hex()
        return {
            "address": account.address,
            "private_key": account.key.hex()
        }

    def get_wallet_private_key(self, address):
        self.validate_address(address)
        private_key = self.wallets.get(address)
        if not private_key:
            raise ValueError("Wallet not found")
        return private_key

    def get_klay_balance(self, address):
        self.validate_address(address)
        balance = self.web3.eth.get_balance(address)  # get klay balance
        return self.web3.from_wei(balance, 'ether')

    def get_token_balance(self, address, token_contract_address):
        self.validate_address(address)
        self.validate_address(token_contract_address)
        with open('abi/ERC20_ABI.json') as f:
            token_abi = json.load(f)
        address = self.web3.to_checksum_address(address)  # convert address for checksum
        token_contract_address = self.web3.to_checksum_address(token_contract_address)  # convert address for checksum
        contract = self.web3.eth.contract(address=token_contract_address, abi=token_abi)  # init contract obj
        balance = contract.functions.balanceOf(address).call()  # get token balance
        decimals = contract.functions.decimals().call()  # get token decimals
        return balance / (10 ** decimals)

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=10),
           retry=retry_if_exception_type((TransactionNotFound, BlockNotFound, TooManyRequests, ProviderConnectionError,
                                          CannotHandleRequest, ValueError)))
    def send_klay(self, private_key, to_address, amount):
        self.validate_address(to_address)
        self.validate_private_key(private_key)
        to_address = self.web3.to_checksum_address(to_address)  # convert address for checksum
        account = self.web3.eth.account.from_key(private_key)  # create account obj from private key
        nonce = self.web3.eth.get_transaction_count(account.address)  # get wallet nonce
        gas_price = self.web3.eth.gas_price  # get network gas price
        amount = self.web3.to_wei(amount, 'ether')   # convert amount to wei
        tx = {
            'nonce': nonce,
            'to': to_address,
            'value': amount,
            'gas': 21000,
            'gasPrice': gas_price
        }
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)   # sign transaction by private key
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)  # broadcast transaction to network
        return self.web3.to_hex(tx_hash)

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=10),
           retry=retry_if_exception_type((TransactionNotFound, BlockNotFound, TooManyRequests, ProviderConnectionError,
                                          CannotHandleRequest, ValueError)))
    def send_token(self, private_key, to_address, amount, token_contract_address):
        self.validate_address(to_address)
        self.validate_private_key(private_key)
        self.validate_address(token_contract_address)
        to_address = self.web3.to_checksum_address(to_address)  # convert address for checksum
        token_contract_address = self.web3.to_checksum_address(token_contract_address)  # convert token contract address for checksum
        account = self.web3.eth.account.from_key(private_key)  # create account obj from private key
        nonce = self.web3.eth.get_transaction_count(account.address)  # get wallet nonce
        with open('abi/ERC20_ABI.json') as f:
            token_abi = json.load(f)
        contract = self.web3.eth.contract(address=token_contract_address, abi=token_abi)  # init contract obj
        decimals = contract.functions.decimals().call()  # get token decimals
        amount = amount * (10 ** decimals)  # convert amount by decimals
        gas_price = self.web3.eth.gas_price  # get network gas price
        tx = contract.functions.transfer(to_address, amount).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gasPrice': gas_price
        })
        gas_limit = self.web3.eth.estimate_gas(tx)  # estimate gas limit
        tx.update({'gas': gas_limit})  # update gas limit
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)  # sign transaction by private key
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)  # broadcast transaction to network
        return self.web3.to_hex(tx_hash)

    def check_transaction_status(self, tx_hash):
        return self.web3.eth.get_transaction_receipt(tx_hash)
