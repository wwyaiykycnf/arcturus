# coding=utf-8

import abc
import datetime
import io
import logging
from pathlib import Path
from queue import Queue
from string import Template
from typing import Optional, Iterable
from multiprocessing import Pool

import requests

import arcturus.ArcturusSources.Source as Source
from .import ArcturusSources
from .Blacklist import Blacklist
from .Post import Post

NAME = "Arcturus"

PYTHON_REQUIRED_MAJOR = 3
PYTHON_REQUIRED_MINOR = 6


class ArcturusError(Exception):
    """base exception class for all Arcturus exceptions"""

class ArcturusCore:
    """central class of the program which takes configuration information and downloads from a data source"""

    def __init__(self,
                 source: Source,
                 taglist: Iterable[str],
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
        self._update_method = self._get_posts_filtered if self._blacklist else self._get_posts_unfiltered

    def _get_posts_unfiltered(self):
        for line in self._taglist:
            for post in self._source.get_posts(query=line):
                yield post

    def _get_posts_filtered(self):
        for line in self._taglist:
            for post in self._source.get_posts(query=line):
                if not self._blacklist.is_blacklisted(post.tags):
                    yield post

    def get_posts(self):
        if self._cache:
            for post in self._update_method():
                if post.md5 in self._cache:
                    continue
                else:
                    self._pending_downloads.put(post)

        else:  # no cache.  just download it all
            for post in self._update_method():
                self._pending_downloads.put(post)

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

    def download(self, namefmt: Optional[str]):
        p = Pool(1)
        p.map(self._print_post, self._pending_downloads)
