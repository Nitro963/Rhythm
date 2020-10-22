import os

from discord.ext import commands

from .log import logger

client = commands.Bot(command_prefix='.', case_insensitive=True)


def load_cogs():
    exclude = ['__init__.py', 'log.py']
    logger.info('loading cogs...')
    for filename in os.listdir('./cogs'):
        if filename in exclude:
            continue
        if filename.endswith('.py'):
            client.load_extension(f'cogs.{filename[:-3]}')


@client.event
async def on_ready():
    logger.info("Bot is up.")

