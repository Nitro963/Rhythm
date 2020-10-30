import discord
from discord.ext import commands

from .log import logger


class MemberNotFound(commands.CommandError):
    def __init__(self):
        super().__init__(message='The specified discriminator can\'t be found.')


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

    @commands.command(help='Removes the user from the server and forbid him from coming back')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.context.Context, member: discord.Member, *, reason=None):
        logger.info(f'Banning {member} from {ctx.guild}')
        await member.ban(reason=reason)
        await ctx.send(f'Banned {member.mention}')

    @commands.command(help='Removes the user from the server')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.context.Context, member: discord.Member, *, reason=None):
        logger.info(f'Kicking {member} from {ctx.guild}')
        await member.kick(reason=reason)
        await ctx.send(f'Kicked {member.mention}')

    @commands.command(help='Remove the user join restriction')
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: commands.context.Context, member_discriminator, *, reason=None):
        logger.info(f'Unbanning the user with {member_discriminator} discriminator from {ctx.guild}')
        banned_users = await ctx.guild.bans()
        for ban_entry in banned_users:
            user = ban_entry.user

            if user.discriminator == member_discriminator:
                await ctx.guild.unban(user, reason=reason)
                await ctx.send(f'Unbanned {user.mention}')
                return
        raise MemberNotFound


def setup(client: commands.Bot):
    client.add_cog(Administration(client))
