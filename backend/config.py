import os

DB_USER = "chess_user"
DB_PASSWORD = "JustAPassword"
DB_HOST = "localhost"
DB_NAME = "chess_db"

SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
