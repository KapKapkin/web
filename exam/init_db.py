#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import hashlib
from app import app, db, Role, User, Genre, Book, Cover

def init_database():
    """Initialize database with tables and default data"""
    
    with app.app_context():
        # Create all tables
        print("Создание таблиц базы данных...")
        db.create_all()
        
        # Check if roles already exist
        if Role.query.count() == 0:
            print("Создание ролей...")
            
            # Create roles
            admin_role = Role(
                name='администратор',
                description='Полный доступ ко всем функциям системы'
            )
            
            moderator_role = Role(
                name='модератор',
                description='Может редактировать книги и управлять контентом'
            )
            
            user_role = Role(
                name='пользователь',
                description='Может просматривать книги, оставлять рецензии и создавать подборки'
            )
            
            db.session.add(admin_role)
            db.session.add(moderator_role)
            db.session.add(user_role)
            db.session.commit()
            
            print("Роли созданы успешно")
        else:
            print("Роли уже существуют")
        
        # Check if users already exist
        if User.query.count() == 0:
            print("Создание пользователей по умолчанию...")
            
            # Get roles
            admin_role = Role.query.filter_by(name='администратор').first()
            moderator_role = Role.query.filter_by(name='модератор').first()
            user_role = Role.query.filter_by(name='пользователь').first()
            
            # Create default admin user
            admin_user = User(
                username='admin',
                first_name='Администратор',
                last_name='Системы',
                role_id=admin_role.id
            )
            admin_user.set_password('admin123')
            
            # Create default moderator
            moderator_user = User(
                username='moderator',
                first_name='Модератор',
                last_name='Контента',
                role_id=moderator_role.id
            )
            moderator_user.set_password('moderator123')
            
            # Create default user
            regular_user = User(
                username='user',
                first_name='Обычный',
                last_name='Пользователь',
                role_id=user_role.id
            )
            regular_user.set_password('user123')
            
            # Create test user
            test_user = User(
                username='reader',
                first_name='Читатель',
                last_name='Книг',
                middle_name='Любитель',
                role_id=user_role.id
            )
            test_user.set_password('reader123')
            
            db.session.add(admin_user)
            db.session.add(moderator_user)
            db.session.add(regular_user)
            db.session.add(test_user)
            db.session.commit()
            
            print("Пользователи созданы успешно")
            print("Администратор: admin / admin123")
            print("Модератор: moderator / moderator123")
            print("Пользователь: user / user123")
            print("Читатель: reader / reader123")
        else:
            print("Пользователи уже существуют")
        
        # Check if genres already exist
        if Genre.query.count() == 0:
            print("Создание жанров...")
            
            genres = [
                'Художественная литература',
                'Детективы',
                'Фантастика',
                'Фэнтези',
                'Романы',
                'Классическая литература',
                'Современная проза',
                'Поэзия',
                'Драматургия',
                'Научная фантастика',
                'Боевики',
                'Триллеры',
                'Ужасы',
                'Приключения',
                'Исторические романы',
                'Любовные романы',
                'Молодежная литература',
                'Детская литература',
                'Биографии',
                'Мемуары',
                'Научно-популярная литература',
                'Техническая литература',
                'Справочники',
                'Энциклопедии',
                'Учебная литература',
                'Философия',
                'Психология',
                'Социология',
                'История',
                'Политика',
                'Экономика',
                'Юриспруденция',
                'Медицина',
                'Естественные науки',
                'Точные науки',
                'Информационные технологии',
                'Искусство',
                'Культура',
                'Религия',
                'Эзотерика'
            ]
            
            for genre_name in genres:
                genre = Genre(name=genre_name)
                db.session.add(genre)
            
            db.session.commit()
            print(f"Создано {len(genres)} жанров")
        else:
            print("Жанры уже существуют")
        
        # Добавляем примеры книг
        if Book.query.count() == 0:
            print("Добавление примеров книг...")
            
            # Получаем жанры
            genre_fiction = Genre.query.filter_by(name='Художественная литература').first()
            genre_fantasy = Genre.query.filter_by(name='Фантастика').first()
            genre_detective = Genre.query.filter_by(name='Детектив').first()
            genre_classic = Genre.query.filter_by(name='Классика').first()
            genre_scifi = Genre.query.filter_by(name='Научная фантастика').first()
            genre_adventure = Genre.query.filter_by(name='Приключения').first()
            
            sample_books = [
                {
                    'title': 'Мастер и Маргарита',
                    'author': 'Михаил Булгаков',
                    'publisher': 'АСТ',
                    'year': 2020,
                    'pages': 480,
                    'description': 'Роман, сочетающий в себе философскую притчу, любовную лирику и сатиру. История о дьяволе, посетившем Москву 1930-х годов, и трагической любви Мастера и Маргариты.',
                    'genres': [genre_classic, genre_fiction]
                },
                {
                    'title': 'Война и мир',
                    'author': 'Лев Толстой',
                    'publisher': 'Эксмо',
                    'year': 2019,
                    'pages': 1300,
                    'description': 'Монументальное произведение о русском обществе в эпоху войн против Наполеона. История судеб аристократических семей на фоне исторических событий.',
                    'genres': [genre_classic, genre_fiction]
                },
                {
                    'title': 'Преступление и наказание',
                    'author': 'Федор Достоевский',
                    'publisher': 'Азбука',
                    'year': 2021,
                    'pages': 608,
                    'description': 'Психологический роман о бедном студенте Раскольникове, совершившем убийство. Исследование моральных границ и человеческой природы.',
                    'genres': [genre_classic, genre_detective]
                },
                {
                    'title': 'Гарри Поттер и философский камень',
                    'author': 'Джоан Роулинг',
                    'publisher': 'Махаон',
                    'year': 2020,
                    'pages': 432,
                    'description': 'Первая книга о юном волшебнике Гарри Поттере, открывающем для себя мир магии в школе чародейства и волшебства Хогвартс.',
                    'genres': [genre_fantasy, genre_adventure]
                },
                {
                    'title': '1984',
                    'author': 'Джордж Оруэлл',
                    'publisher': 'АСТ',
                    'year': 2021,
                    'pages': 320,
                    'description': 'Антиутопия о тоталитарном обществе будущего, где правительство контролирует каждый аспект жизни граждан.',
                    'genres': [genre_scifi, genre_fiction]
                },
                {
                    'title': 'Убийство в «Восточном экспрессе»',
                    'author': 'Агата Кристи',
                    'publisher': 'Эксмо',
                    'year': 2020,
                    'pages': 256,
                    'description': 'Классический детектив с участием знаменитого сыщика Эркюля Пуаро. Расследование убийства в поезде, застрявшем в снегах.',
                    'genres': [genre_detective, genre_fiction]
                },
                {
                    'title': 'Солярис',
                    'author': 'Станислав Лем',
                    'publisher': 'АСТ',
                    'year': 2019,
                    'pages': 224,
                    'description': 'Философская научная фантастика о контакте человечества с внеземным разумом на планете-океане Солярис.',
                    'genres': [genre_scifi]
                },
                {
                    'title': 'Анна Каренина',
                    'author': 'Лев Толстой',
                    'publisher': 'Эксмо',
                    'year': 2020,
                    'pages': 864,
                    'description': 'История трагической любви замужней женщины к офицеру. Роман о морали, семье и обществе XIX века.',
                    'genres': [genre_classic, genre_fiction]
                },
            ]
            
            for book_data in sample_books:
                # Создаем обложку (используем дефолтную заглушку)
                # В реальной работе обложки загружаются через веб-интерфейс
                cover = Cover()
                cover.filename = 'default_cover.jpg'
                cover.mime_type = 'image/jpeg'
                # Генерируем уникальный MD5 хеш из названия книги
                cover.md5_hash = hashlib.md5(book_data["title"].encode()).hexdigest()
                db.session.add(cover)
                db.session.flush()  # Получаем ID обложки
                
                # Создаем книгу
                book = Book()
                book.title = book_data['title']
                book.author = book_data['author']
                book.publisher = book_data['publisher']
                book.year = book_data['year']
                book.pages = book_data['pages']
                book.description = book_data['description']
                book.cover_id = cover.id
                
                # Добавляем жанры
                for genre in book_data['genres']:
                    if genre:
                        book.genres.append(genre)
                
                db.session.add(book)
            
            db.session.commit()
            print(f"Добавлено {len(sample_books)} примеров книг")
        else:
            print("Книги уже существуют")
        
        print("Инициализация базы данных завершена успешно!")

if __name__ == '__main__':
    init_database()