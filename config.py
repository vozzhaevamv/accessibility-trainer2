import os
import secrets

# Генерация секретного ключа
secret_key = secrets.token_hex(32)

class Config:
    basedir = os.path.abspath(os.path.dirname(__file__))
    # Путь к папке instance
    INSTANCE_PATH = os.path.join(basedir, 'instance')
    
    # Гарантируем существование папки
    os.makedirs(INSTANCE_PATH, exist_ok=True)
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(INSTANCE_PATH, 'site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = secret_key
    
    # Настройки почты
    MAIL_SERVER = 'smtp.yandex.ru'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'ваш@yandex.ru'
    MAIL_PASSWORD = 'пароль_от_почты'