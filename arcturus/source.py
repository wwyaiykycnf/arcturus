# coding=utf-8
import datetime
import abc
from .blacklist import Blacklist
from typing import List


class Post:
    def __init__(self, url, tags, uid, ext):
        self.url = url
        self.tags = tags
        self.id = uid
        self.ext = ext

    @property
    def url(self):
        return self.url

    @property
    def tags(self):
        return self.tags

    @property
    def uid(self):
        return self.uid

    @property
    def ext(self):
        return self.ext


class Source(abc.ABC):
    @abc.abstractmethod
    def __init__(self,
                 date: datetime.date = datetime.date.min,
                 blacklist: Blacklist = Blacklist([]),
                 username=None,
                 password=None):
        pass

    @abc.abstractmethod
    def get_posts(self, query: str, blacklist: filter = Blacklist) -> List[Post]:
        pass
