import os
import unittest
import tempfile
import flaskr


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, flaskr.APP.config['DATABASE'] = tempfile.mkstemp()
        flaskr.APP.config['TEST'] = True
        self.app = flaskr.APP.test_client()
        flaskr.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskr.APP.config['DATABASE'])

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_empty_db(self):
        _rv = self.app.get('/')
        assert 'No entries here so far' in _rv.data

    def test_login_logout(self):
        _rv = self.login(username='admin', password='admin')
        assert 'You were logged in' in _rv.data
        _rv = self.logout()
        assert 'You were logged out' in _rv.data
        _rv = self.login(username='adminx', password='admin')
        assert 'Invalid username' in _rv.data
        _rv = self.login(username='admin', password='adminx')
        assert 'Invalid password' in _rv.data
        _rv = self.login(username='adminx', password='adminx')
        assert 'Invalid username' in _rv.data

    def test_msgs(self):
        self.login(username='admin', password='admin')
        _rv = self.app.post('/add/', data=dict(
            title='this is title',
            text='this is text'
        ), follow_redirects=True)
        assert 'New entry has been successfully posted' in _rv.data
        assert 'this is title' in _rv.data
        assert 'this is text' in _rv.data


if __name__ == '__main__':
    unittest.main()
