import asyncio
import os
import logging

from musicbot.bot import load_cogs, client
from api.anilist import AnimeList

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    load_cogs()
    client.run(os.environ.get('API_KEY'))
    # anilist = AnimeList()
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(anilist.from_anime_name('Fate/zero'))

