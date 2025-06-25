import os
import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Инициализация расширений
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    # Создание экземпляра приложения
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object('config.Config')

    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    
    # Настройка входа
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'
    login_manager.login_message_category = 'warning'
    
    # Загрузчик пользователя
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))
    
    # Регистрация Blueprint
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    # Создание БД и начальных данных
    with app.app_context():
        db.create_all()
        initialize_data()
        print("База данных инициализирована")
    
    return app

def initialize_data():
    from .models import Task, QuizQuestion, UserProgress, UserMetric, User
    
    # Если таблица пуста, добавляем начальные данные
    if Task.query.count() == 0:
        tasks = [
            Task(
                title="Семантическая разметка",
                description="Используйте правильные HTML-теги",
                question="Замените div на подходящий семантический тег",
                code_snippet='<div id="header">Заголовок сайта</div>',
                correct_answer="<header>Заголовок сайта</header>",
                difficulty="easy",
                task_type="code"
            ),
            Task(
                title="ARIA-роли",
                description="Добавьте ARIA-роли для элементов",
                question="Добавьте правильную ARIA-роль к меню навигации.",
                code_snippet='<div><a href="/">Главная</a><a href="/about">О сайте</a></div>',
                correct_answer="role='navigation'",
                difficulty="medium",
                task_type="code"
            ),
            Task(
                title="Тест по основам доступности",
                description="Проверьте свои знания принципов доступности",
                question="Выберите правильные утверждения",
                code_snippet="",
                correct_answer="",
                difficulty="easy",
                task_type="quiz"
            )
        ]
        db.session.add_all(tasks)
        db.session.commit()
        
        # Вопросы для теста
        quiz_task = Task.query.filter_by(title="Тест по основам доступности").first()
        
        quiz_questions = [
            QuizQuestion(
                question="Что из перечисленного является принципом WCAG?",
                options=json.dumps({
                    "A": "Воспринимаемость",
                    "B": "Скорость загрузки",
                    "C": "Красивый дизайн",
                    "D": "Сложная анимация"
                }),
                correct_answer="A",
                task_id=quiz_task.id
            ),
            QuizQuestion(
                question="Какой атрибут используется для описания назначения элемента?",
                options=json.dumps({
                    "A": "aria-label",
                    "B": "aria-describedby",
                    "C": "role",
                    "D": "tabindex"
                }),
                correct_answer="A",
                task_id=quiz_task.id
            ),
            QuizQuestion(
                question="Какой тег следует использовать для основной навигации?",
                options=json.dumps({
                    "A": "<div>",
                    "B": "<span>",
                    "C": "<nav>",
                    "D": "<menu>"
                }),
                correct_answer="C",
                task_id=quiz_task.id
            )
        ]
        db.session.add_all(quiz_questions)
        db.session.commit()
        
        print("Добавлены начальные данные")
    
    # Создаем тестового пользователя, если его нет
    if User.query.count() == 0:
        test_user = User(username="test", email="test@example.com")
        test_user.set_password("password")
        db.session.add(test_user)
        db.session.commit()
        print("Создан тестовый пользователь")