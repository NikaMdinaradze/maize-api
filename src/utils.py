from uuid import uuid4

import python_avatars as pa
from random_username.generate import generate_username


def generate_one_username() -> str:
    username = generate_username()[0]
    return username


def generate_avatar() -> str:
    random_avatar = pa.Avatar.random(style=pa.AvatarStyle.TRANSPARENT)
    avatar_path = f"media/profile/{uuid4().hex}.svg"
    random_avatar.render(avatar_path)
    return avatar_path
