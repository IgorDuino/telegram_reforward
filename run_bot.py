import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reforward.settings")
django.setup()

from tgbot.bot.bot import main

if __name__ == "__main__":
    main()
