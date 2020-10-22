from .log import logger

from discord.ext import commands


class Testing(commands.Cog):
    def __init__(self, client):
        self.client = client

    @property
    def description(self):
        return 'extensions loaders and basic testing commands.'

    @commands.command(help='test the connection with me.')
    async def ping(self, ctx):
        await ctx.send(f"**Pong!** Latency: {round(self.client.latency * 1000)}ms.")

    @commands.command(description='load an extension module.')
    async def load(self, ctx, extension):
        logger.info(f'loading extension {extension}.')
        self.client.load_extension(f'cogs.{extension}')
        await ctx.send('extension has been loaded.')

    @commands.command(description='unload an extension module')
    async def unload(self, ctx, extension):
        logger.info(f'unloading extension {extension}.')
        self.client.unload_extension(f'cogs.{extension}')
        await ctx.send('extension has been unloaded')

    @commands.command(description='reload an extension module.')
    async def reload(self, ctx, extension):
        logger.info(f'reloading extension {extension}.')
        self.client.unload_extension(f'cogs.{extension}')
        self.client.load_extension(f'cogs.{extension}')
        await ctx.send('extension has been reloaded.')


def setup(client: commands.Bot):
    client.add_cog(Testing(client))
