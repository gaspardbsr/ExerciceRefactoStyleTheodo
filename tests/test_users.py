# tests/test_users.py
import unittest
from app import app, users_db, articles_db # Accès direct aux bases de données pour les tests

class UserAPITestCase(unittest.TestCase):

    def __init__(self):

    def setUp(self):
        # Réinitialiser les bases de données avant chaque test
        users_db.clear()
        articles_db.clear()
        self.app = app.test_client()
        self.app.testing = True

    def test_create_user_success(self):
        response = self.app.post('/users', json={'name': 'Alice', 'email': 'alice@example.com'})
        self.assertEqual(response.status_code, 201)
        self.assertIn('Alice', str(response.data))
        self.assertEqual(len(users_db), 1)

    def test_create_user_missing_name(self):
        response = self.app.post('/users', json={'email': 'bob@example.com'})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Name and email are required", str(response.data))

    def test_create_user_invalid_email(self):
        response = self.app.post('/users', json={'name': 'Charlie', 'email': 'invalid-email'})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid email format", str(response.data))
        
    def test_create_user_duplicate_email(self):
        self.app.post('/users', json={'name': 'Alice', 'email': 'alice@example.com'})
        response = self.app.post('/users', json={'name': 'Bob', 'email': 'alice@example.com'})
        self.assertEqual(response.status_code, 409)
        self.assertIn("User with this email already exists", str(response.data))

    def test_get_users_empty(self):
        response = self.app.get('/users')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    def test_get_users_with_data(self):
        self.app.post('/users', json={'name': 'Alice', 'email': 'alice@example.com'})
        self.app.post('/users', json={'name': 'Bob', 'email': 'bob@example.com'})
        response = self.app.get('/users')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertIn('Alice', str(response.json))

    def test_get_single_user_success(self):
        self.app.post('/users', json={'name': 'Alice', 'email': 'alice@example.com'})
        response = self.app.get('/users/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Alice')

    def test_get_single_user_not_found(self):
        response = self.app.get('/users/999')
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", str(response.data))

    def test_update_user_name(self):
        self.app.post('/users', json={'name': 'Alice', 'email': 'alice@example.com'})
        response = self.app.put('/users/1', json={'name': 'Alicia'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(users_db[1]['name'], 'Alicia')

    def test_update_user_email(self):
        self.app.post('/users', json={'name': 'Alice', 'email': 'alice@example.com'})
        response = self.app.put('/users/1', json={'email': 'alicia_new@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(users_db[1]['email'], 'alicia_new@example.com')
        
    def test_update_user_duplicate_email(self):
        self.app.post('/users', json={'name': 'Alice', 'email': 'alice@example.com'})
        self.app.post('/users', json={'name': 'Bob', 'email': 'bob@example.com'})
        response = self.app.put('/users/1', json={'email': 'bob@example.com'})
        self.assertEqual(response.status_code, 409)
        self.assertIn("User with this email already exists", str(response.data))


    def test_delete_user_success(self):
        self.app.post('/users', json={'name': 'Alice', 'email': 'alice@example.com'})
        response = self.app.delete('/users/1')
        self.assertEqual(response.status_code, 204)
        self.assertNotIn(1, users_db)

    def test_delete_user_not_found(self):
        response = self.app.delete('/users/999')
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", str(response.data))

    def test_delete_user_also_deletes_articles(self):
        self.app.post('/users', json={'name': 'Alice', 'email': 'alice@example.com'})
        self.app.post('/articles', json={'user_id': 1, 'title': 'Article 1', 'content': 'Content 1'})
        self.app.post('/articles', json={'user_id': 1, 'title': 'Article 2', 'content': 'Content 2'})
        
        self.assertEqual(len(articles_db), 2)
        
        self.app.delete('/users/1')
        self.assertEqual(len(articles_db), 0)


if __name__ == '__main__':
    unittest.main()