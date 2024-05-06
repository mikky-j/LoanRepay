"""
This module contains all the models that would be used for the loan repay plaform
"""

import datetime
from peewee import (
    AutoField,
    BooleanField,
    DateTimeField,
    FloatField,
    ForeignKeyField,
    IntegerField,
    Model,
    PrimaryKeyField,
    SqliteDatabase,
    CharField,
)

db = SqliteDatabase("loanrepay.db")


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = PrimaryKeyField()
    username = CharField(unique=True)
    password = CharField()
    created_at = DateTimeField(default=datetime.datetime.now)


class Loan(BaseModel):
    id = PrimaryKeyField()
    user = ForeignKeyField(User)
    original_loan_amount = IntegerField(null=False)
    loan_amount = FloatField(null=False)
    interest_rate = FloatField(null=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    fixed = BooleanField(default=False)
    fixed_pay_amount = FloatField(default=0)


class Payment(BaseModel):
    id = PrimaryKeyField()
    user = ForeignKeyField(User)
    amount = FloatField(null=False)
    current_balance = FloatField()
    loan = ForeignKeyField(Loan)
    month = IntegerField()
