import unittest
from post_parser import parse,ParseError
from omdb_requester import get_info,OmdbError

with open('info/badPosts.txt') as f:
    badPosts = f.readlines()
with open('info/goodPosts.txt') as f:
    goodPosts = f.readlines()

class TestRegex(unittest.TestCase):

    def test_bad_posts(self):
        for badPost in badPosts:
            with self.assertRaises(ParseError):
                parse(badPost)

    def test_good_posts(self):
        for goodPost in goodPosts:
            try:
                parse(goodPost)
            except ParseError:
                self.fail(goodPost)

class TestOmdb(unittest.TestCase):

    def test_bad_show(self):
            with self.assertRaises(OmdbError):
                get_info('seafoijosefijo',1,1)

    def test_good_show(self):
        try:
            get_info() # default param is game of thrones, s1e1
        except OmdbError as e:
            self.fail(e)