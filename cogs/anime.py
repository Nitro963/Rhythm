import requests
import discord
import json

from discord.ext import commands
from api import tracemoe

from .log import logger


class MultipleImagesQueryError(commands.CommandError):
    def __init__(self):
        super().__init__(message='Multiple images search query is not supported.')


class ImageFormatError(commands.CommandError):
    def __init__(self):
        super().__init__(message='Image format is not supported.')


class AnimeEngine(commands.Cog):

    ColorDict = {'blue': discord.Color.blue(),
                 'red': discord.Color.red(),
                 'green': discord.Color.green()}

    def __init__(self, client):
        self.client = client

    @property
    def description(self):
        return 'Anime search engine'

    @commands.command()
    async def what(self, ctx: commands.context.Context, url=None):
        if url is None:
            logger.info('Attachment search query.')
            if ctx.message.attachments:
                raise commands.MissingRequiredArgument(param='image attachment')
            elif len(ctx.message.attachments) == 1:
                attachment_url = ctx.message.attachments[0].url
                try:
                    response = tracemoe.AnimeTracer.url_query(attachment_url)
                    await ctx.send(embed=AnimeEngine.create_info_embed(response))
                except tracemoe.ImageFormatError:
                    raise ImageFormatError
            else:
                raise MultipleImagesQueryError
        else:
            logger.info('Url search query.')
            try:
                response = tracemoe.AnimeTracer.url_query(url)
                await ctx.send(embed=AnimeEngine.create_info_embed(response))
            except tracemoe.ImageFormatError:
                raise ImageFormatError

    @staticmethod
    def create_info_embed(response: requests.Response):

        response_content = json.loads(response.content.decode('utf-8'))
        docs = response_content['docs']

        docs.sort(key=lambda obj: obj['similarity'], reverse=True)

        top_result = docs[0]

        tracemoe_thumbnail_url = tracemoe.AnimeTracer.get_thumbnail_url(top_result)

        # TODO add anilist cover thumbnail
        similarity = int(top_result['similarity'] * 100)
        embed = discord.Embed(
            title=''.join([top_result['title_romaji'], ' #', f"{top_result['episode']}"]),
            color=AnimeEngine.ColorDict[(lambda x: 'red' if x < 87 else 'blue' if x < 93 else 'green')(similarity)])

        embed.add_field(name='Timestamp', value=''.join([str(round(top_result['at'] / 60, 1))]))
        embed.add_field(name='Similarity', value=''.join([str(similarity), '%']))
        embed.add_field(name='Anilist ID', value=str(top_result['anilist_id']), inline=False)
        embed.add_field(name='MAL ID', value=str(top_result['mal_id']))

        embed.set_image(url=tracemoe_thumbnail_url)
        # embed.set_thumbnail(url=anilist_cover_url)

        embed.set_footer(text='Brought to you by Nitro')

        return embed


def setup(client: commands.Bot):
    client.add_cog(AnimeEngine(client))
