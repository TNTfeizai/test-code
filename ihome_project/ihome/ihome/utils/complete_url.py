from django.conf import settings


def Url(url):
    """拼接完整lujing"""
    url = settings.FDFS_URL + url
    return url
