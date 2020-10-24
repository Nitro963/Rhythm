import requests


class AnimeTracer:

    ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/bmp']

    @staticmethod
    def check_image_type(url):
        response = requests.head(url)
        content_type = response.headers['Content-Type']
        if content_type not in AnimeTracer.ALLOWED_TYPES:
            return False
        return True
