import os
import logging
from musicbot.bot import load_cogs, client

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    load_cogs()
    client.run(os.environ.get('API_KEY'))
