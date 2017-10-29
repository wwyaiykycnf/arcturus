# coding=utf-8

import typing
import datetime
import logging
import io

from typing import Optional, Iterable

from .source import Source
from .blacklist import Blacklist

def ArcturusError(Exception):
    """base exception class for all Arcturus exceptions"""

class ArcturusCore:
    """central class of the program which takes configuration information and downloads from a data source"""

    def __init__(self,
                 src: Source,
                 lastrun: Optional[datetime.date],
                 taglist: Iterable[str],
                 blacklist: Optional[Blacklist],
                 cache: Optional[io.TextIOBase],
                 **kwargs
                 ):
        # required args
        self._src = src
        self._lastrun = lastrun
        self._taglist = taglist
        self._blacklist = blacklist
        self._cache = cache
        # optional args
        self._kwargs = kwargs
        self._threads = kwargs.get('download_threads', default=4)
        self._nameformat = kwargs.get('download_nameformat', default="$artist_$uid.$ext")
        self._log = logging.getLogger()
        