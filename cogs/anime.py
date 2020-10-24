from discord.ext import commands
from api.tracemoe import AnimeTracer

from .log import logger


class AnimeEngine(commands.Cog):

    class MultipleImagesQueryError(commands.CommandError):
        def __init__(self):
            super().__init__(message='multiple images search query is not supported.')

    class ImageFormatError(commands.CommandError):
        def __init__(self):
            super().__init__(message='image format is not supported.')

    def __init__(self, client):
        self.client = client

    @property
    def description(self):
        return 'Anime search engine'

    @commands.command()
    async def what(self, ctx: commands.context.Context, url=None):
        if url is None:
            logger.info('attachment search query.')
            if ctx.message.attachments:
                raise commands.MissingRequiredArgument(param='image attachment')
            elif len(ctx.message.attachments) == 1:
                attachment_url = ctx.message.attachments[0].url
                if AnimeTracer.check_image_type(attachment_url):
                    # TODO send query to trace.moe api
                    pass
                else:
                    raise self.ImageFormatError
            else:
                raise self.MultipleImagesQueryError
        else:
            logger.info('url search query.')
            if AnimeTracer.check_image_type(url):
                # TODO send query to trace.moe api
                pass
            else:
                raise self.ImageFormatError


def setup(client: commands.Bot):
    client.add_cog(AnimeEngine(client))
