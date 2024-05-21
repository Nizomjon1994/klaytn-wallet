from KlaytnWallet import KlaytnWallet

provider_url = "https://gateway.kmint.app/v1/klaytn/baobab"  # replace with your Klaytn node provider URL
wallet = KlaytnWallet(provider_url)


def createWalletTest():
    new_wallet = wallet.create_wallet()
    print(new_wallet)


def getKlayBalanceTest():
    wallet_address = '0x3dda8FaA454A72b96f438A600735CF9B1Ff43A02'
    balance = wallet.get_klay_balance(wallet_address)
    print(balance)


def getTokenBalanceBalanceTest():
    token_address = '0xcee8faf64bb97a73bb51e115aa89c17ffa8dd167'  # usdt
    wallet_address = '0xc0c8d309540ad56d284605695fc392979cc26f22'
    balance = wallet.get_token_balance(wallet_address, token_address)
    print(balance)


def sendKlayTest():
    private_key = ''
    wallet_address = '0xc0c8d309540ad56d284605695fc392979cc26f22'
    amount = 0.02
    tx_hash = wallet.send_klay(private_key, wallet_address, amount)
    print(tx_hash)


def sendTokenTest():
    private_key = ''
    wallet_address = '0xc0c8d309540ad56d284605695fc392979cc26f22'
    amount = 5
    token_contract_address = '0xaa5542abbd8047df38231818c49d23a47c930ed2'
    tx_hash = wallet.send_token(private_key, wallet_address, amount, token_contract_address)
    print(tx_hash)


def checkTxHashStatus():
    tx_hash = '0xb84570df72f59feef068826c552594460ab577806c9ec4222dc591a73467be94'
    result = wallet.check_transaction_status(tx_hash)
    print(result.status == 1)  # success

def startIndexing():
    wallet.start_indexing()

if __name__ == '__main__':
    # 1. deposit wallet
    createWalletTest()
    # 2. deposit wallet
    createWalletTest()
    # 3. deposit wallet
    createWalletTest()
    # start indexing (deposit wallets are being saved in memory in 'wallets')

    # supports KLAY and ERC20
    wallet.start_indexing()



