from flask import Flask, render_template, request, redirect, session, url_for
from flask_mail import Mail, Message
import sqlite3
import os
from dotenv import load_dotenv
import threading
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET_KEY', 'dev-secret')

# Конфигурация почты
app.config.update(
    MAIL_SERVER=os.getenv('MAIL_SERVER'),
    MAIL_PORT=int(os.getenv('MAIL_PORT', 465)),
    MAIL_USE_SSL=os.getenv('MAIL_USE_SSL', 'True').lower() == 'true',
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD')
)

mail = Mail(app)


# Маршруты
@app.route('/')
def index():
    """Главная страница с формой"""
    app.logger.debug("Rendering index page")
    return render_template('lform.html')


@app.route('/ping')
def ping():
    """Проверка работоспособности"""
    return "Pong! Service is operational", 200


# Middleware для логирования
@app.after_request
def log_requests(response):
    app.logger.info(
        f"[{datetime.now()}] {request.remote_addr} {request.method} "
        f"{request.path} -> {response.status_code}"
    )
    return response


if __name__ == '__main__':
    # Создаем папку для шаблонов если её нет
    if not os.path.exists('templates'):
        os.makedirs('templates')

    # Запуск с подробным логгированием
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True,
        use_debugger=True
    )