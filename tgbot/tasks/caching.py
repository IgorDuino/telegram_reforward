import asyncio
from django.core.cache import cache

from reforward.celery import app
from tgbot.models import User, Meme
from tgbot.bot.utils import get_cache_key_for_recommendation_function


@app.task(ignore_result=True)
def update_empty_cache(function_name, user_id, limit):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(__update_empty_cache(function_name, user_id, limit))


async def __update_empty_cache(function_name, user_id, limit):
    key = get_cache_key_for_recommendation_function(function_name, user_id)
    function_object = getattr(Meme.objects, function_name)

    await asyncio.sleep(0.4)
    user = await User.objects.only("user_id").aget(user_id=user_id)
    memes = await function_object(user, limit=limit)
    cache.set(key, memes, timeout=60 * 60)
