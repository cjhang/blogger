# -*- coding: utf-8 -*-
import os
import blogger
import unittest
import tempfile

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, blogger.app.config['DATABASE'] = tempfile.mkstemp()
        blogger.app.config['TESTING'] = True
        self.app = blogger.app.test_client()
        with blogger.app.app_context():
            blogger.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(blogger.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'No blogs here so far' in rv.data

    def test_displayblogs(self):
        rv = self.app.post('/add', data = dict(
            name = 'test1',
            title_zh = '测试1',
            author = 'test_author',
            release = '2010-10-06',
            revise = '2012-10-06',
            tags = 'test',
            abstract = 'Test1 abstract',
            content = 'This is a test blog content.'))
        rv = self.app.get('/')
        assert b'No blogs here so far' not in rv.data
        assert b'测试1' in rv.data
        assert b'Test1 abstract' in rv.data
        assert b'2012-10-06' in rv.data
        rv = self.app.get('/blogs/test1')
        assert b'测试1' in rv.data
        assert b'2010-10-06' in rv.data
        assert b'2012-10-06' in rv.data
        assert b'This is a test blog content.' in rv.data
        assert b'No comments so far' in rv.data
        rv = self.app.post('/blogs/test1', data = dict(
            user_name = 'tester',
            comment_detail = 'What a good blog!'))
        rv = self.app.get('/blogs/test1')
        assert b'What a good blog!' in rv.data


    # def test_comment(self):
        # rv = self.app.post('/add', data = dict(
            # name = 'test2',
            # content = 'This is a test blog'))
        # rv = self.app.get('/')

if __name__ == '__main__':
    unittest.main()
