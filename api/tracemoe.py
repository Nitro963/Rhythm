import requests
import base64
import json
from typing import Dict

from PIL import Image
from urllib.parse import quote


class ImageFormatError(Exception):
    pass


class AnimeTracer:
    ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/bmp']
    BASE_URL = 'https://trace.moe/'

    @staticmethod
    def check_image_type(url):
        response = requests.head(url)
        content_type = response.headers['Content-Type']
        if content_type not in AnimeTracer.ALLOWED_TYPES:
            return False
        return True

    @staticmethod
    def url_query(url):
        if not AnimeTracer.check_image_type(url):
            raise ImageFormatError
        return requests.get(url=''.join([AnimeTracer.BASE_URL, 'api/', 'search']), params={'url': url})

    @staticmethod
    def image_query(path):

        img = Image.open(path)
        mime_type = ''.join(['image/', img.format])

        if mime_type not in AnimeTracer.ALLOWED_TYPES:
            raise ImageFormatError

        with open(path, "rb") as image_file:
            base64_img = base64.encodebytes(image_file.read())
            response = requests.post(url=''.join([AnimeTracer.BASE_URL, 'api/', 'search']),
                                     data=json.dumps({'image': base64_img.decode('utf-8')}),
                                     headers={'Content-Type': 'application/json'})
            return response

    @staticmethod
    def get_thumbnail_url(document: Dict):
        return f"{AnimeTracer.BASE_URL}thumbnail.php?anilist_id={document['anilist_id']}" \
               f"&file={quote(document['filename'])}&t={document['at']}" \
               f"&token={document['tokenthumb']}"
