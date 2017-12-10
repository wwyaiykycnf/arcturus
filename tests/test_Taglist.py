# coding=utf-8
"""tests for taglist line processing logic"""

# noinspection PyUnresolvedReferences,PyPep8
from arcturus.Taglist import Taglist, Query, _ALIAS, _COMMENT_CHAR, _IGNORE_LASTRUN_CHAR
from arcturus.Taglist import _IGNORE_LASTRUN_CHAR as FF # for "fast forward"
from arcturus.Taglist import _COMMENT_CHAR as CC # for "comment char"
from arcturus.Taglist import _ALIAS as AL # for "ALias"


def test_smoke():
    assert Taglist._parse_taglist_line("foo") == Query("foo", None, False)
    assert Taglist._parse_taglist_line(f"foo {AL} bar") == Query("foo", "bar", False)
    assert Taglist._parse_taglist_line(f"{FF} foo") == Query("foo", None, True)


def test_only_comments():
    for x in [f"{CC}", f"{CC} ", f"{CC*80}",
              f"{CC} comment",
              f"{CC}comment",
              f" {CC} comment",
              f"{CC}{CC} comment",
              f"{CC} double {CC} comment",
              f"{CC} a {FF} b"
              ]:
        assert Taglist._parse_taglist_line(x) == None

def test_text_and_comment():
    assert Taglist._parse_taglist_line("text # comment") == Query("text", None, False)
    assert Taglist._parse_taglist_line("a b # comment") == Query("a b", None, False)
    assert Taglist._parse_taglist_line("-a b # comment") == Query("-a b", None, False)

def test_alias():
    assert Taglist._parse_taglist_line(f"{AL} b") == None
    assert Taglist._parse_taglist_line(f"a {AL} b") == Query("a", "b", False)
    assert Taglist._parse_taglist_line(f"a {AL} b {AL} c") == Query("a", f"b {AL} c", False)
    assert Taglist._parse_taglist_line(f"a b c {AL} z") == Query("a b c", "z", False)
    assert Taglist._parse_taglist_line(f"a {AL} {CC} b") == Query("a", None, False)

def test_fastforward():
    assert Taglist._parse_taglist_line(f"{FF}a") == Query("a", None, True)
    assert Taglist._parse_taglist_line(f"{FF} a") == Query("a", None, True)
    assert Taglist._parse_taglist_line(f" {FF}a") == Query("a", None, True)
    assert Taglist._parse_taglist_line(f" {FF} a") == Query("a", None, True)

def test_complex():
    assert Taglist._parse_taglist_line(f"{FF} a b {AL} z {CC} ignored") == Query("a b", "z", True)

def test_taglist():
    test_lines = [
        f"{CC} comment",
        "a",
        f"b {AL} z",
        f"{FF} c {AL} y",
        f"a b {CC} comment"
    ]
    tl = Taglist.factory(test_lines)

    assert len(tl) == len(test_lines) - 1
    assert tl[0] == Query("a", None, False)
    assert tl[1] == Query("b", "z", False)
    assert tl[2] == Query("c", "y", True)
    assert tl[3] == Query("a b", None, False)
