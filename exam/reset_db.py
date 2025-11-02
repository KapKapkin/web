#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для очистки и пересоздания базы данных
"""

import os
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'library1')

def reset_database():
    """Удаляет и создаёт заново базу данных"""
    try:
        # Подключаемся без указания базы данных
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Удаляем базу данных если существует
            print(f"Удаление базы данных '{DB_NAME}'...")
            cursor.execute(f"DROP DATABASE IF EXISTS `{DB_NAME}`")
            
            # Создаём базу данных заново
            print(f"Создание базы данных '{DB_NAME}'...")
            cursor.execute(f"CREATE DATABASE `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            
        connection.commit()
        connection.close()
        
        print(f"✓ База данных '{DB_NAME}' успешно пересоздана")
        print("\nТеперь запустите: python3 init_db.py")
        
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False
    
    return True

if __name__ == '__main__':
    print("=" * 50)
    print("ОЧИСТКА БАЗЫ ДАННЫХ")
    print("=" * 50)
    print(f"База данных: {DB_NAME}")
    print(f"Хост: {DB_HOST}")
    print(f"Пользователь: {DB_USER}")
    print("=" * 50)
    
    confirm = input("\nВНИМАНИЕ! Все данные будут удалены. Продолжить? (yes/no): ")
    
    if confirm.lower() in ['yes', 'y', 'да']:
        reset_database()
    else:
        print("Отменено")
