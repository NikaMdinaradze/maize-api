from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class User(models.Model):
    id = fields.UUIDField(pk=True)
    username = fields.CharField(max_length=20)
    first_name = fields.CharField(max_length=50)
    last_name = fields.CharField(max_length=50)
    email = fields.CharField(max_length=50)
    password = fields.CharField(max_length=128)
    birth_date = fields.DateField()
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class PydanticMeta:
        exclude = ("created_at", "modified_at")


UserCreate = pydantic_model_creator(User, name="UserCreate", exclude=("id",))
UserView = pydantic_model_creator(User, name="UserView", exclude=("password",))
