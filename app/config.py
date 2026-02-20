import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = "ranjbarcoin-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "db.sqlite3")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
