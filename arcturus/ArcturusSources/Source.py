from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, Generator
from arcturus.Blacklist import Blacklist
from arcturus.Post import Post

class Source(ABC):
    def __init__(self,
                 date: Optional[date] = None,
                 blacklist: Optional[Blacklist] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None
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
    def get_posts(self, query: str, alias: Optional[str], lastrun=None) -> Generator[Post, None, None]:
        pass
