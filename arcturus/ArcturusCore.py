# coding=utf-8

import logging
import io
import datetime
import abc
import requests

from typing import Optional, Iterable
from queue import Queue
from string import Template
from pathlib import Path

from .blacklist import Blacklist

NAME = "arcturus"

PYTHON_REQUIRED_MAJOR = 3
PYTHON_REQUIRED_MINOR = 6


class ArcturusError(Exception):
    """base exception class for all Arcturus exceptions"""


class Post:
    def __init__(self, url: str, tags: Optional[Iterable[str]], uid: str, ext: str):
        self._url = url
        self._tags = tags
        self._uid = uid
        self._ext = ext

    @property
    def url(self):
        return self._url

    @property
    def tags(self):
        return self._tags

    @property
    def uid(self):
        return self._uid

    @property
    def ext(self):
        return self._ext


class Source(abc.ABC):
    @abc.abstractmethod
    def __init__(self,
                 date: Optional[datetime.date],
                 blacklist: Optional[Blacklist],
                 username: Optional[str],
                 password: Optional[str]):
        pass

    @abc.abstractmethod
    def get_posts(self, query: str) -> Iterable[Post]:
        pass


class ArcturusCore:
    """central class of the program which takes configuration information and downloads from a data source"""

    def __init__(self,
                 src: Source,
                 taglist: Iterable[str],
                 download_dir: Path,
                 lastrun: Optional[datetime.date],
                 blacklist: Optional[Blacklist],
                 cache: Optional[io.TextIOBase],
                 **kwargs
                 ):

        # required args
        self._src = src
        self._taglist = taglist
        self._download_dir = download_dir

        # optional args
        self._lastrun = lastrun
        self._blacklist = blacklist
        self._cache = cache
        self._threads = kwargs.get('download_threads', default=4)
        self._nameformat = kwargs.get('download_nameformat', default="$artist_$uid.$ext")
        self._kwargs = kwargs

        self._log = logging.getLogger()

        # attributes
        self._pending_downloads = Queue()
        self._update_method = self._get_posts_filtered if self._blacklist else self._get_posts_unfiltered

    def _get_posts_unfiltered(self):
        for line in self._taglist:
            for post in self._src.get_posts(query=line):
                yield post

    def _get_posts_filtered(self):
        for line in self._taglist:
            for post in self._src.get_posts(query=line):
                if not self._blacklist.is_blacklisted(post.tags):
                    yield post

    def get_posts(self):
        for post in self._update_method():
            if self._cache and post.uid in self._cache:
                continue
            else:
                self._pending_downloads.put(post)

    def _download_single(self, post: Post):
        filename = Template(self._nameformat).substitute(post.__dict__)
        destination = self._download_dir / Path(filename)
        response = requests.get(post.url, stream=True)
        handle = open(destination, "wb")
        for chunk in response.iter_content(chunk_size=512):
            if chunk:  # filter out keep-alive new chunks
                handle.write(chunk)

    def download(self):
        pass

    def update_lastrun(self):
        pass
