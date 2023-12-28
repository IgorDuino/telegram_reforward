import pyrogram
from decouple import config


TELEGRAM_API_ID = config("TELEGRAM_API_ID")
TELEGRAM_API_HASH = config("TELEGRAM_API_HASH")
PHONE_NUMBER = config("PHONE_NUMBER")

with pyrogram.Client(
    "userbot",
    workdir="sessions",
    api_id=TELEGRAM_API_ID,
    api_hash=TELEGRAM_API_HASH,
    phone_number=PHONE_NUMBER,
) as app:
    print("Done")
