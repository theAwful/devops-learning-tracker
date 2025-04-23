import unittest
from app import create_app, db

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
    
    def test_add_resource(self):
        self.client.post('/register', data={'username': 'test', 'password': 'test123'})
        self.client.post('/login', data={'username': 'test', 'password': 'test123'})
        response = self.client.post('/resources/add', data={
            'title': 'Docker Docs',
            'url': 'https://docs.docker.com',
            'notes': 'Official guide',
            'category': 'Docker',
            'tags': 'Beginner'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Docker Docs', response.data)
    
    def test_add_goal(self):
        self.client.post('/register', data={'username': 'test', 'password': 'test123'})
        self.client.post('/login', data={'username': 'test', 'password': 'test123'})
        response = self.client.post('/goals/add', data={
            'title': 'Learn Docker',
            'deadline': '2025-05-15',
            'points': 20,
            'category': 'Docker'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Learn Docker', response.data)
    
    def test_checkin(self):
        self.client.post('/register', data={'username': 'test', 'password': 'test123'})
        self.client.post('/login', data={'username': 'test', 'password': 'test123'})
        response = self.client.post('/checkin', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'5 Points', response.data)
    
    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
