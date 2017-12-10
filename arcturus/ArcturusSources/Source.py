from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, Generator
from arcturus.Blacklist import Blacklist
from arcturus.Post import Post

class Source(ABC):
    def __init__(self,
                 date: Optional[date],
                 blacklist: Optional[Blacklist],
                 username: Optional[str],
                 password: Optional[str]
                 ):

        self._date = date
        self._blacklist = blacklist
        self._username = username
        self._password = password

    @property
    def date(self):
        return self._date

    @property
    def blacklist(self):
        return self._blacklist

    @property
    def namefmt(self):
        return self._namefmt

    @abstractmethod
    def get_posts(self, query: str, alias: Optional[str], lastrun: Optional[date]) -> Generator[Post, None, None]:
        pass
