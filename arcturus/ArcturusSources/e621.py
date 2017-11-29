# coding=utf-8

import abc
import datetime
import typing
from ..Post import Post
from ..Blacklist import Blacklist

class E621(abc.ABC):
    def __init__(self,
                 date: typing.Optional[datetime.date],
                 blacklist: typing.Optional[Blacklist],
                 username: typing.Optional[str],
                 password: typing.Optional[str]):

        super().__init__(date, blacklist, username, password)

    def get_posts(self, query: str) -> typing.Iterable[Post]:
        pass

    def _get_page(self, query: str, page_num: int):
        pass
    
