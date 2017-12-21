# coding=utf-8

import abc
import datetime
import io
import logging
import importlib
from pathlib import Path
from queue import Queue
from string import Template
from typing import Optional, Iterable, Generator
from multiprocessing import Pool


import requests

import arcturus.ArcturusSources.Source as Source
from .import ArcturusSources
from .Blacklist import Blacklist
from .Post import Post
from .Taglist import Query

NAME = "Arcturus"

PYTHON_REQUIRED_MAJOR = 3
PYTHON_REQUIRED_MINOR = 6


class ArcturusError(Exception):
    """base exception class for all Arcturus exceptions"""

class ArcturusCore:
    """central class of the program which takes configuration information and downloads from a data source"""

    def __init__(self,
                 source: Source,
                 taglist: Iterable[Query],
                 download_dir: Path,
                 lastrun: Optional[datetime.date],
                 blacklist: Optional[Blacklist],
                 cache: Optional[io.TextIOBase],
                 **kwargs
                 ):

        # required args
        self._source = source
        self._taglist = taglist
        self._download_dir = download_dir

        # optional args
        self._lastrun = lastrun
        self._blacklist = blacklist
        self._cache = cache
        self._threads = kwargs.get('download_threads', 4)
        self._nameformat = kwargs.get('download_nameformat', "${artist}_${md5}.${ext}")
        self._kwargs = kwargs

        self._log = logging.getLogger()

        # attributes
        self._pending_downloads = Queue()

    @classmethod
    def import_arcturus_source(cls, source_name):
        return importlib.import_module(f'.ArcturusSources.{source_name}', __package__)

    def _get_posts(self) -> Generator[Post, None, None]:
        for line in self._taglist:
            lastrun = self._lastrun
            if line.ignore_lastrun:
                lastrun = None
            for post in self._source.get_posts(query=line.text, alias=line.alias, lastrun=lastrun):

                # these are the individual images / movies / files

                # it has been previously downloaded.  don't download it again
                if self._cache and post.md5 in self._cache:
                    continue

                # if we have a blacklist and this shouldn't be downloaded based on it, skip it
                if self._blacklist and self._blacklist.is_blacklisted(post.tags):
                    continue

                yield post

    def _download_single(self, post: Post):

        filename = Template(self._nameformat).substitute(post.__dict__)
        destination = self._download_dir / Path(filename)
        response = requests.get(post.url, stream=True)
        handle = open(destination, "wb")
        for chunk in response.iter_content(chunk_size=512):
            if chunk:  # filter out keep-alive new chunks
                handle.write(chunk)

    def _print_post(self, post: Post):
        print(post.url)

    def update(self, namefmt: Optional[str], download_method=_download_single):
        p = Pool(1)
        p.map(download_method, self._get_posts())
