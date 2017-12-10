# coding=utf-8

from collections import namedtuple

_IGNORE_LASTRUN_CHAR = '|'
_ALIAS = '~'
_COMMENT_CHAR = '#'

Query = namedtuple('Query', ['text', 'alias', 'ignore_lastrun'])

class Taglist:
    @staticmethod
    def factory(fp):
        queries = []
        for line in fp:
            query = Taglist._parse_taglist_line(line)
            if query:
                queries.append(query)
        return queries

    @staticmethod
    def _parse_taglist_line(raw_text: str) -> Query:

        text = raw_text.strip()
        alias = None
        ignore_lastrun = False

        # if there is a comment halfway through the line, remove anything after it
        if _COMMENT_CHAR in text:
            text = text.split(_COMMENT_CHAR)[0].strip()
            if not text:
                return None

        # if the line starts with the fast-forward char, set that field true
        if text.startswith(_IGNORE_LASTRUN_CHAR):
            ignore_lastrun = True
            text = text.replace(_IGNORE_LASTRUN_CHAR, '').strip()

        # if there's an alias,
        if _ALIAS in text:
            text, alias = (x.strip() for x in text.split(_ALIAS, maxsplit=1))
            if not alias.strip():
                alias = None

        if not text:
            return None

        return Query(text.strip(), alias, ignore_lastrun)
