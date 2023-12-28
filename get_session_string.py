import pyrogram
from decouple import config


TELEGRAM_USERBOT_SESSION_STRING = config("TELEGRAM_USERBOT_SESSION_STRING", default=None)
if TELEGRAM_USERBOT_SESSION_STRING:
    try:
        pyrogram.Client(
            "",
            api_id=0,
            api_hash="",
            in_memory=True,
            session_string=TELEGRAM_USERBOT_SESSION_STRING,
        ).start()
        print("Session string is already provided and valid")
        exit(0)

    except Exception:
        TELEGRAM_USERBOT_SESSION_STRING = None
        print("Session string is already provided but invalid, generating new one")

TELEGRAM_API_ID = config("TELEGRAM_API_ID")
TELEGRAM_API_HASH = config("TELEGRAM_API_HASH")
PHONE_NUMBER = config("PHONE_NUMBER")

with pyrogram.Client(
    "",
    api_id=TELEGRAM_API_ID,
    api_hash=TELEGRAM_API_HASH,
    in_memory=True,
    phone_number=PHONE_NUMBER,
) as app:
    print(app.export_session_string())
