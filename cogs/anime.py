import inspect
from typing import Dict

import discord

from discord.ext import commands
from saucenao_api.containers import SauceResponse, VideoSauce

from api import tracemoe, anilist
from saucenao_api import SauceNao

from .log import logger


class MultipleImagesQueryError(commands.CommandError):
    def __init__(self):
        super().__init__(message='Multiple images search query is not supported.')


class ImageFormatError(commands.CommandError):
    def __init__(self):
        super().__init__(message='Image format is not supported.')


class AnimeNotFoundError(commands.CommandError):
    def __init__(self):
        super().__init__(message='Can\'t find the specified anime title.')


class ImageAttachmentParameter(inspect.Parameter):
    def __init__(self):
        super().__init__('image_attachment', inspect.Parameter.VAR_KEYWORD)


class AnimeEngine(commands.Cog):
    COLOR_DICT = {'blue': discord.Color.blue(),
                  'red': discord.Color.red(),
                  'green': discord.Color.green()}

    def __init__(self, client):
        self.client = client
        self.tracemoe_api = tracemoe.TraceMoe()
        self.anilist_api = anilist.AnimeList()

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
            if not ctx.message.attachments:
                raise commands.MissingRequiredArgument(param=ImageAttachmentParameter())
            elif len(ctx.message.attachments) == 1:
                attachment_url = ctx.message.attachments[0].url
                try:
                    response = await self.tracemoe_api.from_url(attachment_url)
                    await ctx.send(embed=await self.create_tracemoe_info_embed(response))
                except tracemoe.ImageFormatError:
                    raise ImageFormatError
            else:
                raise MultipleImagesQueryError
        else:
            logger.info('Url search query.')
            try:
                response = await self.tracemoe_api.from_url(url)
                await ctx.send(embed=await self.create_tracemoe_info_embed(response))
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
                await ctx.send(embed=await self.create_sauce_info_embed(response))
            else:
                raise MultipleImagesQueryError
        else:
            logger.info('Url search query.')
            response = sauce.from_url(url)
            await ctx.send(embed=await self.create_sauce_info_embed(response))

    @commands.command(help='', description='')
    async def info(self, ctx, *, name: str):
        logger.info(f'Retrieving information of {name}')
        try:
            response = await self.anilist_api.from_anime_name(name)
            await ctx.send(embed=await self.create_anime_info_embed(response['data']['Media']))
        except anilist.AnimeNotFoundError:
            raise AnimeNotFoundError

    async def create_tracemoe_info_embed(self, response: Dict):

        docs = response['docs']

        docs.sort(key=lambda obj: obj['similarity'], reverse=True)

        top_result = docs[0]

        tracemoe_thumbnail_url = self.tracemoe_api.get_thumbnail_url(top_result)

        similarity = int(top_result['similarity'] * 100)
        embed = discord.Embed(
            title=''.join([top_result['title_romaji'], ' #', f"{top_result['episode']}"]),
            color=AnimeEngine.COLOR_DICT[(lambda x: 'red' if x < 87 else 'blue' if x < 93 else 'green')(similarity)])

        anilist_response = await self.anilist_api.cover_from_anime_id(int(top_result['anilist_id']))

        embed.set_thumbnail(url=anilist_response['data']['Media']['coverImage']['large'])

        embed.add_field(name='Timestamp', value=''.join([str(round(top_result['at'] / 60, 1))]))
        embed.add_field(name='Similarity', value=''.join([str(similarity), '%']))
        embed.add_field(name='Anilist ID', value=str(top_result['anilist_id']), inline=False)
        embed.add_field(name='MAL ID', value=str(top_result['mal_id']))

        embed.set_image(url=tracemoe_thumbnail_url)
        # embed.set_thumbnail(url=anilist_cover_url)

        embed.set_footer(text='Brought to you by Nitro')

        return embed

    async def create_sauce_info_embed(self, response: SauceResponse):
        top_result = response[0]

        sauce_thumbnail_url = top_result.thumbnail

        similarity = int(top_result.similarity)
        embed = discord.Embed(
            title=top_result.title,
            color=self.COLOR_DICT[(lambda x: 'red' if x < 75 else 'blue' if x < 93 else 'green')(similarity)])

        if isinstance(top_result, VideoSauce):
            embed.add_field(name='Episode', value=top_result.part)
            embed.add_field(name='Est Time', value=top_result.est_time)

        embed.add_field(name='Similarity', value=''.join([str(similarity), '%']))

        embed.set_image(url=sauce_thumbnail_url)

        embed.set_footer(text='Brought to you by Nitro')

        return embed

    async def create_anime_info_embed(self, response: Dict):
        embed = discord.Embed(
            title=response['title']['romaji'],
            color=self.COLOR_DICT['blue'])

        embed.set_thumbnail(url=response['coverImage']['large'])

        embed.add_field(name='Genres', value=', '.join(response['genres']), inline=False)

        embed.add_field(name='Premiered', value=' '.join([str.capitalize(response['season']),
                                                          str(response['seasonYear'])
                                                          ]
                                                         ),
                        inline=False)

        embed.add_field(name='Status', value=str.capitalize(response['status']))

        embed.add_field(name='Episodes', value=str(response['episodes']))

        embed.add_field(name='Rating', value=str(response['averageScore'] / 10))

        embed.add_field(name='Duration', value=str(response['duration']), inline=False)

        embed.add_field(name='Source', value=' '.join(list(map(str.capitalize, str.split(response['source'], '_')))))

        embed.add_field(name='Animation Studio',
                        value=', '.join([val['node']['name']
                                         for val in response['studios']['edges']
                                         if val['node']['isAnimationStudio']
                                         ]
                                        ),
                        inline=True)

        prequel = '\n'.join([val['node']['title']['romaji']
                             for val in response['relations']['edges']
                             if val['relationType'] == 'PREQUEL'
                             ]
                            )
        if prequel:
            embed.add_field(name='Prequel',
                            value=prequel,
                            inline=False)

        sequel = '\n'.join([val['node']['title']['romaji']
                            for val in response['relations']['edges']
                            if val['relationType'] == 'SEQUEL'
                            ]
                           )
        if sequel:
            embed.add_field(name='Sequel',
                            value=sequel,
                            inline=False)

        return embed


def setup(client: commands.Bot):
    client.add_cog(AnimeEngine(client))
