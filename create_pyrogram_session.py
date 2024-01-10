import pyrogram
from decouple import Config, RepositoryEnv

env = Config(RepositoryEnv(".env"))

TELEGRAM_API_ID = env.get("TELEGRAM_API_ID")
TELEGRAM_API_HASH = env.get("TELEGRAM_API_HASH")
PHONE_NUMBER = env.get("PHONE_NUMBER")

with pyrogram.Client(
    "userbot",
    workdir="sessions",
    api_id=TELEGRAM_API_ID,
    api_hash=TELEGRAM_API_HASH,
    phone_number=PHONE_NUMBER,
) as app:
    print("Done")
