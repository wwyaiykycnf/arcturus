# coding=utf-8

from abc import ABC
from datetime import date
from typing import Optional, Generator
from ..Post import Post
from ..Blacklist import Blacklist

class E621(ABC):
    def __init__(self,
                 date: Optional[date],
                 blacklist: Optional[Blacklist],
                 username: Optional[str],
                 password: Optional[str]):

        super().__init__(date, blacklist, username, password)

    def get_posts(self, query: str, alias: Optional[str], lastrun: Optional[date]) -> Generator[Post, None, None]:
        pass

    def _get_page(self, query: str, page_num: int):
        pass

