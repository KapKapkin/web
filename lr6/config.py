import os

SECRET_KEY = 'you-will-never-guess'

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///project.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'images')
MAX_CONTENT_LENGTH = 1 * 1024 * 1024
