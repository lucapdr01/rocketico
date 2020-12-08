import json
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from .forms import RegisterForm, UserProfileForm, BuyTokenForm, TokenSaleForm, EtherTransactionForm
from .models import Contracts

from . import utils


# admin page to deploy contracts and start token sale
def control(request):

    if request.method == "POST":
        form = TokenSaleForm(data=request.POST)

        if form.is_valid():

            key = form.cleaned_data.get('adminPrivateKey')
            tokensAvailable = form.cleaned_data.get('amount')

            # deploy contracts
            contractsDict = utils.blockChainSetUp(key)

            # insert contracts info in the DB
            buildContracts = Contracts(rocketAbi=contractsDict['rocketAbi'],
                                       saleAbi=contractsDict['saleAbi'],
                                       rocketAddress=contractsDict['rocketAddress'],
                                       saleAddress=contractsDict['saleAddress'],
                                       tokensAvailable=tokensAvailable)
            buildContracts.save()

            # get contracts information from the db to check if information have been stored correctly
            contracts = Contracts.objects.all()[0]
            # start token sale
            utils.initializeSale(key, contracts.rocketAddress, contracts.rocketAbi, contracts.saleAddress,
                                 contracts.saleAbi, tokensAvailable)
            return redirect('/')
        else:
            return render(request, "main/control.html", {"form": form})

    form = TokenSaleForm()
    return render(request, "main/control.html", {"form": form})


# function to send ether from admin to new accounts for test purpose
def sendEther(request):

    if request.method == "POST":
        form = EtherTransactionForm(data=request.POST)
        if form.is_valid():

            key = form.cleaned_data.get('adminPrivateKey')
            toAddress = form.cleaned_data.get('toAddress')
            amount = form.cleaned_data.get('amount')
            # send ether if recipient address is invalid show an error message
            result = utils.sendEther(toAddress, amount, key)
            if result:
                msg = ""
                return render(request, "main/sendether.html", {"form": form, "msg": msg})
            else:
                msg = "Error: invalid address"
                return render(request, "main/sendether.html", {"form": form, "msg": msg})

        else:
            msg = ""
            return render(request, "main/sendether.html", {"form": form, "msg": msg})

    form = EtherTransactionForm()
    msg = ""
    return render(request, "main/sendether.html", {"form": form, "msg": msg})


# home page
def home(request):
    # Check contracts are already deployed
    if len(Contracts.objects.all()) != 0:

        contracts = Contracts.objects.all()[0]
        maxToken = contracts.tokensAvailable
        tokensSold = utils.getSaleInfo(contracts.saleAddress, json.loads(contracts.saleAbi))['tokensSold']

        percentage = (tokensSold / maxToken) * 100
        # print(tokensSold)
        # print(percentage)
        warning = ""

    else:
        maxToken = 0
        percentage = 0
        warning = "Contracts Not Deployed"
    return render(request, "main/home.html", {"percentage": percentage, "total": maxToken, "warning": warning})


def dash(request):
    # get all the information to build the dashboard for users
    contracts = Contracts.objects.all()[0]

    user = request.user
    wallet = user.wallet
    address = wallet.address
    msg = ""

    # wallet balance ( ether and rocket token )
    balance = utils.getWalletBalance(wallet.address, contracts.rocketAddress, contracts.rocketAbi)
    # info about price and and number token sold of Rocket Token
    saleInfo = utils.getSaleInfo(contracts.saleAddress, json.loads(contracts.saleAbi))

    if request.method == "POST":
        form = BuyTokenForm(data=request.POST)

        if form.is_valid():

            password = form.cleaned_data.get('password')
            amount = form.cleaned_data.get('amount')

            passwd = request.user.password
            # check if password inserted matches user's password
            check = check_password(password, passwd)

            if check:
                # buy tokens
                utils.buyTokens(amount, wallet.encryptedKey, password, contracts.saleAddress, contracts.saleAbi)
                return redirect('/dash')
            else:
                msg = 'Wrong password'
                return render(request, "main/dash.html", {"form": form, "address": address, "msg": msg, "tokePrice": saleInfo['tokenPrice'], "tokensSold": saleInfo['tokensSold'],  "etherBalance": balance['etherBalance'], "rocketBalance": balance['rocketBalance']})
        else:
            return render(request, "main/dash.html", {"form": form, "address": address, "msg": msg, "tokePrice": saleInfo['tokenPrice'], "tokensSold": saleInfo['tokensSold'], "etherBalance": balance['etherBalance'], "rocketBalance": balance['rocketBalance']})

    form = BuyTokenForm()
    msg = ""
    return render(request, "main/dash.html", {"form": form, "address": address, "msg": msg, "tokePrice": saleInfo['tokenPrice'], "tokensSold": saleInfo['tokensSold'], "etherBalance": balance['etherBalance'], "rocketBalance": balance['rocketBalance']})


# registration form
def register(request):
    if request.method == "POST":

        form = RegisterForm(request.POST)
        profileForm = UserProfileForm(request.POST)

        if form.is_valid():
            user = form.save()

            profile = profileForm.save(commit=False)
            profile.user = user
            newWallet = utils.createWallet(form.cleaned_data['password1'])
            profile.encryptedKey = json.dumps(newWallet['keystore'])
            profile.address = newWallet['address']
            profile.save()

            return redirect("/")
    else:
        # initialise blank form and ip info
        form = RegisterForm()
    # render the page
    return render(request, "main/register.html", {"form": form, })


# handle logout
def logoutReq(request):
    logout(request)
    return redirect("/")


# handle login
def loginReq(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:

                login(request, user)
                return redirect('/')
            else:
                return render(request, "main/login.html", {"form": form})
        else:
            return render(request, "main/login.html", {"form": form})

    form = AuthenticationForm()
    return render(request, "main/login.html", {"form": form})
