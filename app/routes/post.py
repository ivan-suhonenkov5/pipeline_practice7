from flask import Blueprint, render_template, request, redirect, abort
from flask_login import login_required, current_user
from sqlalchemy import desc

from ..extensions import db
from ..forms import StudentForm, TeacherForm
from ..models.models import Post, User, Role

post = Blueprint("post", __name__)


@post.route("/", methods=["POST", "GET"])
def all():
    form = TeacherForm()
    # Выбираем пользователей с ролью "teacher"
    teacher_role = Role.query.filter_by(name='teacher').first()
    if not teacher_role:
        abort(500, "Role 'teacher' not found in the database.")
    form.teacher.choices = [t.name for t in User.query.filter_by(role_id=teacher_role.id).all()]

    if request.method == "POST":
        teacher = request.form["teacher"]
        teacher_id = User.query.filter_by(name=teacher).first().id
        posts = Post.query.filter_by(teacher=teacher_id).order_by(Post.date.desc()).all()
    else:
        posts = Post.query.order_by(Post.date.desc()).limit(20).all()
    return render_template("post/all.html", posts=posts, user=User, form=form)


@post.route("/post/create", methods=["POST", "GET"])
@login_required
def create():
    form = StudentForm()
    # Выбираем пользователей с ролью "student"
    student_role = Role.query.filter_by(name='student').first()
    if not student_role:
        abort(500, "Role 'student' not found in the database.")
    form.student.choices = [s.name for s in User.query.filter_by(role_id=student_role.id).all()]

    if request.method == "POST":
        subject = request.form.get("subject")
        student = request.form.get("student")
        student_id = User.query.filter_by(name=student).first().id

        post = Post(teacher=current_user.id, subject=subject, student=student_id)

        try:
            db.session.add(post)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            db.session.rollback()
            print(str(e))

    return render_template("post/create.html", form=form)


@post.route("/post/<int:id>/update", methods=["POST", "GET"])
@login_required
def update(id):
    post = Post.query.get(id)

    # Проверяем, является ли пользователь автором поста или имеет роль "teacher"
    teacher_role = Role.query.filter_by(name='teacher').first()
    if post.author.id == current_user.id or current_user.role_id == teacher_role.id:
        form = StudentForm()
        student_role = Role.query.filter_by(name='student').first()
        if not student_role:
            abort(500, "Role 'student' not found in the database.")

        form.student.data = User.query.filter_by(id=post.student).first().name
        form.student.choices = [s.name for s in User.query.filter_by(role_id=student_role.id).all()]

        if request.method == "POST":
            post.subject = request.form.get("subject")
            student = request.form.get("student")

            post.student = User.query.filter_by(name=student).first().id

            try:
                db.session.commit()
                return redirect("/")
            except Exception as e:
                db.session.rollback()
                print(str(e))
        else:
            return render_template("post/update.html", post=post, form=form)
    else:
        abort(403)


@post.route("/post/<int:id>/delete", methods=["POST", "GET"])
@login_required
def delete(id):
    post = Post.query.get(id)

    # Проверяем, является ли пользователь автором поста или имеет роль "teacher"
    teacher_role = Role.query.filter_by(name='teacher').first()
    if post.author.id == current_user.id or current_user.role_id == teacher_role.id:
        try:
            db.session.delete(post)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            db.session.rollback()
            print(str(e))
            return str(e)
    else:
        abort(403)
