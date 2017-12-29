# coding=utf-8

from datetime import datetime
from typing import Optional, Generator
from ..Post import Post
from ..Blacklist import Blacklist
from .Source import Source
import requests
import os.path
import logging
from ..version import VERSION
from ..ArcturusCore import NAME

USER_AGENT = f"{NAME}/{VERSION} (by wwyaiykycnf1)"


class source(Source):

    def __init__(self,
                 date: Optional[date] = None,
                 blacklist: Optional[Blacklist] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None):

        super().__init__(date, blacklist, username, password)
        self._list_url = 'https://e621.net/post/index.json?'
        self._session = requests.Session()
        self._session.headers.update({'User-Agent': USER_AGENT})


    def get_posts(self, query: str, alias: Optional[str], lastrun=None) -> Generator[Post, None, None]:
        while True:
            results = self._get_page(query, 0)

            if len(results) == 0:
                break

            for result in results:
                if lastrun and lastrun < self._get_created_at_datetime(result):
                    yield self._make_post(result)

    def _get_created_at_datetime(self, metadata) -> datetime:
        return datetime.utcfromtimestamp(metadata['created_at']['s'])

    def _make_post(self, metadata):
        return Post(url=metadata["file_url"],
                    tags=metadata["tags"],
                    md5=metadata["md5"],
                    filename=os.path.basename(metadata["file_url"]),
                    ext=metadata["file_ext"]
                    )

    def _get_page(self, query_str: str, page_num: int):
        log = logging.getLogger()
        url = f'{self._list_url}tags={query_str}&page={page_num}'
        log.debug(f"url: {url}")

        response = self._session.get(url)
        log.debug(f"response: status={response.status_code}: {response..reason}")

        try:
            return response.json()
        except ValueError:
            return {}
