from peewee import SqliteDatabase
from loanrepay import models


def init() -> SqliteDatabase:
    models.db.connect()
    models.db.create_tables([models.User, models.Loan, models.Payment])
    return models.db
