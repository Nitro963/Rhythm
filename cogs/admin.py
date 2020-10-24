from discord.ext import commands

from .log import logger


class Administration(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(help='Deletes most recent messages on the channel')
    @commands.has_permissions(manage_messages=True)
    async def dispose(self, ctx: commands.context.Context, amount=10):
        end = 's' if amount > 1 else ''
        logger.info(f'Clearing the {amount} most recent message{end}'
                    f' from {ctx.channel.name} channel on {ctx.channel.guild.name} server')
        await ctx.channel.purge(limit=amount)


def setup(client: commands.Bot):
    client.add_cog(Administration(client))
