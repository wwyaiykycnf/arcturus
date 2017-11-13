# coding=utf-8
"""tests for blacklist logic"""

# noinspection PyUnresolvedReferences,PyPep8
from arcturus.blacklist import Blacklist

all_posts = [
    ['a'], ['b'], ['c'], ['d'], ['e'], ['f'],
    ['a', 'b'], ['b', 'c'], ['c', 'd'], ['e', 'f'],
    ['a', 'b', 'c'], ['b' 'c', 'd'], ['c', 'd', 'e'], ['d', 'e', 'f'],
    ['a', 'b', 'c', 'd'], ['b', 'c', 'd', 'e'],
    ['a', 'b', 'c', 'd', 'e'], ['b', 'c', 'd', 'e', 'f'],
]


def test_single_pos_term():
    f = Blacklist(blacklist=['a'])
    for post in all_posts:
        assert ('a' in post) == f.is_blacklisted(post)


def test_single_negative_term():
    f = Blacklist(blacklist=['-a'])
    for post in all_posts:
        assert ('a' not in post) == f.is_blacklisted(post)


def test_two_pos():
    f = Blacklist(blacklist=['a b'])
    for post in all_posts:
        assert ('a' in post and 'b' in post) == f.is_blacklisted(post)


def test_three_pos():
    f = Blacklist(blacklist=['a b c'])
    for post in all_posts:
        assert ('a' in post and 'b' in post and 'c' in post) == f.is_blacklisted(post)


def test_two_negative():
    f = Blacklist(blacklist=['-a -b'])
    for post in all_posts:
        assert ('a' not in post and 'b' not in post) == f.is_blacklisted(post)


def test_three_neg():
    f = Blacklist(blacklist=['-a -b -c'])
    for post in all_posts:
        assert ('a' not in post and 'b' not in post and 'c' not in post) == f.is_blacklisted(post)


def test_pos_neg():
    f = Blacklist(blacklist=['a -b'])
    for post in all_posts:
        assert ('a' in post and 'b' not in post) == f.is_blacklisted(post)


def test_pos_two_neg():
    f = Blacklist(blacklist=['a -b -c'])
    for post in all_posts:
        assert ('a' in post and 'b' not in post and 'c' not in post) == f.is_blacklisted(post)


def test_two_pos_one_neg():
    f = Blacklist(blacklist=['a b -c'])
    for post in all_posts:
        assert ('a' in post and 'b' in post and 'c' not in post) == f.is_blacklisted(post)


def test_double_pos_double_neg():
    f = Blacklist(blacklist=['a b -c -d'])
    for post in all_posts:
        assert (('a' in post and 'b' in post) and ('c' not in post and 'd' not in post)) == f.is_blacklisted(post)


def test_two_line_simple():
    f = Blacklist(blacklist=['a', 'b'])
    for post in all_posts:
        assert ('a' in post or 'b' in post) == f.is_blacklisted(post)


def test_two_line_neg():
    f = Blacklist(blacklist=['-a', '-b'])
    for post in all_posts:
        assert ('a' not in post or 'b' not in post) == f.is_blacklisted(post)
