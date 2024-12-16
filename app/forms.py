from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional

from app.models.models import User


class RegistrationForm(FlaskForm):
    name = StringField("Имя", validators=[DataRequired(), Length(min=2, max=100)])
    login = StringField("Логин", validators=[
        DataRequired(),
        Length(min=2, max=20)])
    password = PasswordField("Пароль", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Подтвердите пароль", validators=[DataRequired(), EqualTo("password")]
    )
    avatar = FileField(
        "Загрузите аватар", validators=[
            FileRequired(message="Файл обязательный для загрузки"),
            FileAllowed(["jpg", "jpeg", "png"], message="Допустимые форматы: jpg, jpeg, png")]
    )
    submit = SubmitField("Зарегистрироваться")

    def validate_login(self, login):
        if User.query.filter_by(login=login.data).first():
            raise ValidationError('Данное имя пользователя уже занято!')


class LoginForm(FlaskForm):
    """Form for login users"""
    login = StringField("Логин", validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField("<PASSWORD>", validators=[DataRequired()])
    remember = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")


class StudentForm(FlaskForm):
    student = SelectField("student", choices=[], render_kw={"class": "form-control"})


class TeacherForm(FlaskForm):
    teacher = SelectField("teacher", choices=[], render_kw={"class": "form-control"})


class AdminCreateUserForm(FlaskForm):
    name = StringField("Имя", validators=[DataRequired(), Length(min=2, max=100)])
    login = StringField("Логин", validators=[
        DataRequired(),
        Length(min=2, max=20)])
    password = PasswordField("Пароль", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Подтвердите пароль", validators=[DataRequired(), EqualTo("password")]
    )
    avatar = FileField(
        "Загрузите аватар", validators=[
            FileAllowed(["jpg", "jpeg", "png"], message="Допустимые форматы: jpg, jpeg, png")]
    )
    role_id = SelectField("Роль", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Создать пользователя")

    def validate_login(self, login):
        if User.query.filter_by(login=login.data).first():
            raise ValidationError('Данное имя пользователя уже занято!')


class ProfileForm(FlaskForm):
    name = StringField(
        "Имя",
        validators=[Length(min=2, max=100, message="Имя должно быть от 2 до 100 символов."), Optional()],
    )
    login = StringField(
        "Логин",
        validators=[Length(min=2, max=20, message="Логин должен быть от 2 до 20 символов."), Optional()],
    )
    password = PasswordField(
        "Новый пароль",
        validators=[Length(min=6, message="Пароль должен быть не менее 6 символов."), Optional()],
    )
    confirm_password = PasswordField(
        "Подтвердите новый пароль",
        validators=[EqualTo("password", message="Пароли должны совпадать"), Optional()],
    )
    avatar = FileField(
        "Загрузите новый аватар",
        validators=[
            FileAllowed(["jpg", "jpeg", "png"], message="Допустимые форматы: jpg, jpeg, png"),
            Optional(),
        ],
    )
    submit = SubmitField("Сохранить изменения")
