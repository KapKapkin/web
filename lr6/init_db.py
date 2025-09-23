
"""
Скрипт для инициализации базы данных и заполнения её тестовыми данными
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Category, User, Course, Image, Review

def init_database():
    print("Создание таблиц...")
    db.create_all()
    print("Таблицы созданы!")

def populate_categories():
    categories_data = [
        'Программирование',
        'Математика', 
        'Языкознание',
        'Физика',
        'Химия',
        'История'
    ]
    
    categories = []
    for cat_name in categories_data:
        category = Category(name=cat_name)
        db.session.add(category)
        categories.append(category)
        db.session.flush() 
    
    db.session.commit()
    print(f"Добавлено {len(categories)} категорий")
    return categories

def populate_users():
    users_data = [
        {'first_name': 'Иван', 'last_name': 'Иванов', 'login': 'ivan', 'password': 'qwerty'},
        {'first_name': 'Петр', 'last_name': 'Петров', 'login': 'petr', 'password': 'qwerty'},
        {'first_name': 'Анна', 'last_name': 'Сидорова', 'login': 'anna', 'password': 'qwerty'},
        {'first_name': 'Олег', 'last_name': 'Худяков', 'login': 'oleg', 'password': 'qwerty'},
        {'first_name': 'Мария', 'last_name': 'Смирнова', 'login': 'maria', 'password': 'qwerty'},
    ]
    
    users = []
    for user_data in users_data:
        user = User(
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            login=user_data['login']
        )
        user.set_password(user_data['password'])
        db.session.add(user)
        users.append(user)
    
    db.session.commit()
    print(f"Добавлено {len(users)} пользователей")
    return users

def populate_courses(categories, users):
    courses_data = [
        {
            'name': 'Основы Python',
            'short_desc': 'Изучите основы программирования на Python',
            'full_desc': 'Полный курс по изучению языка программирования Python с нуля. Курс включает в себя изучение синтаксиса, основных структур данных, объектно-ориентированного программирования и многое другое.',
            'category_id': 1,  
            'author_id': 1,   
        },
        {
            'name': 'Веб-разработка с Flask',
            'short_desc': 'Создание веб-приложений на Flask',
            'full_desc': 'Изучите создание веб-приложений с использованием микрофреймворка Flask. Курс покрывает маршрутизацию, шаблоны, работу с базами данных и деплой приложений.',
            'category_id': 1,  
            'author_id': 2,    
        },
        {
            'name': 'Математический анализ',
            'short_desc': 'Основы математического анализа',
            'full_desc': 'Курс по математическому анализу, включающий изучение пределов, производных, интегралов и их применений в решении практических задач.',
            'category_id': 2,  
            'author_id': 3,    
        },
        {
            'name': 'Английский язык для IT',
            'short_desc': 'Английский язык для программистов',
            'full_desc': 'Специализированный курс английского языка для IT-специалистов. Изучение технической терминологии, написание документации и общение в международных командах.',
            'category_id': 3, 
            'author_id': 4,   
        },
    ]
    
    courses = []
    for course_data in courses_data:
        course = Course(
            name=course_data['name'],
            short_desc=course_data['short_desc'],
            full_desc=course_data['full_desc'],
            category_id=course_data['category_id'],
            author_id=course_data['author_id'],
            rating_sum=0,
            rating_num=0
        )
        db.session.add(course)
        courses.append(course)
    
    db.session.commit()
    print(f"Добавлено {len(courses)} курсов")
    return courses

def populate_reviews(courses, users):
    reviews_data = [
        {
            'course_id': 1,
            'user_id': 2,  
            'rating': 5,
            'text': 'Отличный курс! Все объяснено очень понятно и доступно. Рекомендую всем начинающим разработчикам.'
        },
        {
            'course_id': 1,
            'user_id': 3, 
            'rating': 4,
            'text': 'Хороший курс, но хотелось бы больше практических заданий.'
        },
        {
            'course_id': 1,
            'user_id': 5, 
            'rating': 5,
            'text': 'Превосходный курс! Автор очень хорошо объясняет сложные концепции.'
        },
        
   
        {
            'course_id': 2,
            'user_id': 1, 
            'rating': 4,
            'text': 'Интересный курс, но некоторые моменты могли бы быть объяснены лучше.'
        },
        {
            'course_id': 2,
            'user_id': 3,  
            'rating': 5,
            'text': 'Отличный практический курс! Теперь могу создавать свои веб-приложения.'
        },
        
       
        {
            'course_id': 3,
            'user_id': 1, 
            'rating': 3,
            'text': 'Курс неплохой, но довольно сложный для восприятия.'
        },
        {
            'course_id': 3,
            'user_id': 4, 
            'rating': 4,
            'text': 'Хороший академический курс с качественной подачей материала.'
        },
        

        {
            'course_id': 4,
            'user_id': 2, 
            'rating': 5,
            'text': 'Именно то, что нужно для работы в IT! Очень полезная лексика и фразы.'
        },
        {
            'course_id': 4,
            'user_id': 5,
            'rating': 4,
            'text': 'Хороший курс, помог улучшить технический английский.'
        },
    ]
    
    reviews = []
    for review_data in reviews_data:
        review = Review(
            course_id=review_data['course_id'],
            user_id=review_data['user_id'],
            rating=review_data['rating'],
            text=review_data['text']
        )
        db.session.add(review)
        reviews.append(review)
        
        course = courses[review_data['course_id'] - 1]
        course.rating_sum += review_data['rating']
        course.rating_num += 1
    
    db.session.commit()
    print(f"Добавлено {len(reviews)} отзывов")
    return reviews

def main():
    """Основная функция"""
    app = create_app()
    
    with app.app_context():
        print("Инициализация базы данных...")
        
        db.drop_all()
        init_database()
        
        categories = populate_categories()
        users = populate_users()
        courses = populate_courses(categories, users)
        reviews = populate_reviews(courses, users)
        
        print("\nБаза данных успешно инициализирована!")
        print(f"Создано:")
        print(f"  - Категорий: {len(categories)}")
        print(f"  - Пользователей: {len(users)}")
        print(f"  - Курсов: {len(courses)}")
        print(f"  - Отзывов: {len(reviews)}")
        
        print("\nДанные для входа:")
        print("Логин: ivan, Пароль: qwerty")
        print("Логин: petr, Пароль: qwerty")
        print("Логин: anna, Пароль: qwerty")
        print("Логин: oleg, Пароль: qwerty")
        print("Логин: maria, Пароль: qwerty")

if __name__ == '__main__':
    main()