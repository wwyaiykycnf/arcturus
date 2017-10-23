# coding=utf-8
"""tests for blacklist logic"""
import unittest
import sys
sys.path.append('../arcturus')

# noinspection PyUnresolvedReferences,PyPep8
from blacklist import Filter

all_posts = [
    ['a'], ['b'], ['c'], ['d'], ['e'], ['f'],
    ['a', 'b'], ['b', 'c'], ['c', 'd'], ['e', 'f'],
    ['a', 'b', 'c'], ['b' 'c', 'd'], ['c', 'd', 'e'], ['d', 'e', 'f'],
    ['a', 'b', 'c', 'd'], ['b', 'c', 'd', 'e'],
    ['a', 'b', 'c', 'd', 'e'], ['b', 'c', 'd', 'e', 'f'],
]


class SimpleTests(unittest.TestCase):
    def test_single_pos_term(self):
        f = Filter(blacklist=['a'])
        for post in all_posts:
            if 'a' in post:
                self.assertTrue(f.is_blacklisted(post))
            else:
                self.assertFalse(f.is_blacklisted(post))

    def test_single_negative_term(self):
        f = Filter(blacklist=['-a'])
        for post in all_posts:
            if 'a' not in post:
                self.assertTrue(f.is_blacklisted(post))
            else:
                self.assertFalse(f.is_blacklisted(post))


class MultipleItemTests(unittest.TestCase):
    def test_two_pos(self):
        f = Filter(blacklist=['a b'])
        for post in all_posts:
            if 'a' in post and 'b' in post:
                self.assertTrue(f.is_blacklisted(post))
            else:
                self.assertFalse(f.is_blacklisted(post))

    def test_three_pos(self):
        f = Filter(blacklist=['a b c'])
        for post in all_posts:
            if 'a' in post and 'b' in post and 'c' in post:
                self.assertTrue(f.is_blacklisted(post))
            else:
                self.assertFalse(f.is_blacklisted(post))

    def test_two_negative(self):
        f = Filter(blacklist=['-a -b'])
        for post in all_posts:
            if 'a' not in post and 'b' not in post:
                self.assertTrue(f.is_blacklisted(post))
            else:
                self.assertFalse(f.is_blacklisted(post))

    def test_three_negative(self):
        f = Filter(blacklist=['-a -b -c'])
        for post in all_posts:
            if 'a' not in post and 'b' not in post and 'c' not in post:
                self.assertTrue(f.is_blacklisted(post))
            else:
                self.assertFalse(f.is_blacklisted(post))


class CombinationTests(unittest.TestCase):
    def test_pos_neg(self):
        f = Filter(blacklist=['a -b'])
        for post in all_posts:
            if 'a' in post and 'b' not in post:
                self.assertTrue(f.is_blacklisted(post))
            else:
                self.assertFalse(f.is_blacklisted(post))

    def test_pos_two_neg(self):
        f = Filter(blacklist=['a -b -c'])
        for post in all_posts:
            if 'a' in post and 'b' not in post and 'c' not in post:
                self.assertTrue(f.is_blacklisted(post))
            else:
                self.assertFalse(f.is_blacklisted(post))

    def test_two_pos_one_neg(self):
        f = Filter(blacklist=['a b -c'])
        for post in all_posts:
            if 'a' in post and 'b' in post and 'c' not in post:
                self.assertTrue(f.is_blacklisted(post))
            else:
                self.assertFalse(f.is_blacklisted(post))

    def test_double_pos_double_neg(self):
        f = Filter(blacklist=['a', 'b', '-c', '-d'])
        for post in all_posts:
            if ('a' in post and 'b' in post) and ('c' not in post and 'd' not in post):
                self.assertTrue(f.is_blacklisted(post))


class MultiLineBlacklist(unittest.TestCase):
    def test_two_line_simple(self):
        f = Filter(blacklist=['a', 'b'])
        for post in all_posts:
            if 'a' in post or 'b' in post:
                self.assertTrue(f.is_blacklisted(post))
            else:
                self.assertFalse(f.is_blacklisted(post))

    def test_two_line_neg(self):
        f = Filter(blacklist=['-a', '-b'])
        for post in all_posts:
            if 'a' not in post or 'b' not in post:
                self.assertTrue(f.is_blacklisted(post))
            else:
                self.assertFalse(f.is_blacklisted(post))


if __name__ == '__main__':
    unittest.main(verbosity=2)