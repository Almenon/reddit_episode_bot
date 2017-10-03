import unittest
from post_parser import parse,ParseError
from omdb_requester import get_info,OmdbError
from comment_formatter import format_post_reply

with open('info/badPosts.txt') as f:
    badPosts = f.readlines()
with open('info/goodPosts.txt') as f:
    goodPosts = f.readlines()


class TestRegex(unittest.TestCase):

    def test_bad_posts(self):
        for badPost in badPosts:
            with self.assertRaises(ParseError, msg=badPost):
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


class TestCommentFormatter(unittest.TestCase):

    # def test_all_subreddits(self):
    #     try:
    #         [format_post_reply("s1e1",sub) for sub in subreddits]
    #     except Exception as e:
    #         self.fail(e)

    def test_good_reply(self):
        goodReply = "#####&#009;  \n######&#009;  \n####&#009;  \n" \
        "[**I Wasn't Ready**](http://www.imdb.com/title/tt2400770) [7.8 ★] | " \
        "[Watch on Netflix](http://www.netflix.com/title/70242311) | [imdb](http://www.imdb.com/title/tt2400770)" \
        "\n\n> [Piper Chapman is sent to jail as a result of her relationship with a drug smuggler.](/spoiler)"

        reply = format_post_reply("s1e1","orangeisthenewblack")
        self.assertEqual(reply,goodReply)

    def test_no_netflix(self):
        goodReply = "#####&#009;  \n######&#009;  \n####&#009;  \n" \
        "[**Tourist Trapped**](http://www.imdb.com/title/tt2152239) [8.5 ★] | [imdb](http://www.imdb.com/title/tt2152239)" \
        "\n\n> [After finding a strange book in the forest, Dipper begins to learn about the dark side of Gravity Falls," \
                    " and suspects that Mabel's new boyfriend is a zombie.](#spoiler)"

        reply = format_post_reply("s1e1","gravityfalls")
        self.assertEqual(reply,goodReply)

    # def test_missing_rating(self):
        #  this should be tested once you find another test case
        #  last example got updated

    # def test_missing_plot(self):
        #  this should be tested once you find another test case
        #  last example got updated