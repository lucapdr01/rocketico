from django.db import models
from django.contrib.auth.models import User


# Model that stores contract info
class Contracts(models.Model):
    rocketAbi = models.CharField(max_length=500000)
    saleAbi = models.CharField(max_length=500000)
    rocketAddress = models.CharField(max_length=50)
    saleAddress = models.CharField(max_length=50)
    tokensAvailable = models.IntegerField(blank=True, null=True, default=None)


# Wallet assigned at each new user registers
class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(blank=True, null=True, default=None)
    encryptedKey = models.CharField(blank=True, max_length=2000, null=True, default=None)
    address = models.CharField(blank=True, max_length=500, null=True, default=None)


# Model for buy form
class BuyToken(models.Model):
    amount = models.IntegerField(blank=False)
    password = models.CharField(blank=False, max_length=200, )


# Model for token sale form
class TokenSale(models.Model):
    adminPrivateKey = models.CharField(blank=False, null=False, default=None, max_length=200)
    amount = models.IntegerField(blank=False)


# Model for sendEther form
class EtherTransaction(models.Model):
    adminPrivateKey = models.CharField(blank=False, null=False, default=None, max_length=200)
    toAddress = models.CharField(blank=False, null=False, default=None, max_length=200)
    amount = models.IntegerField(blank=False)

