from web3 import Web3
import json

# all functions with direct interaction with the blockchain trough web3 are here

# connect to local blockchain
ganache_url = "HTTP://127.0.0.1:7545"
w3 = Web3(Web3.HTTPProvider(ganache_url))


# deploy contracts with basic parameters
def blockChainSetUp(key):

    # admin account
    acct = w3.eth.account.privateKeyToAccount(key)
    # variable to store output
    outputDict = {}

    # load smart contracts ( compiled contracts with truffle needed )
    # ERC-20 token contract
    RocketTokenFile = json.load(open('truffle/build/contracts/RocketToken.json'))
    RocketTokenAbi = RocketTokenFile['abi']
    RocketTokenBytecode = RocketTokenFile['bytecode']
    RocketTokenContract = w3.eth.contract(bytecode=RocketTokenBytecode, abi=RocketTokenAbi)

    outputDict['rocketAbi'] = json.dumps(RocketTokenAbi)

    # sale smart contract
    RocketSaleFile = json.load(open('truffle/build/contracts/RocketTokenSale.json'))
    RocketSaleAbi = RocketSaleFile['abi']
    RocketSaleBytecode = RocketSaleFile['bytecode']
    RocketSaleContract = w3.eth.contract(bytecode=RocketSaleBytecode, abi=RocketSaleAbi)

    outputDict['saleAbi'] = json.dumps(RocketSaleAbi)

    # building transaction
    tokenToEmit = 1000000
    # token emission
    TokenConstruct_txn = RocketTokenContract.constructor(tokenToEmit).buildTransaction({
        'from': acct.address,
        'nonce': w3.eth.getTransactionCount(acct.address),
        'gas': 1728712,
        'gasPrice': w3.toWei('21', 'gwei')})

    TokenSigned = acct.signTransaction(TokenConstruct_txn)

    TokenTx_hash = w3.eth.sendRawTransaction(TokenSigned.rawTransaction)
    # print(TokenTx_hash.hex())
    TokenTx_receipt = w3.eth.waitForTransactionReceipt(TokenTx_hash)

    TokenContract_address = TokenTx_receipt['contractAddress']
    outputDict['rocketAddress'] = TokenContract_address

    print("Contract Deployed At:", TokenContract_address)
    # ------------------------------------------------
    # ------------------------------------------------

    # Contract instance
    TokenContract_instance = w3.eth.contract(abi=RocketTokenAbi, address=TokenContract_address)
    # print to check balance
    print("Current Balance ", TokenContract_instance.functions.balanceOf(acct.address).call())

    # build token sale transaction
    tokenPrice = 1000000000000000  # in wei
    SaleConstruct_txn = RocketSaleContract.constructor(TokenContract_address, tokenPrice).buildTransaction({
        'from': acct.address,
        'nonce': w3.eth.getTransactionCount(acct.address),
        'gas': 1728712,
        'gasPrice': w3.toWei('21', 'gwei')})

    SaleSigned = acct.signTransaction(SaleConstruct_txn)

    SaleTx_hash = w3.eth.sendRawTransaction(SaleSigned.rawTransaction)
    print(SaleTx_hash.hex())
    SaleTx_receipt = w3.eth.waitForTransactionReceipt(SaleTx_hash)

    Sale_address = SaleTx_receipt['contractAddress']
    outputDict['saleAddress'] = Sale_address

    print("Contract Deployed At:", Sale_address)

    # Contract instance
    SaleContract_instance = w3.eth.contract(abi=RocketSaleAbi, address=Sale_address)
    # check token price
    print('Token Price: ', SaleContract_instance.functions.tokenPrice().call())

    return outputDict


# start a sale
def initializeSale(key, token_address, token_abi, sale_address, sale_abi, tokens_available):
    # admin account
    acct = w3.eth.account.privateKeyToAccount(key)

    # get contract instances
    tokenInstance = w3.eth.contract(abi=token_abi, address=token_address)
    saleInstance = w3.eth.contract(abi=sale_abi, address=sale_address)

    # transefer to sale the number of token desired
    InitSale_txn = tokenInstance.functions.transfer(saleInstance.address, tokens_available).buildTransaction({
        'from': acct.address,
        'nonce': w3.eth.getTransactionCount(acct.address),
        'gas': 1728712,
        'gasPrice': w3.toWei('21', 'gwei')
    })

    InitTxn_singed = acct.signTransaction(InitSale_txn)
    Init_hash = w3.eth.sendRawTransaction(InitTxn_singed.rawTransaction)

    print(Init_hash.hex())


# create a wallet for new users when they register
def createWallet(password):
    outputDict = {}
    # new account
    account = w3.eth.account.create()
    outputDict['address'] = account.address

    balance = w3.eth.getBalance(account.address)
    print('New Account Balance: ', balance)

    # encrypt account with user password
    keystore = account.encrypt(password)
    outputDict['keystore'] = keystore
    return outputDict


# send ether to account ( created fot test purpose )
def sendEther(to_address, amount_eth, key):
    # check if to_address is valid
    if w3.isAddress(to_address):
        acct = w3.eth.account.privateKeyToAccount(key)
        # build transaction
        signed_txn = w3.eth.account.signTransaction(dict(
            nonce=w3.eth.getTransactionCount(acct.address),
            gasPrice=w3.eth.gasPrice,
            gas=100000,
            to=to_address,
            value=w3.toWei(amount_eth, 'ether')
        ),
            key)

        w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        return True
    return False


# function to get balance of users in eth and Rocket tokens
def getWalletBalance(address, token_address, token_abi):
    outputDict = {}

    balance = w3.eth.getBalance(address)
    outputDict['etherBalance'] = w3.fromWei(balance, 'ether')

    tokenInstance = w3.eth.contract(abi=token_abi, address=token_address)

    # get rocket balance with smart contract function
    rocketBalance = tokenInstance.functions.balanceOf(address).call()
    outputDict['rocketBalance'] = rocketBalance

    """
    print("_______BALANCE________")
    print(w3.fromWei(balance, 'ether'), " ether")
    print(rocketBalance, " rocketToken")
    """

    return outputDict


# get number of token sold and token price
def getSaleInfo(sale_address, sale_abi):

    outDict = {}
    # contract instance
    SaleContract_instance = w3.eth.contract(abi=sale_abi, address=sale_address)

    tokenPrice = w3.fromWei(SaleContract_instance.functions.tokenPrice().call(), 'ether')
    outDict['tokenPrice'] = tokenPrice

    tokensSold = SaleContract_instance.functions.tokensSold().call()
    outDict['tokensSold'] = tokensSold

    return outDict


# function for users to buy tokens
def buyTokens(amount, key, password, sale_address, sale_abi):
    # decrypt user account
    acct = w3.eth.account.privateKeyToAccount(w3.toHex(w3.eth.account.decrypt(key, password)))
    # sale instance
    SaleContract_instance = w3.eth.contract(abi=sale_abi, address=sale_address)
    tokenPrice = w3.fromWei(SaleContract_instance.functions.tokenPrice().call(), 'ether')

    # build buy transaction
    Buy_txn = SaleContract_instance.functions.buyTokens(amount).buildTransaction({
        'from': acct.address,
        'value': w3.toWei(amount * tokenPrice, 'ether'),
        'nonce': w3.eth.getTransactionCount(acct.address),
        'gas': 1728712,
        'gasPrice': w3.toWei('21', 'gwei')})

    Buy_signed = acct.signTransaction(Buy_txn)

    BuyTx_hash = w3.eth.sendRawTransaction(Buy_signed.rawTransaction)
    print(BuyTx_hash)
