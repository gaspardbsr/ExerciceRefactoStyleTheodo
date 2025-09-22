# tests/test_articles.py
import unittest
from app import app, users_db, articles_db
from datetime import datetime, timedelta

class ArticleAPITestCase(unittest.TestCase):

    def setUp(self):
        users_db.clear()
        articles_db.clear()
        self.app = app.test_client()
        self.app.testing = True

        # Créer un utilisateur pour associer les articles
        self.app.post('/users', json={'name': 'Test User', 'email': 'test@example.com'})
        self.user_id = 1

    def test_create_article_success(self):
        response = self.app.post('/articles', json={
            'user_id': self.user_id,
            'title': 'My First Article',
            'content': 'This is the content.',
            'tags': 'python,flask'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('My First Article', str(response.data))
        self.assertEqual(len(articles_db), 1)
        self.assertIn('python', articles_db[1]['tags'])
        self.assertIn('flask', articles_db[1]['tags'])
        
    def test_create_article_missing_fields(self):
        response = self.app.post('/articles', json={
            'user_id': self.user_id,
            'title': 'My First Article'
            # Content is missing
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("user_id, title, and content are required", str(response.data))

    def test_create_article_user_not_found(self):
        response = self.app.post('/articles', json={
            'user_id': 999, # User inexistant
            'title': 'Invalid User Article',
            'content': 'Content here.'
        })
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", str(response.data))

    def test_get_articles_empty(self):
        response = self.app.get('/articles')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    def test_get_articles_with_data(self):
        self.app.post('/articles', json={'user_id': self.user_id, 'title': 'Art1', 'content': 'C1'})
        self.app.post('/articles', json={'user_id': self.user_id, 'title': 'Art2', 'content': 'C2'})
        response = self.app.get('/articles')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertIn('Art1', str(response.json))

    def test_get_articles_filter_by_tag(self):
        self.app.post('/articles', json={'user_id': self.user_id, 'title': 'Art1', 'content': 'C1', 'tags': 'python'})
        self.app.post('/articles', json={'user_id': self.user_id, 'title': 'Art2', 'content': 'C2', 'tags': 'flask,python'})
        self.app.post('/articles', json={'user_id': self.user_id, 'title': 'Art3', 'content': 'C3', 'tags': 'java'})

        response = self.app.get('/articles?tag=python')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertIn('Art1', str(response.json))
        self.assertIn('Art2', str(response.json))
        self.assertNotIn('Art3', str(response.json))

    def test_get_articles_filter_by_date_after(self):
        # Créer des articles avec des dates spécifiques pour le test
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)

        # Utilisation directe de articles_db pour contrôler les dates
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
        self.assertIn('Recent Article', str(response.json))
        self.assertIn('Future Article', str(response.json))
        self.assertNotIn('Old Article', str(response.json))

    def test_get_articles_filter_invalid_date_format(self):
        response = self.app.get('/articles?date_after=not-a-date')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid date_after format", str(response.data))

    def test_get_single_article_success(self):
        self.app.post('/articles', json={'user_id': self.user_id, 'title': 'Single Article', 'content': 'Content'})
        response = self.app.get('/articles/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['title'], 'Single Article')

    def test_get_single_article_not_found(self):
        response = self.app.get('/articles/999')
        self.assertEqual(response.status_code, 404)
        self.assertIn("Article not found", str(response.data))

    # Manque des tests pour l'update et le delete des articles !
    # Manque des tests pour la validation des tags lors de la création
    # Manque des tests pour des cas d'erreur spécifiques (ex: utilisateur supprime son article)


if __name__ == '__main__':
    unittest.main()