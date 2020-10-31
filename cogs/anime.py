from typing import Dict

import aiohttp
import requests
import discord
import json

from discord.ext import commands
from saucenao_api.containers import SauceResponse, VideoSauce

from api import tracemoe
from saucenao_api import SauceNao

from api.tracemoe import TraceMoe
from .log import logger


class MultipleImagesQueryError(commands.CommandError):
    def __init__(self):
        super().__init__(message='Multiple images search query is not supported.')


class ImageFormatError(commands.CommandError):
    def __init__(self):
        super().__init__(message='Image format is not supported.')


class AnimeEngine(commands.Cog):
    COLOR_DICT = {'blue': discord.Color.blue(),
                  'red': discord.Color.red(),
                  'green': discord.Color.green()}

    def __init__(self, client):
        self.client = client
        self.tracemoe = TraceMoe()

    @property
    def description(self):
        return 'Anime search engine'

    @commands.command(help='Searches for anime screenshots using trace.moe API',
                      description='Life is too short to answer all the "What is the anime?" questions. Let computers '
                                  'do that for you.\nYou can provide any screenshot '
                                  'from an aired anime by either a url or an attachment '
                                  'and I will try to find the source of it as long as it is in these formats '
                                  'Jpg, Png, or Bmp')
    async def what(self, ctx: commands.context.Context, url=None):
        if url is None:
            logger.info('Attachment search query.')
            if ctx.message.attachments:
                raise commands.MissingRequiredArgument(param='image attachment')
            elif len(ctx.message.attachments) == 1:
                attachment_url = ctx.message.attachments[0].url
                try:
                    response = await self.tracemoe.from_url(attachment_url)
                    await ctx.send(embed=self.create_tracemoe_info_embed(response))
                except tracemoe.ImageFormatError:
                    raise ImageFormatError
            else:
                raise MultipleImagesQueryError
        else:
            logger.info('Url search query.')
            try:
                response = await self.tracemoe.from_url(url)
                await ctx.send(embed=self.create_tracemoe_info_embed(response))
            except tracemoe.ImageFormatError:
                raise ImageFormatError

    @commands.command(help='Searches for anime pictures source using SauceNAO API',
                      description='No need to ask anybody for the sauce! let computers help you.\n'
                                  'You can provide any anime illustration by either a url or an attachment '
                                  'and I will try to find the source of it'
                                  ' in various databases including but not limited to: '
                                  'Pixiv, Danbooru, DeviantArt and an original anime database')
    async def sauce(self, ctx, url=None):
        sauce = SauceNao()
        if url is None:
            logger.info('Attachment search query.')
            if ctx.message.attachments:
                raise commands.MissingRequiredArgument(param='image attachment')
            elif len(ctx.message.attachments) == 1:
                attachment_url = ctx.message.attachments[0].url
                response = sauce.from_url(attachment_url)
                await ctx.send(embed=self.create_sauce_info_embed(response))
            else:
                raise MultipleImagesQueryError
        else:
            logger.info('Url search query.')
            response = sauce.from_url(url)
            await ctx.send(embed=self.create_sauce_info_embed(response))

    @commands.command(help='', description='')
    async def info(self, ctx, name):
        # TODO integrate Anilist API
        pass

    def create_tracemoe_info_embed(self, response: Dict):

        docs = response['docs']

        docs.sort(key=lambda obj: obj['similarity'], reverse=True)

        top_result = docs[0]

        tracemoe_thumbnail_url = await self.tracemoe.get_thumbnail_url(top_result)

        # TODO add anilist cover thumbnail
        similarity = int(top_result['similarity'] * 100)
        embed = discord.Embed(
            title=''.join([top_result['title_romaji'], ' #', f"{top_result['episode']}"]),
            color=AnimeEngine.COLOR_DICT[(lambda x: 'red' if x < 87 else 'blue' if x < 93 else 'green')(similarity)])

        embed.add_field(name='Timestamp', value=''.join([str(round(top_result['at'] / 60, 1))]))
        embed.add_field(name='Similarity', value=''.join([str(similarity), '%']))
        embed.add_field(name='Anilist ID', value=str(top_result['anilist_id']), inline=False)
        embed.add_field(name='MAL ID', value=str(top_result['mal_id']))

        embed.set_image(url=tracemoe_thumbnail_url)
        # embed.set_thumbnail(url=anilist_cover_url)

        embed.set_footer(text='Brought to you by Nitro')

        return embed

    @staticmethod
    def create_sauce_info_embed(response: SauceResponse):
        top_result = response[0]

        sauce_thumbnail_url = top_result.thumbnail

        similarity = int(top_result.similarity)
        embed = discord.Embed(
            title=top_result.title,
            color=AnimeEngine.COLOR_DICT[(lambda x: 'red' if x < 75 else 'blue' if x < 93 else 'green')(similarity)])

        if isinstance(top_result, VideoSauce):
            embed.add_field(name='Episode', value=top_result.part)
            embed.add_field(name='Est Time', value=top_result.est_time)

        embed.add_field(name='Similarity', value=''.join([str(similarity), '%']))

        embed.set_image(url=sauce_thumbnail_url)

        embed.set_footer(text='Brought to you by Nitro')

        return embed


def setup(client: commands.Bot):
    client.add_cog(AnimeEngine(client))
