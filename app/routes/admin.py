from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models.models import User, Role
from ..extensions import db

from ..functions import save_picture
from ..forms import AdminCreateUserForm
from ..extensions import bcrypt

admin = Blueprint("admin", __name__, url_prefix="/admin")
@admin.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    if current_user.role.name != "admin":
        return redirect(url_for("user.login"))
    # Получаем список всех пользователей
    users = User.query.all()
    return render_template("admin/dashboard.html", users=users)
@admin.route("/users/create", methods=["GET", "POST"])
@login_required
def create_user():
    if current_user.role.name != "admin":
        return redirect(url_for("user.login"))

    form = AdminCreateUserForm()
    form.role_id.choices = [(role.id, role.name) for role in Role.query.all()]  # Наполняем список ролей

    if form.validate_on_submit():
        avatar_filename = None
        if form.avatar.data:  # Сохраняем файл аватара, если он предоставлен
            avatar_filename = save_picture(form.avatar.data)

        # Используем bcrypt для хэширования пароля
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(
            login=form.login.data,
        password = hashed_password,
        name = form.name.data,
        avatar = avatar_filename,
        role_id = form.role_id.data,
        status = "user"
        )

        try:
            db.session.add(new_user)
            db.session.commit(
                flash("Пользователь успешно создан.", "success"))
            return redirect(url_for("admin.dashboard"))
        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при создании пользователя: {e}", "danger")

    return render_template("admin/create_user.html", form=form)


@admin.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    if current_user.role.name != "admin":
        return redirect(url_for("user.login"))

    user = User.query.get(user_id)
    if not user:
        flash("Пользователь не найден.", "danger")
        return redirect(url_for("admin.dashboard"))

    try:
        db.session.delete(user)
        db.session.commit()
        flash("Пользователь успешно удалён.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при удалении пользователя: {e}", "danger")

    return redirect(url_for("admin.dashboard"))


@admin.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    if current_user.role.name != "admin":
        return redirect(url_for("user.login"))

    user = User.query.get(user_id)
    roles = Role.query.all()

    if not user:
        flash("Пользователь не найден.", "danger")
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        user.login = request.form.get("login")
        user.role_id = request.form.get("role_id")
        password = request.form.get("password")
        if password:
            user.password = bcrypt.generate_password_hash(password).decode('utf-8')

        try:
            db.session.commit()
            flash("Данные пользователя успешно обновлены.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при обновлении пользователя: {e}", "danger")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/edit_user.html", user=user, roles=roles)
