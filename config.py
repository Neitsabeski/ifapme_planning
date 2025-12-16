# config.py

class Config:
    # Adresse IP sur laquelle Flask doit écouter
    HOST = "192.168.138.235"

    # Port d'écoute
    PORT = 5000

    # Mode debug (True = rechargement auto, logs détaillés)
    DEBUG = True

    # Clé secrète pour sessions/cookies
    SECRET_KEY = "change_me_en_production"

    # Exemple d'autres paramètres (base de données, etc.)
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # ⚠ reverse proxy !!!!