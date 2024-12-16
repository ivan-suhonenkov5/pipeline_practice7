from flask import Blueprint, redirect, render_template, flash, url_for, request
from flask_login import login_user, logout_user, login_required, current_user

from ..functions import save_picture
from ..forms import RegistrationForm, LoginForm, ProfileForm
from ..extensions import db, bcrypt
from ..models.models import User, Role


user = Blueprint("user", __name__)

@user.route("/profile/<int:user_id>", methods=["GET", "POST"])
@login_required
def profile(user_id):
    # Проверяем, что пользователь редактирует свой профиль
    if user_id != current_user.id:
        flash("У вас нет доступа к этому профилю.", "danger")
        return redirect(url_for("post.all"))

    form = ProfileForm()
    user = User.query.get_or_404(user_id)

    if request.method == "GET":
        # Заполняем форму текущими данными пользователя
        form.name.data = user.name
        form.login.data = user.login

    elif form.validate_on_submit():  # Обновляем только если форма валидна
        # Добавляем отладочные сообщения для проверки данных
        print(f"Данные из формы: name={form.name.data}, login={form.login.data}")

        # Обновляем поля пользователя
        user.name = form.name.data
        user.login = form.login.data

        if form.password.data:  # Если указан новый пароль
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
            user.password = hashed_password

        if form.avatar.data:  # Если загружен новый аватар
            avatar_filename = save_picture(form.avatar.data)
            user.avatar = avatar_filename

        try:
            # Сохраняем изменения в базе данных
            db.session.commit()
            flash("Ваш профиль был успешно обновлен.", "success")
            return redirect(url_for("user.profile", user_id=user.id))
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при обновлении: {str(e)}")
            flash("Произошла ошибка при сохранении изменений. Попробуйте снова.", "danger")
    else:
        print(f"Ошибка валидации формы: {form.errors}")

    return render_template("user/profile.html", form=form, user=user)

@user.route('/user/register', methods=['POST', 'GET'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        avatar_filename = save_picture(form.avatar.data)

        # Получаем роль по умолчанию (например, "ученик"). Вы можете изменить это.
        default_role = Role.query.filter_by(name='student').first()

        if not default_role:
            flash("Ошибка регистрации: Роль по умолчанию не найдена. Обратитесь к администратору.", "danger")
            return redirect(url_for('user.register'))

        # Создаём нового пользователя с ролью
        user = User(
            name=form.name.data,
            login=form.login.data,
            avatar=avatar_filename,
            password=hashed_password,
            role_id=default_role.id,  # Присваиваем ID роли
            status='user'
        )
        try:
            db.session.add(user)
            db.session.commit()
            flash(f"Поздравляем, {form.login.data}! Вы успешно зарегистрированы", "success")
            return redirect(url_for('user.login'))
        except Exception as e:
            db.session.rollback()
            print(str(e))
            flash(f"При регистрации произошла ошибка: {str(e)}", "danger")
    return render_template('user/register.html', form=form)


@user.route("/user/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            # Перенаправление в зависимости от роли
            if user.role.name == "admin":
                flash(f"Добро пожаловать, {form.login.data}! Вы вошли как администратор.", "success")
                return redirect(url_for("admin.dashboard"))
            elif user.role.name == "teacher":
                flash(f"Добро пожаловать, {form.login.data}! Вы вошли как учитель.", "success")
                return redirect(url_for("teacher.dashboard"))
            elif user.role.name == "student":
                flash(f"Добро пожаловать, {form.login.data}! Вы вошли как ученик.", "success")
                return redirect(url_for("student.dashboard"))
            elif user.role.name == "methodologist":
                flash(f"Добро пожаловать, {form.login.data}! Вы вошли как методист.", "success")
                return redirect(url_for("methodologist.dashboard"))
            elif user.role.name == "parent":
                flash(f"Добро пожаловать, {form.login.data}! Вы вошли как родитель.", "success")
                return redirect(url_for("parent.dashboard"))

            # Если роль неизвестна, возвращаем ошибку
            flash(f"Роль {user.role.name} не распознана. Обратитесь к администратору.", "danger")
            return redirect(url_for("user.login"))
        else:
            flash(f"Ошибка входа. Пожалуйста, проверьте логин и пароль!", "danger")
    return render_template("user/login.html", form=form)


@user.route("/user/logout", methods=["POST", "GET"])
def logout():
    logout_user()
    return redirect(url_for("user.login"))

