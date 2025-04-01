from flask import Flask, render_template, request, redirect, session, url_for
from flask_mail import Mail, Message
import json
import sqlite3
import os
from dotenv import load_dotenv
import threading
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import random

# Загрузка переменных окружения
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET_KEY', 'default-secret-key')

# Конфигурация почты с исправлением SSL/TLS
app.config.update(
    MAIL_SERVER=os.getenv('MAIL_SERVER'),
    MAIL_PORT=int(os.getenv('MAIL_PORT', 465)),
    MAIL_USE_SSL=os.getenv('MAIL_USE_SSL', 'True').lower() == 'true',
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER')
)

mail = Mail(app)

# Проверка сервисного аккаунта Google
SERVICE_ACCOUNT_PATH = os.getenv('SERVICE_ACCOUNT_JSON')
if not SERVICE_ACCOUNT_PATH or not os.path.exists(SERVICE_ACCOUNT_PATH):
    raise FileNotFoundError(
        f"Service account file not found at: {SERVICE_ACCOUNT_PATH}. "
        "Check .env configuration.")

# Инициализация Google Calendar API с правильными scopes
try:
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_PATH,
        scopes=['https://www.googleapis.com/auth/calendar']
    )
    service = build('calendar', 'v3', credentials=credentials)
except Exception as e:
    print(f"Error initializing Google API: {str(e)}")
    service = None  # Обработать отсутствие сервиса в коде


# Функции для работы с базой данных
def create_database():
    with sqlite3.connect('leave_applications.db') as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS leave_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            leave_days TEXT,
            leave_period TEXT,
            reason TEXT,
            status TEXT DEFAULT 'pending'
        )""")

        c.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )""")

        # Добавление тестового пользователя если не существует
        try:
            c.execute(
                "INSERT OR IGNORE INTO users (email, password) VALUES (?, ?)",
                (os.getenv('DEFAULT_USER'), os.getenv('DEFAULT_USER_PASSWORD'))
            )
            conn.commit()
        except sqlite3.IntegrityError:
            pass


create_database()


def get_db():
    conn = sqlite3.connect('leave_applications.db')
    conn.row_factory = sqlite3.Row
    return conn


# ... (остальные функции работы с БД остаются без изменений, но стоит добавить обработку ошибок)

@app.context_processor
def inject_global_vars():
    return {
        'domain': os.getenv('Domain_OR_IP', 'localhost:5000'),
        'current_year': datetime.now().year
    }


def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Error sending email: {str(e)}")


# ... (остальные маршруты и функции с добавлением обработки ошибок)

if __name__ == '__main__':
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )