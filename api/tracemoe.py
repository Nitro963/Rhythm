import base64
import json
import aiohttp

from typing import Dict
from urllib.parse import quote

from PIL import Image


class ImageFormatError(Exception):
    pass


class TraceMoe:
    ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/bmp']
    BASE_URL = 'https://trace.moe/'

    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def check_image_type(self, url):
        response = await self.session.head(url)
        if response.content_type not in TraceMoe.ALLOWED_TYPES:
            return False
        return True

    async def from_url(self, url):
        if not await self.check_image_type(url):
            raise ImageFormatError

        response = await self.session.get(url=''.join([TraceMoe.BASE_URL, 'api/', 'search']), params={'url': url})

        return await response.json()

    async def from_image(self, path):

        img = Image.open(path)
        mime_type = ''.join(['image/', img.format])

        if mime_type not in TraceMoe.ALLOWED_TYPES:
            raise ImageFormatError

        async with open(path, "rb") as image_file:
            base64_img = base64.encodebytes(image_file.read())
            response = await self.session.post(url=''.join([TraceMoe.BASE_URL, 'api/', 'search']),
                                               data=json.dumps({'image': base64_img.decode('utf-8')}),
                                               headers={'Content-Type': 'application/json'})
        return await response.json()

    @staticmethod
    def get_thumbnail_url(document: Dict):
        return f"{TraceMoe.BASE_URL}thumbnail.php?anilist_id={document['anilist_id']}" \
               f"&file={quote(document['filename'])}&t={document['at']}" \
               f"&token={document['tokenthumb']}"

    def __del__(self):
        self.session.close()
        del self.session
