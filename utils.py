# utils.py
import re
from datetime import datetime

def is_valid_email(email):
    """Valide le format d'une adresse email."""
    # Une regex plus robuste pourrait être utilisée
    return re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email)

def format_datetime_for_display(dt_obj):
    """Formate un objet datetime en chaîne de caractères lisible."""
    if isinstance(dt_obj, datetime):
        return dt_obj.strftime("%Y-%m-%d %H:%M:%S")
    return str(dt_obj) # Gérer les cas où ce n'est pas un datetime object

# D'autres fonctions utilitaires (validation de données, etc.) pourraient aller ici.