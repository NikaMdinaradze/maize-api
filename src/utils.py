from random_username.generate import generate_username


def generate_one_username() -> str:
    username = generate_username()[0]
    return username
