import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(64))
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://mongodb:27017/')
    MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'scrapy')
    MONGODB_COLLECTION = os.getenv('MONGODB_COLLECTION', 'items')
