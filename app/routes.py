from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from .models import User, Task, UserProgress, QuizQuestion, UserMetric
from .forms import RegistrationForm, LoginForm, AnswerForm, QuizForm
from .utils import generate_report_pdf
import markdown
import os
import json

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/theory')
def theory():
    return render_template('theory.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация прошла успешно! Теперь можете войти.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.tasks'))
        flash('Неверный email или пароль', 'danger')
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('main.index'))

@bp.route('/tasks')
@login_required
def tasks():
    tasks = Task.query.all()
    
    # Создаем записи прогресса для новых заданий
    for task in tasks:
        progress = UserProgress.query.filter_by(
            user_id=current_user.id, task_id=task.id
        ).first()
        
        if not progress:
            progress = UserProgress(
                user_id=current_user.id,
                task_id=task.id,
                completed=False
            )
            db.session.add(progress)
    
    db.session.commit()
    
    progress_list = {p.task_id: p for p in current_user.progress}
    return render_template('tasks.html', tasks=tasks, progress=progress_list)

@bp.route('/task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def task(task_id):
    task = Task.query.get_or_404(task_id)
    form = AnswerForm()

    progress = UserProgress.query.filter_by(
        user_id=current_user.id, task_id=task.id
    ).first()

    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            task_id=task.id,
            completed=False
        )
        db.session.add(progress)
        db.session.commit()

    # Начало отсчёта времени
    metric = UserMetric.query.filter_by(
        user_id=current_user.id, 
        task_id=task_id
    ).first()
    
    if not metric:
        metric = UserMetric(user_id=current_user.id, task_id=task_id)
        db.session.add(metric)
        db.session.commit()

    if form.validate_on_submit():
        user_answer = form.answer.data.strip()

        if user_answer == task.correct_answer:
            progress.completed = True
            progress.correct_attempts += 1
            flash('✅ Правильно!', 'success')
            metric.complete_task(True)
        else:
            flash(f'❌ Неправильно. Правильный ответ: {task.correct_answer}', 'danger')
            metric.complete_task(False)

        progress.last_attempt = datetime.utcnow()
        db.session.commit()

        return redirect(url_for('main.task', task_id=task.id))

    return render_template('task.html', task=task, form=form, progress=progress)

@bp.route('/theory/<topic>')
def theory_topic(topic):
    """Страница с теорией по конкретной теме"""
    # Защита от path traversal
    safe_topic = ''.join(c for c in topic if c.isalnum() or c in ['-', '_'])
    file_path = os.path.join('app', 'content', 'theory', f'{safe_topic}.md')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        html_content = markdown.markdown(content)
    except FileNotFoundError:
        flash('Материал по данной теме не найден', 'warning')
        return redirect(url_for('main.theory'))
    
    return render_template('theory_detail.html', content=html_content, topic=topic)

@bp.route('/task/<int:task_id>/quiz', methods=['GET', 'POST'])
@login_required
def quiz_task(task_id):
    """Задание в формате теста"""
    task = Task.query.get_or_404(task_id)
    if task.task_type != 'quiz':
        return redirect(url_for('main.task', task_id=task_id))
    
    questions = QuizQuestion.query.filter_by(task_id=task_id).all()
    if not questions:
        flash('Вопросы для этого задания не найдены', 'danger')
        return redirect(url_for('main.tasks'))
    
    # Начало отсчёта времени
    metric = UserMetric.query.filter_by(
        user_id=current_user.id, 
        task_id=task_id
    ).first()
    
    if not metric:
        metric = UserMetric(user_id=current_user.id, task_id=task_id)
        db.session.add(metric)
        db.session.commit()
    
    # Проверка ответа
    if request.method == 'POST':
        score = 0
        total = len(questions)
        
        for question in questions:
            user_answer = request.form.get(f'question_{question.id}')
            if user_answer == question.correct_answer:
                score += 1
        
        # Обновление прогресса
        progress = UserProgress.query.filter_by(
            user_id=current_user.id, task_id=task_id
        ).first()
        
        if not progress:
            progress = UserProgress(
                user_id=current_user.id,
                task_id=task_id,
                completed=True,
                correct_attempts=1
            )
            db.session.add(progress)
        else:
            progress.completed = True
            progress.correct_attempts += 1
        
        # Сохранение метрики
        metric.complete_task(score / total >= 0.7)
        db.session.commit()
        
        flash(f'Вы ответили правильно на {score} из {total} вопросов', 'info')
        return redirect(url_for('main.quiz_task', task_id=task_id))
    
    return render_template('quiz.html', task=task, questions=questions)

@bp.route('/dashboard')
@login_required
def dashboard():
    """Панель аналитики пользователя"""
    # Прогресс по задачам с предзагрузкой связанных задач
    progress = db.session.query(UserProgress).\
        options(db.joinedload(UserProgress.task)).\
        filter_by(user_id=current_user.id).all()
    
    # Метрики с предзагрузкой связанных задач
    metrics = db.session.query(UserMetric).\
        options(db.joinedload(UserMetric.task)).\
        filter_by(user_id=current_user.id).all()
    
    # Статистика
    completed_tasks = sum(1 for p in progress if p.completed)
    total_tasks = Task.query.count()
    completion_rate = round((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
    
    # Среднее время только по успешным попыткам
    successful_metrics = [m for m in metrics if m.success and m.time_spent]
    avg_time = round(sum(m.time_spent for m in successful_metrics) / len(successful_metrics)) if successful_metrics else 0
    
    return render_template('dashboard.html', 
                          progress=progress,
                          metrics=metrics,
                          completed_tasks=completed_tasks,
                          total_tasks=total_tasks,
                          completion_rate=completion_rate,
                          avg_time=avg_time)

@bp.route('/survey')
@login_required
def survey():
    """Анкета оценки системы (SUS)"""
    return render_template('survey.html')

@bp.route('/submit_survey', methods=['POST'])
@login_required
def submit_survey():
    """Обработка результатов анкеты"""
    # Здесь будет логика сохранения результатов
    flash('Спасибо за ваши ответы! Ваше мнение очень важно для нас.', 'success')
    return redirect(url_for('main.dashboard'))

@bp.route('/report')
@login_required
def generate_report():
    """Генерация итогового отчёта"""
    # Сбор данных для отчёта
    user_data = {
        'username': current_user.username,
        'email': current_user.email,
        'registration_date': current_user.created_at.strftime('%d.%m.%Y'),
        'level': current_user.level
    }
    
    # Прогресс
    progress = UserProgress.query.filter_by(user_id=current_user.id).all()
    progress_data = [
        {
            'task': p.task.title,
            'completed': 'Да' if p.completed else 'Нет',
            'attempts': p.correct_attempts,
            'last_attempt': p.last_attempt.strftime('%d.%m.%Y %H:%M') if p.last_attempt else 'Нет данных'
        } 
        for p in progress
    ]
    
    # Генерация PDF
    pdf_file = generate_report_pdf(user_data, progress_data)
    
    # Отправка файла
    return send_file(
        pdf_file,
        as_attachment=True,
        download_name=f'report_{current_user.username}.pdf',
        mimetype='application/pdf'
    )

@bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@bp.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500