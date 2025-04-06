from flask import g
from pymongo import MongoClient
from config import Config

def get_db():
    if 'db' not in g:
        client = MongoClient(Config.MONGO_URI)
        g.db = client[Config.MONGO_DB_NAME]
    return g.db 