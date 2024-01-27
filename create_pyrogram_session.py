import pyrogram
from decouple import config
import os

TELEGRAM_API_ID = config("TELEGRAM_API_ID")
TELEGRAM_API_HASH = config("TELEGRAM_API_HASH")
PHONE_NUMBER = config("PHONE_NUMBER")

if not os.path.exists("sessions/"):
    os.mkdir("sessions/")


for name in ("userbot", "notify_userbot"):
    if os.path.exists(f"sessions/{name}.session"):
        print(f"Session {name} already exists")
        continue
    print(f"Creating {name} session")
    with pyrogram.Client(
        name,
        workdir="sessions",
        api_id=TELEGRAM_API_ID,
        api_hash=TELEGRAM_API_HASH,
        phone_number=PHONE_NUMBER,
    ) as app:
        print(f"Session {name} created")
