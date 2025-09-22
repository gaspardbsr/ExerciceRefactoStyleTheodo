# models.py
# Ce fichier pourrait contenir des classes pour User et Article
# par exemple, pour valider les données ou gérer la persistance

from datetime import datetime

class User:
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'email': self.email}

class Article:
    def __init__(self, id, user_id, title, content, tags=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.content = content
        self.tags = tags if tags is not None else []
        self.created_at = created_at if created_at is not None else datetime.now()

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() # Utiliser ISO format par défaut
        }

# Pour l'instant, l'implémentation de `app.py` n'utilise pas ces classes directement.
# C'est une opportunité de refactoring !