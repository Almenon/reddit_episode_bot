import unittest
from post_parser import parse,ParseError

with open('info/badPosts.txt') as f:
    badPosts = f.readlines()
with open('info/goodPosts.txt') as f:
    goodPosts = f.readlines()

class TestRegex(unittest.TestCase):

    def test_badPosts(self):
        for badPost in badPosts:
            with self.assertRaises(ParseError):
                parse(badPost)

    def test_goodPosts(self):
        for goodPost in goodPosts:
            try:
                parse(goodPost)
            except ParseError:
                self.fail(goodPost)