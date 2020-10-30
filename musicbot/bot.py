import os

from discord import ClientUser
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
    logger.error(''.join([str(ctx.author), ' caused an exception']), exc_info=error)
    await ctx.send(error)


@client.event
async def on_message(message):
    await client.process_commands(message)
    if not message.guild:
        # TODO add conversational model
        await message.author.send(f"Received: {message.content}")
