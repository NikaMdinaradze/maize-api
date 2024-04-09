from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.UUIDField(pk=True)
    username = fields.CharField(max_length=50)
    email = fields.CharField(max_length=100)
    age = fields.IntField()
    first_name = fields.CharField(max_length=50)
    last_name = fields.CharField(max_length=50)
    password = fields.CharField(max_length=255)
