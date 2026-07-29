import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
PROXY_URL = os.getenv("PROXY_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
ADMIN_NAME = os.getenv("ADMIN_NAME")
ADMIN_PHONE = os.getenv("ADMIN_PHONE")

CHECK_DAYS = 3
DEBT_FLOOR = 5
