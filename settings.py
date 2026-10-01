import os

class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SECRET_KEY = os.getenv('SECRET_KEY')
    # Добавьте строчку для получения токена из переменных окружения.
    DROPBOX_TOKEN = os.getenv('DROPBOX_TOKEN')
