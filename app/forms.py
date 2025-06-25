from flask_wtf import FlaskForm
from wtforms import (
    StringField, 
    PasswordField, 
    SubmitField, 
    TextAreaField, 
    BooleanField, 
    RadioField
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from .models import User

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[
        DataRequired(message="Поле не может быть пустым"),
        Length(min=3, max=50, message="Имя должно быть от 3 до 50 символов")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Поле не может быть пустым"),
        Email(message="Введите корректный email"),
        Length(max=120)
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message="Введите пароль"),
        Length(min=6, message="Пароль должен быть не менее 6 символов")
    ])
    confirm_password = PasswordField('Подтвердите пароль', validators=[
        DataRequired(message="Подтвердите пароль"),
        EqualTo('password', message="Пароли должны совпадать")
    ])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Это имя пользователя уже занято')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Этот email уже зарегистрирован')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message="Введите email"),
        Email(message="Введите корректный email")
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message="Введите пароль")
    ])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class AnswerForm(FlaskForm):
    answer = TextAreaField('Ваш ответ', validators=[
        DataRequired(message="Введите ваш ответ")
    ], render_kw={"placeholder": "Например: role='navigation'"})
    submit = SubmitField('Проверить ответ')

class QuizForm(FlaskForm):
    answer = RadioField('Ваш ответ', choices=[], validators=[DataRequired(message="Выберите ответ")])
    submit = SubmitField('Отправить ответ')