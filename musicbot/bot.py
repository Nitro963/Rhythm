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


@client.event
async def on_command_error(ctx, error):
    error_name: str = type(error).__name__
    if 'Error' not in error_name:
        error_name = ''.join([error_name, ' Error'])
    if isinstance(error, commands.CommandInvokeError):
        error_name = str(error)
    logger.error(''.join([error_name, ' caused by user ', str(ctx.author)]))
    await ctx.send(error)
