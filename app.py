from flask import Flask, request, jsonify
from datetime import datetime
import re

app = Flask(__name__)

# Base de données "in-memory" pour simplifier
users_db = {}  # {user_id: {id, name, email}}
articles_db = {} # {article_id: {id, user_id, title, content, tags, created_at}}

# --- Fonctions utilitaires "inline" ou mal placées ---
def validate_email(email):
    # Regex simple pour la validation d'email
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def format_date_display(dt_obj):
    return dt_obj.strftime("%Y-%m-%d %H:%M:%S")

# --- Routes Utilisateurs ---
@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    name = data.get('name')
    email = data.get('email')

    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400

    if not validate_email(email):
        return jsonify({"error": "Invalid email format"}), 400
    
    for user_id in users_db:
        if users_db[user_id]['email'] == email:
            return jsonify({"error": "User with this email already exists"}), 409

    user_id = len(users_db) + 1
    new_user = {'id': user_id, 'name': name, 'email': email}
    users_db[user_id] = new_user
    return jsonify(new_user), 201

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(list(users_db.values())), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = users_db.get(user_id)
    if user:
        return jsonify(user), 200
    return jsonify({"error": "User not found"}), 404

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = users_db.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.json
    new_name = data.get('name')
    new_email = data.get('email')

    if new_name:
        user['name'] = new_name
    if new_email:
        if not validate_email(new_email):
            return jsonify({"error": "Invalid email format"}), 400
        
        # Vérifier si l'email existe déjà pour un autre utilisateur
        for existing_user_id in users_db:
            if existing_user_id != user_id and users_db[existing_user_id]['email'] == new_email:
                return jsonify({"error": "User with this email already exists"}), 409
        
        user['email'] = new_email
        
    return jsonify(user), 200

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if user_id in users_db:
        del users_db[user_id]
        # Supprimer aussi les articles de cet utilisateur (logique métier dans le contrôleur)
        articles_to_delete = [art_id for art_id, art in articles_db.items() if art['user_id'] == user_id]
        for art_id in articles_to_delete:
            del articles_db[art_id]
        return jsonify({"message": "User and associated articles deleted"}), 204
    return jsonify({"error": "User not found"}), 404

# --- Routes Articles ---
@app.route('/articles', methods=['POST'])
def create_article():
    data = request.json
    user_id = data.get('user_id')
    title = data.get('title')
    content = data.get('content')
    tags_str = data.get('tags', '') # Tags sous forme de chaîne "tag1,tag2"

    if not user_id or not title or not content:
        return jsonify({"error": "user_id, title, and content are required"}), 400

    if user_id not in users_db:
        return jsonify({"error": "User not found"}), 404
    
    tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()] if tags_str else []

    article_id = len(articles_db) + 1
    new_article = {
        'id': article_id,
        'user_id': user_id,
        'title': title,
        'content': content,
        'tags': tags,
        'created_at': datetime.now() # Date de création
    }
    articles_db[article_id] = new_article
    
    # Formatage de la date pour la réponse (mélange de responsabilités)
    response_article = new_article.copy()
    response_article['created_at'] = format_date_display(new_article['created_at'])
    
    return jsonify(response_article), 201

@app.route('/articles', methods=['GET'])
def get_articles():
    # Logique de filtrage d'articles (par date, par tag)
    filtered_articles = list(articles_db.values())

    tag_filter = request.args.get('tag')
    date_after_str = request.args.get('date_after') # Format YYYY-MM-DD

    if tag_filter:
        filtered_articles = [
            article for article in filtered_articles if tag_filter in article['tags']
        ]

    if date_after_str:
        try:
            date_after = datetime.strptime(date_after_str, "%Y-%m-%d")
            filtered_articles = [
                article for article in filtered_articles if article['created_at'] >= date_after
            ]
        except ValueError:
            return jsonify({"error": "Invalid date_after format. Use YYYY-MM-DD"}), 400

    # Formatage des dates pour chaque article (responsabilité répétée)
    articles_for_response = []
    for article in filtered_articles:
        art_copy = article.copy()
        art_copy['created_at'] = format_date_display(article['created_at'])
        articles_for_response.append(art_copy)

    return jsonify(articles_for_response), 200

@app.route('/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    article = articles_db.get(article_id)
    if article:
        # Formatage de la date (responsabilité du contrôleur)
        response_article = article.copy()
        response_article['created_at'] = format_date_display(article['created_at'])
        return jsonify(response_article), 200
    return jsonify({"error": "Article not found"}), 404

# Point d'entrée pour lancer l'application
if __name__ == '__main__':
    app.run(debug=True)