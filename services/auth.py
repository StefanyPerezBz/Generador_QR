import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PASS = os.getenv("ADMIN_PASS")

def login(username: str, password: str) -> bool:
    return username == ADMIN_USER and password == ADMIN_PASS
