from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.contrib.auth.models import User
from .models import Wallet, BuyToken, TokenSale, EtherTransaction


class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ["username", "password1", "password2", ]


# save the encrypted key when user registers
class UserProfileForm(forms.ModelForm):

    class Meta:
        model = Wallet
        fields = ('encryptedKey',)
        widgets = {'encryptedKey': forms.HiddenInput()}


class BuyTokenForm(forms.ModelForm):
    class Meta:
        model = BuyToken
        fields = ["amount", "password"]
        widgets = {'password': forms.PasswordInput}


class TokenSaleForm(forms.ModelForm):
    class Meta:
        model = TokenSale
        fields = ["adminPrivateKey", "amount"]
        widgets = {'adminPrivateKey': forms.PasswordInput}


class EtherTransactionForm(forms.ModelForm):
    class Meta:
        model = EtherTransaction
        fields = ["toAddress", "amount", "adminPrivateKey", ]
        widgets = {'adminPrivateKey': forms.PasswordInput}
