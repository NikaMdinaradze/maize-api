from src.settings import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER

db_url = f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:" f"{DB_PORT}/{DB_NAME}"
