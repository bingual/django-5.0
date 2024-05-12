class ThumbnailFetchError(Exception):
    def __init__(self, message, image_url):
        self.message = message
        self.image_url = image_url
