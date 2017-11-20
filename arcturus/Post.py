# coding=utf-8

import typing

class Post:
    def __init__(self, url: str, tags: typing.Optional[typing.Iterable[str]], md5: str, filename: str, ext: str):
        self._url = url
        self._tags = tags
        self._md5 = md5
        self._ext = ext

    @property
    def url(self):
        return self._url

    @property
    def tags(self):
        return self._tags

    @property
    def md5(self):
        return self._md5

    @property
    def ext(self):
        return self._ext
