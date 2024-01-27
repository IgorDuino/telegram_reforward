from decouple import config

from pyrogram import Client
from pyrogram.enums import ParseMode

import asyncio
import redis.asyncio as redis

import json
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

REDIS_HOST = config("REDIS_HOST", default="redis")
REDIS_PORT = config("REDIS_PORT", cast=int, default=6379)
REDIS_DB = config("REDIS_DB", cast=int, default=0)
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

PHONE_NUMBER = config("PHONE_NUMBER")
TELEGRAM_API_ID = config("TELEGRAM_API_ID", cast=int)
TELEGRAM_API_HASH = config("TELEGRAM_API_HASH")

app = Client(
    "notify_userbot",
    workdir="sessions",
    phone_number=PHONE_NUMBER,
    api_id=TELEGRAM_API_ID,
    api_hash=TELEGRAM_API_HASH,
)


async def listen_redis_pubsub(app):
    client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    pubsub = client.pubsub()
    await pubsub.subscribe("notifications")

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                chat_id = data["chat_id"]
                text = data["text"]

                try:
                    await app.send_message(chat_id, text, parse_mode=ParseMode.MARKDOWN)
                except Exception as e:
                    logger.exception(e)

    except Exception as e:
        logger.exception(e)

    finally:
        await client.aclose()


if __name__ == "__main__":
    app.start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(listen_redis_pubsub(app))
