from datetime import datetime
import pytest
from flask import template_rendered
from contextlib import contextmanager
from app import app as application

@pytest.fixture
def app():
    return application

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
@contextmanager
def captured_templates(app):
    recorded = []
    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)

POST_LIST = [
        {
            'title': 'Заголовок поста',
            'text': 'Текст поста',
            'author': 'Иванов Иван Иванович',
            'date': datetime(2025, 3, 10, 17, 11, 22),
            'image_id': '123.jpg',
            'comments': [{"author": "Oleg Khudykov", "text": "Норм пост такой"}]
        }
    ]

@pytest.fixture
def posts_list():
    return POST_LIST

@pytest.fixture(autouse=True)
def mock_posts_list(mocker):
    mock = mocker.patch("app.posts_list", autospec=True, return_value=POST_LIST)
    return mock