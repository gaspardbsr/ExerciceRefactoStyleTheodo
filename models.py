# models.py
# Ce fichier pourrait contenir des classes pour User et Article
# par exemple, pour valider les données ou gérer la persistance

from datetime import datetime
from typing import Optional

class UserInfos:
    id: int
    name: str
    email: str

class User:
    def __init__(self, infos: UserInfos):
        self.id = infos.id
        self.name = infos.name
        self.email = infos.email

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'email': self.email}

class ArticleInfos:
    id: int
    user_id: int
    title: str
    content: str
    tags: Optional[list[str]] = None
    created_at: Optional[datetime] = datetime.now()

class Article:
    def __init__(self, infos: ArticleInfos):
        self.id = infos.id
        self.user_id = infos.user_id
        self.title = infos.title
        self.content = infos.content
        self.tags = infos.tags
        self.created_at = infos.created_at

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