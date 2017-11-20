import abc
import datetime
import typing

from typing import Optional
from arcturus.Blacklist import Blacklist
from arcturus.Post import Post

class Source(abc.ABC):
    def __init__(self,
                 date: Optional[datetime.date],
                 blacklist: Optional[Blacklist],
                 username: Optional[str],
                 password: Optional[str]):

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

    @abc.abstractmethod
    def get_posts(self, query: str) -> typing.Iterable[Post]:
        pass
