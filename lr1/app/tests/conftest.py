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

@pytest.fixture
def posts_list():
    return [
        {
            'title': 'Заголовок поста',
            'text': 'Текст поста для тестирования',
            'author': 'Иванов Иван Иванович',
            'date': datetime(2025, 3, 10, 14, 30),
            'image_id': '123.jpg',
            'comments': [
                {
                    'author': 'Петров Петр',
                    'text': 'Отличный пост!',
                    'replies': [
                        {
                            'author': 'Сидоров Сидор',
                            'text': 'Согласен!'
                        }
                    ]
                }
            ]
        }
    ]

@pytest.fixture
def posts_list_no_comments():
    return [
        {
            'title': 'Пост без комментариев',
            'text': 'Текст поста без комментариев',
            'author': 'Автор Тест',
            'date': datetime(2025, 1, 15, 10, 45),
            'image_id': 'test.jpg',
            'comments': []
        }
    ]
