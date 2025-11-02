#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import hashlib
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import bleach
import markdown
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Database configuration
DATABASE_URL = f"mysql+pymysql://{os.environ.get('DB_USER', 'root')}:{os.environ.get('DB_PASSWORD', '')}@{os.environ.get('DB_HOST', 'localhost')}/{os.environ.get('DB_NAME', 'electronic_library')}?charset=utf8mb4"

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Association tables
book_genres = db.Table('book_genres',
    db.Column('book_id', db.Integer, db.ForeignKey('books.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)

collection_books = db.Table('collection_books',
    db.Column('collection_id', db.Integer, db.ForeignKey('collections.id'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('books.id'), primary_key=True)
)

# Models
class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    users = db.relationship('User', backref='role', lazy=True)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    
    reviews = db.relationship('Review', backref='user', lazy=True, cascade='all, delete-orphan')
    collections = db.relationship('Collection', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        name = f"{self.first_name} {self.last_name}"
        if self.middle_name:
            name += f" {self.middle_name}"
        return name

class Genre(db.Model):
    __tablename__ = 'genres'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class Cover(db.Model):
    __tablename__ = 'covers'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    md5_hash = db.Column(db.String(32), unique=True, nullable=False)
    
    books = db.relationship('Book', backref='cover', lazy=True)

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    publisher = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    cover_id = db.Column(db.Integer, db.ForeignKey('covers.id'), nullable=False)
    
    genres = db.relationship('Genre', secondary=book_genres, lazy='subquery',
                           backref=db.backref('books', lazy=True))
    reviews = db.relationship('Review', backref='book', lazy=True, cascade='all, delete-orphan')
    
    @property
    def average_rating(self):
        review_list = list(self.reviews)
        if not review_list:
            return None
        return sum(review.rating for review in review_list) / len(review_list)
    
    @property
    def review_count(self):
        return len(list(self.reviews))
    
    @property
    def genres_list(self):
        return ', '.join([genre.name for genre in list(self.genres)])

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('book_id', 'user_id', name='unique_user_book_review'),)

class Collection(db.Model):
    __tablename__ = 'collections'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    books = db.relationship('Book', secondary=collection_books, lazy='subquery',
                           backref=db.backref('collections', lazy=True))
    
    @property
    def book_count(self):
        return len(list(self.books))

# Helper functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Для выполнения данного действия необходимо пройти процедуру аутентификации')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Для выполнения данного действия необходимо пройти процедуру аутентификации')
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or user.role.name != 'администратор':
            flash('У вас недостаточно прав для выполнения данного действия')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def moderator_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Для выполнения данного действия необходимо пройти процедуру аутентификации')
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or user.role.name not in ['администратор', 'модератор']:
            flash('У вас недостаточно прав для выполнения данного действия')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def get_user_role():
    if 'user_id' not in session:
        return None
    
    user = User.query.get(session['user_id'])
    return user.role.name if user else None

def sanitize_html(text):
    allowed_tags = ['p', 'br', 'strong', 'b', 'em', 'i', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                   'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'img']
    allowed_attributes = {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title']
    }
    return bleach.clean(text, tags=allowed_tags, attributes=allowed_attributes)

# Routes
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    books_pagination = Book.query.order_by(Book.year.desc(), Book.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    books = books_pagination.items
    
    return render_template('index.html', 
                         books=books, 
                         page=page, 
                         total_pages=books_pagination.pages,
                         user_role=get_user_role())

@app.route('/cover/<int:cover_id>')
def serve_cover(cover_id):
    """Отдает файл обложки по ID"""
    cover = Cover.query.get_or_404(cover_id)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], cover.filename)
    
    if os.path.exists(file_path):
        return send_file(file_path, mimetype=cover.mime_type)
    else:
        # Возвращаем заглушку, если файл не найден
        abort(404)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = 'remember' in request.form
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.full_name
            
            if remember:
                session.permanent = True
            
            return redirect(url_for('index'))
        else:
            flash('Невозможно аутентифицироваться с указанными логином и паролем')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    
    reviews = Review.query.filter_by(book_id=book_id).order_by(Review.created_at.desc()).all()
    
    user_review = None
    if 'user_id' in session:
        user_review = Review.query.filter_by(book_id=book_id, user_id=session['user_id']).first()
    
    book_description_html = markdown.markdown(book.description) if book.description else ''
    
    return render_template('book_detail.html', 
                         book=book, 
                         book_description_html=book_description_html,
                         reviews=reviews,
                         user_review=user_review,
                         user_role=get_user_role())

@app.route('/book/add', methods=['GET', 'POST'])
@admin_required
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        year = request.form['year']
        author = request.form['author']
        publisher = request.form['publisher']
        pages = request.form['pages']
        genre_ids = request.form.getlist('genres')
        cover_file = request.files['cover']
        
        description = sanitize_html(description)
        
        if not cover_file or cover_file.filename == '':
            flash('Необходимо загрузить обложку книги')
            return render_template('book_form.html', 
                                 book=None, 
                                 genres=Genre.query.all(), 
                                 form_data=request.form)
        
        if not allowed_file(cover_file.filename):
            flash('Недопустимый формат файла обложки')
            return render_template('book_form.html', 
                                 book=None, 
                                 genres=Genre.query.all(), 
                                 form_data=request.form)
        
        try:
            cover_data = cover_file.read()
            cover_hash = hashlib.md5(cover_data).hexdigest()
            
            existing_cover = Cover.query.filter_by(md5_hash=cover_hash).first()
            
            if existing_cover:
                cover = existing_cover
            else:
                if cover_file.filename:
                    filename = secure_filename(cover_file.filename)
                    mime_type = cover_file.content_type or 'image/jpeg'
                    
                    cover = Cover(
                        filename=filename,
                        mime_type=mime_type,
                        md5_hash=cover_hash
                    )
                    db.session.add(cover)
                    db.session.flush()
                    
                    file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
                    new_filename = f"{cover.id}.{file_extension}"
                    cover.filename = new_filename
                    
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                    print(f"Saving cover to: {file_path}")  # Debug
                    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")  # Debug
                    print(f"File exists after save: {os.path.exists(file_path)}")  # Debug
                    
                    with open(file_path, 'wb') as f:
                        f.write(cover_data)
                    
                    print(f"File saved, size: {os.path.getsize(file_path)} bytes")  # Debug
                    print(f"File still exists: {os.path.exists(file_path)}")  # Debug
                    print(f"Files in folder: {os.listdir(app.config['UPLOAD_FOLDER'])}")  # Debug
            
            book = Book(
                title=title,
                description=description,
                year=int(year),
                author=author,
                publisher=publisher,
                pages=int(pages),
                cover_id=cover.id
            )
            
            db.session.add(book)  # Сначала добавляем книгу в сессию
            
            # Потом добавляем жанры
            for genre_id in genre_ids:
                genre = Genre.query.get(int(genre_id))
                if genre:
                    book.genres.append(genre)
            print(f"Before commit - file exists: {os.path.exists(file_path)}")  # Debug
            db.session.commit()
            print(f"After commit - file exists: {os.path.exists(file_path)}")  # Debug
            print(f"After commit - files: {os.listdir(app.config['UPLOAD_FOLDER'])}")  # Debug
            
            flash('Книга успешно добавлена')
            return redirect(url_for('book_detail', book_id=book.id))
            
        except Exception as e:
            db.session.rollback()
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.')
            return render_template('book_form.html', 
                                 book=None, 
                                 genres=Genre.query.all(), 
                                 form_data=request.form)
    
    return render_template('book_form.html', book=None, genres=Genre.query.all())

@app.route('/book/<int:book_id>/edit', methods=['GET', 'POST'])
@moderator_or_admin_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        year = request.form['year']
        author = request.form['author']
        publisher = request.form['publisher']
        pages = request.form['pages']
        genre_ids = request.form.getlist('genres')
        cover_file = request.files.get('cover')
        
        description = sanitize_html(description)
        
        try:
            book.title = title
            book.description = description
            book.year = int(year)
            book.author = author
            book.publisher = publisher
            book.pages = int(pages)
            
            # Обработка новой обложки, если загружена
            if cover_file and cover_file.filename != '':
                if not allowed_file(cover_file.filename):
                    flash('Недопустимый формат файла обложки')
                    return render_template('book_form.html', 
                                         book=book, 
                                         current_genres=[genre.id for genre in book.genres],
                                         genres=Genre.query.all())
                
                # Читаем файл и вычисляем хеш
                cover_data = cover_file.read()
                cover_hash = hashlib.md5(cover_data).hexdigest()
                
                # Проверяем, существует ли уже такая обложка
                existing_cover = Cover.query.filter_by(md5_hash=cover_hash).first()
                
                if existing_cover:
                    # Используем существующую обложку
                    old_cover_id = book.cover_id
                    book.cover_id = existing_cover.id
                    
                    # Удаляем старую обложку, если она не используется другими книгами
                    if old_cover_id:
                        old_cover = Cover.query.get(old_cover_id)
                        if old_cover and Book.query.filter_by(cover_id=old_cover_id).count() == 0:
                            old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], old_cover.filename)
                            if os.path.exists(old_file_path):
                                os.remove(old_file_path)
                            db.session.delete(old_cover)
                else:
                    # Создаем новую обложку
                    filename = secure_filename(cover_file.filename)
                    mime_type = cover_file.content_type or 'image/jpeg'
                    
                    new_cover = Cover()
                    new_cover.filename = filename
                    new_cover.mime_type = mime_type
                    new_cover.md5_hash = cover_hash
                    db.session.add(new_cover)
                    db.session.flush()
                    
                    # Сохраняем файл с ID в имени
                    file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
                    new_filename = f"{new_cover.id}.{file_extension}"
                    new_cover.filename = new_filename
                    
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                    with open(file_path, 'wb') as f:
                        f.write(cover_data)
                    
                    # Удаляем старую обложку
                    old_cover_id = book.cover_id
                    book.cover_id = new_cover.id
                    
                    if old_cover_id:
                        old_cover = Cover.query.get(old_cover_id)
                        if old_cover and Book.query.filter_by(cover_id=old_cover_id).count() == 0:
                            old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], old_cover.filename)
                            if os.path.exists(old_file_path):
                                os.remove(old_file_path)
                            db.session.delete(old_cover)
            
            book.genres.clear()
            for genre_id in genre_ids:
                genre = Genre.query.get(int(genre_id))
                if genre:
                    book.genres.append(genre)
            
            db.session.commit()
            
            flash('Книга успешно обновлена')
            return redirect(url_for('book_detail', book_id=book_id))
            
        except Exception as e:
            db.session.rollback()
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.')
    
    current_genres = [genre.id for genre in list(book.genres)]
    
    return render_template('book_form.html', 
                         book=book, 
                         current_genres=current_genres,
                         genres=Genre.query.all())

@app.route('/book/<int:book_id>/delete', methods=['POST'])
@admin_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    try:
        cover_filename = book.cover.filename if book.cover else None
        
        db.session.delete(book)
        db.session.commit()
        
        if cover_filename:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], cover_filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        flash('Книга успешно удалена')
        
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении книги')
    
    return redirect(url_for('index'))

@app.route('/book/<int:book_id>/review', methods=['GET', 'POST'])
@login_required
def add_review(book_id):
    book = Book.query.get_or_404(book_id)
    
    existing_review = Review.query.filter_by(book_id=book_id, user_id=session['user_id']).first()
    if existing_review:
        flash('Вы уже оставляли рецензию на эту книгу')
        return redirect(url_for('book_detail', book_id=book_id))
    
    if request.method == 'POST':
        rating = request.form['rating']
        text = request.form['text']
        
        text = sanitize_html(text)
        
        try:
            review = Review(
                book_id=book_id,
                user_id=session['user_id'],
                rating=int(rating),
                text=text
            )
            
            db.session.add(review)
            db.session.commit()
            
            flash('Рецензия успешно добавлена')
            return redirect(url_for('book_detail', book_id=book_id))
            
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при сохранении рецензии')
    
    return render_template('review_form.html', book_title=book.title, book_id=book_id)

# Collection routes
@app.route('/collections')
@login_required
def my_collections():
    user = User.query.get(session['user_id'])
    if not user or user.role.name != 'пользователь':
        flash('Доступ запрещен')
        return redirect(url_for('index'))
    
    collections = Collection.query.filter_by(user_id=session['user_id']).order_by(Collection.created_at.desc()).all()
    
    return render_template('collections.html', collections=collections, user_role=get_user_role())

@app.route('/collections/add', methods=['POST'])
@login_required
def add_collection():
    user = User.query.get(session['user_id'])
    if not user or user.role.name != 'пользователь':
        flash('Доступ запрещен')
        return redirect(url_for('index'))
    
    name = request.form.get('name', '').strip()
    
    if not name:
        flash('Название подборки не может быть пустым')
        return redirect(url_for('my_collections'))
    
    try:
        collection = Collection(
            name=name,
            user_id=session['user_id']
        )
        
        db.session.add(collection)
        db.session.commit()
        
        flash('Подборка успешно создана')
        
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при создании подборки')
    
    return redirect(url_for('my_collections'))

@app.route('/collections/<int:collection_id>')
@login_required
def collection_detail(collection_id):
    collection = Collection.query.get_or_404(collection_id)
    
    if collection.user_id != session['user_id']:
        flash('Доступ запрещен')
        return redirect(url_for('my_collections'))
    
    return render_template('collection_detail.html', collection=collection, user_role=get_user_role())

@app.route('/book/<int:book_id>/add_to_collection', methods=['POST'])
@login_required
def add_book_to_collection(book_id):
    user = User.query.get(session['user_id'])
    if not user or user.role.name != 'пользователь':
        flash('Доступ запрещен')
        return redirect(url_for('book_detail', book_id=book_id))
    
    book = Book.query.get_or_404(book_id)
    collection_id = request.form.get('collection_id')
    
    if not collection_id:
        flash('Выберите подборку')
        return redirect(url_for('book_detail', book_id=book_id))
    
    collection = Collection.query.get(collection_id)
    
    if not collection or collection.user_id != session['user_id']:
        flash('Подборка не найдена')
        return redirect(url_for('book_detail', book_id=book_id))
    
    try:
        collection_books_list = list(collection.books)
        if book not in collection_books_list:
            collection.books.append(book)
            db.session.commit()
            flash(f'Книга добавлена в подборку "{collection.name}"')
        else:
            flash('Книга уже находится в этой подборке')
            
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при добавлении книги в подборку')
    
    return redirect(url_for('book_detail', book_id=book_id))

@app.route('/collections/<int:collection_id>/remove_book/<int:book_id>', methods=['POST'])
@login_required
def remove_book_from_collection(collection_id, book_id):
    collection = Collection.query.get_or_404(collection_id)
    
    if collection.user_id != session['user_id']:
        flash('Доступ запрещен')
        return redirect(url_for('my_collections'))
    
    book = Book.query.get_or_404(book_id)
    
    try:
        collection_books_list = list(collection.books)
        if book in collection_books_list:
            collection.books.remove(book)
            db.session.commit()
            flash('Книга удалена из подборки')
        else:
            flash('Книга не найдена в подборке')
            
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении книги из подборки')
    
    return redirect(url_for('collection_detail', collection_id=collection_id))

@app.route('/api/user_collections')
@login_required
def api_user_collections():
    user = User.query.get(session['user_id'])
    if not user or user.role.name != 'пользователь':
        return {'error': 'Access denied'}, 403
    
    collections = Collection.query.filter_by(user_id=session['user_id']).all()
    
    return jsonify([
        {
            'id': c.id,
            'name': c.name,
            'book_count': c.book_count
        }
        for c in collections
    ])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)