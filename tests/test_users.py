# tests/test_users.py
import unittest
from app import app, users_db, articles_db 
from datetime import datetime, timedelta


class BaseAPITestCase(unittest.TestCase): # Pas de unittest.TestCase ici !
    
    def setUp(self):
        users_db.clear() 
        articles_db.clear()
        self.app = app.test_client()
        self.app.testing = True

# --- Classe de test concrète pour les Users ---
class UserRouteTestCase(BaseAPITestCase): # Hérite de unittest.TestCase ici
    
    def setUp(self):
        super().setUp()
        self.db = users_db

    def test_create_success(self):
        response = self.app.post('/users', json={'name': 'Alice', 'email': 'alice@example.com'})
        self.assertEqual(response.status_code, 201)
        self.assertIn('Alice', str(response.data))
        self.assertEqual(len(users_db), 1)

    def test_create_missing_name(self):
        response = self.app.post('/users', json={'email': 'bob@example.com'})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Name and email are required", str(response.data))
    
    def test_create_missing_email(self):
        response = self.app.post('/users', json={'name': 'Alice'})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Name and email are required", str(response.data))

    def test_create_invalid_email(self):
        response = self.app.post('/users', json={'name': 'Charlie', 'email': 'invalid-email'})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid email format", str(response.data))
        
    def test_create_duplicate_email(self):
        self.app.post('/users', json={'name': 'Alice', 'email': 'alice@example.com'})
        response = self.app.post('/users', json={'name': 'Bob', 'email': 'alice@example.com'})
        self.assertEqual(response.status_code, 409)
        self.assertIn("User with this email already exists", str(response.data))

    def test_get_empty(self):
        response = self.app.get('/users')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    def test_get_with_data(self):
        self.app.post('/users', json={'name': 'Alice', 'email': 'alice@example.com'})
        self.app.post('/users', json={'name': 'Bob', 'email': 'bob@example.com'})
        response = self.app.get('/users')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        # Assurez-vous que les données sont bien dans la réponse JSON, pas juste la chaîne
        self.assertTrue(any(user['name'] == 'Alice' for user in response.json))

    def test_get_single_success(self):
        self.app.post('/users', json={'name': 'Alice', 'email': 'alice@example.com'})
        response = self.app.get('/users/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Alice')

    def test_get_single_not_found(self):
        response = self.app.get('/users/999')
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", str(response.data))

    def test_update_name(self):
        self.app.post('/users', json={'name': 'Alice', 'email': 'alice@example.com'})
        response = self.app.put('/users/1', json={'name': 'Alicia'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(users_db[1]['name'], 'Alicia')

    def test_update_email(self):
        self.app.post('/users', json={'name': 'Alice', 'email': 'alice@example.com'})
        response = self.app.put('/users/1', json={'email': 'alicia_new@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(users_db[1]['email'], 'alicia_new@example.com')
        
    def test_update_duplicate_email(self):
        self.app.post('/users', json={'name': 'Alice', 'email': 'alice@example.com'})
        self.app.post('/users', json={'name': 'Bob', 'email': 'bob@example.com'})
        response = self.app.put('/users/1', json={'email': 'bob@example.com'})
        self.assertEqual(response.status_code, 409)
        self.assertIn("User with this email already exists", str(response.data))


    def test_delete_success(self):
        self.app.post('/users', json={'name': 'Alice', 'email': 'alice@example.com'})
        response = self.app.delete('/users/1')
        self.assertEqual(response.status_code, 204)
        self.assertNotIn(1, users_db)

    def test_delete_not_found(self):
        response = self.app.delete('/users/999')
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", str(response.data))

    def test_delete_also_deletes_articles(self):
        self.app.post('/users', json={'name': 'Alice', 'email': 'alice@example.com'})
        self.app.post('/articles', json={'user_id': 1, 'title': 'Article 1', 'content': 'Content 1'})
        self.app.post('/articles', json={'user_id': 1, 'title': 'Article 2', 'content': 'Content 2'})
        
        self.assertEqual(len(articles_db), 2)
        
        self.app.delete('/users/1')
        self.assertEqual(len(articles_db), 0)

# --- Classe de test concrète pour les Articles ---
class ArticlesRouteTestCase(BaseAPITestCase): 
    
    def setUp(self):
        super().setUp()
        self.db = articles_db
        self.user_id = 1
        self.app.post('/users', json={'name': 'Test User For Articles', 'email': 'article_user@example.com'})

    def test_create_success(self):
        response = self.app.post('/articles', json={'user_id': self.user_id, 'title': 'Article Test', 'content': 'Content test'})
        self.assertEqual(response.status_code, 201)
        self.assertIn('Article Test', str(response.data))
        self.assertEqual(len(articles_db), 1) 

    def test_create_missing_id(self):
        response = self.app.post('/articles', json={'title': 'Article 1', 'content': 'Content 1'})
        self.assertEqual(response.status_code, 400)
        self.assertIn("user_id, title, and content are required", str(response.data))

    def test_create_missing_title(self):
        response = self.app.post('/articles', json={'user_id': self.user_id, 'content': 'Content 1'})
        self.assertEqual(response.status_code, 400)
        self.assertIn("user_id, title, and content are required", str(response.data))

    def test_create_missing_content(self):
        response = self.app.post('/articles', json={'user_id': self.user_id, 'title': 'Article 1'})
        self.assertEqual(response.status_code, 400)
        self.assertIn("user_id, title, and content are required", str(response.data))

    def test_create_invalid_user_id(self):
        response = self.app.post('/articles', json={'user_id': 999, 'title': 'Article 1', 'content': 'Content 1'})
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", str(response.data))
    
    def test_get_empty(self):
        response = self.app.get('/articles')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    def test_get_with_data(self):
        self.app.post('/articles', json={'user_id': self.user_id, 'title': 'Article 1', 'content': 'Content 1'})
        self.app.post('/articles', json={'user_id': self.user_id, 'title': 'Article 2', 'content': 'Content 2'})
        response = self.app.get('/articles')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertTrue(any(article['title'] == 'Article 1' for article in response.json))
        self.assertTrue(any(article['title'] == 'Article 2' for article in response.json))

    def test_get_single_success(self):
        self.app.post('/articles', json={'user_id': self.user_id, 'title': 'Article 1', 'content': 'Content 1'})
        response = self.app.get('/articles/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['title'], 'Article 1')

    def test_get_single_not_found(self):
        response = self.app.get('/articles/999')
        self.assertEqual(response.status_code, 404)
        self.assertIn("Article not found", str(response.data))

    def test_get_articles_filter_by_tag(self):
        self.app.post('/articles', json={'user_id': self.user_id, 'title': 'Art1', 'content': 'C1', 'tags': 'python'})
        self.app.post('/articles', json={'user_id': self.user_id, 'title': 'Art2', 'content': 'C2', 'tags': 'flask,python'})
        self.app.post('/articles', json={'user_id': self.user_id, 'title': 'Art3', 'content': 'C3', 'tags': 'java'})

        response = self.app.get('/articles?tag=python')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertTrue(any(article['title'] == 'Art1' for article in response.json))
        self.assertTrue(any(article['title'] == 'Art2' for article in response.json))
        self.assertFalse(any(article['title'] == 'Art3' for article in response.json))

    def test_get_articles_filter_by_date_after(self):
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)

        articles_db[1] = {'id': 1, 'user_id': self.user_id, 'title': 'Old Article', 'content': 'Old', 'tags': [], 'created_at': yesterday}
        articles_db[2] = {'id': 2, 'user_id': self.user_id, 'title': 'Recent Article', 'content': 'Recent', 'tags': [], 'created_at': now}
        articles_db[3] = {'id': 3, 'user_id': self.user_id, 'title': 'Future Article', 'content': 'Future', 'tags': [], 'created_at': tomorrow}

        date_filter_str = yesterday.strftime("%Y-%m-%d")
        response = self.app.get(f'/articles?date_after={date_filter_str}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 3) # yesterday, now, tomorrow

        date_filter_str = now.strftime("%Y-%m-%d")
        response = self.app.get(f'/articles?date_after={date_filter_str}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2) # now, tomorrow
        self.assertTrue(any(article['title'] == 'Recent Article' for article in response.json))
        self.assertTrue(any(article['title'] == 'Future Article' for article in response.json))
        self.assertFalse(any(article['title'] == 'Old Article' for article in response.json))

    def test_get_articles_filter_invalid_date_format(self):
        response = self.app.get('/articles?date_after=not-a-date')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid date_after format", str(response.data))


if __name__ == '__main__':
    unittest.main()