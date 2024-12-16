from datetime import datetime, timezone
from ..extensions import db, login_manager
from flask_login import UserMixin


# Таблица Роль
class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)


# Таблица Пользователь
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    avatar = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(50), default="user")
    class_id = db.Column(db.Integer, db.ForeignKey('class.id', ondelete='CASCADE'))  # Новый столбец для связи с классом

    # Связь с ролью
    role = db.relationship('Role', backref='users', lazy='select')

    # Связь с классом
    classroom = db.relationship('Class', backref='students', lazy='select')  # Связь с классом

    # Связь с родителем
    children = db.relationship('ParentStudent', foreign_keys='ParentStudent.parent_id', backref='parent', lazy='dynamic')
    parents = db.relationship('ParentStudent', foreign_keys='ParentStudent.student_id', backref='student', lazy='dynamic')

    # Связь с постами
    posts = db.relationship('Post', backref='author', lazy='dynamic')


# Таблица Класс
class Class(db.Model):
    __tablename__ = 'class'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    # Связь с уроками
    lessons = db.relationship('Lesson', backref='classroom_association', lazy='dynamic')


# Таблица Предмет
class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    hours = db.Column(db.Integer, nullable=False)

    # Связь с уроками
    lessons = db.relationship('Lesson', backref='subject_in_lesson', lazy='dynamic')


# Таблица Занятие (урок)
class Lesson(db.Model):
    __tablename__ = 'lesson'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id', ondelete='CASCADE'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    # Связь с пользователем (учителем)
    teacher = db.relationship('User', backref='teaching_lessons', lazy='select')

    # Связь с классом
    classroom = db.relationship('Class', backref='lessons_in_class', lazy='select')

    # Связь с предметом
    subject = db.relationship('Subject', backref='lessons_in_subject', lazy='select')


# Таблица Оценки
class Grade(db.Model):
    __tablename__ = 'grade'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id', ondelete='CASCADE'), nullable=False)  # Привязка к уроку
    grade = db.Column(db.Integer, nullable=True)  # Оценка ученика (может быть None, если пропуск)

    # Связь с учеником
    student = db.relationship('User', foreign_keys=[student_id], backref='grades', lazy='select')

    # Связь с уроком
    lesson = db.relationship('Lesson', backref='grades_in_lesson', lazy='select')

    def __repr__(self):
        return f'<Grade {self.id} - Student: {self.student.name}, Lesson: {self.lesson.id}, Grade: {self.grade}>'


# Таблица Посты
class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    subject = db.Column(db.String(250), nullable=True)
    student_id = db.Column(db.Integer, nullable=True)
    date = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    # Связь с автором поста (учителем)
    teacher = db.relationship('User', backref='teaching_posts', lazy='select')


# Таблица Родитель-Ученик
class ParentStudent(db.Model):
    __tablename__ = 'parent_student'
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    # Уникальная связь "родитель-ученик"
    __table_args__ = (db.UniqueConstraint('parent_id', 'student_id', name='_parent_student_uc'),)


# Подключение Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
