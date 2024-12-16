from flask import request, Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from .. import db
from ..models.models import Lesson, Class, Subject, Grade, User
from datetime import datetime

teacher = Blueprint("teacher", __name__, url_prefix="/teacher")


# Роут для отображения карточек классов и предметов
@teacher.route("/dashboard")
@login_required
def dashboard():
    # Проверяем, что текущий пользователь - учитель
    if current_user.role.name != "teacher":
        return "Доступ запрещен", 403

    # Получаем уроки, которые преподавал текущий учитель
    lessons = Lesson.query.filter_by(teacher_id=current_user.id).all()
    classes = {}

    # Собираем классы и предметы, которые преподает учитель
    for lesson in lessons:
        classroom = lesson.classroom
        if classroom not in classes:
            classes[classroom] = []
        classes[classroom].append(lesson.subject)

    return render_template("teacher/dashboard.html", classes=classes)


@teacher.route("/class_journal/<int:class_id>/<int:subject_id>")
@login_required
def class_journal(class_id, subject_id):
    if current_user.role.name != "teacher":
        return "Доступ запрещен", 403

    # Получение класса и предмета
    classroom = Class.query.get_or_404(class_id)
    subject = Subject.query.get_or_404(subject_id)

    # Получение всех уроков для данного класса и предмета
    lessons = Lesson.query.filter_by(class_id=classroom.id, subject_id=subject.id).order_by(Lesson.date).all()

    # Получение всех учеников класса
    students = User.query.filter_by(class_id=classroom.id).all()

    # Журнал для отображения
    journal_data = []
    for student in students:
        student_data = {
            "id": student.id,
            "name": student.name,
            "grades": []
        }

        # Получение оценок для каждого урока
        for lesson in lessons:
            grade = Grade.query.filter_by(student_id=student.id, lesson_id=lesson.id).first()
            student_data["grades"].append({
                "lesson_id": lesson.id,
                "grade": grade.grade if grade else "Пропуск"
            })

        journal_data.append(student_data)

    return render_template(
        "teacher/class_journal.html",
        classroom=classroom,
        subject=subject,
        lessons=lessons,
        journal=journal_data
    )

@teacher.route("/update_grades", methods=["POST"])
@login_required
def update_grades():
    if current_user.role.name != "teacher":
        return jsonify({"success": False, "error": "Доступ запрещен"}), 403

    grades_data = request.form.to_dict(flat=False)  # Сбор всех данных из формы
    for student_id, lessons in grades_data.items():
        for lesson_id, grade_value in lessons.items():
            # Пропускаем пустые значения
            if not grade_value.strip():
                continue

            grade_value = int(grade_value)
            grade = Grade.query.filter_by(student_id=student_id, lesson_id=lesson_id).first()
            if grade:
                grade.grade = grade_value
            else:
                grade = Grade(student_id=student_id, lesson_id=lesson_id, grade=grade_value, teacher_id=current_user.id)
                db.session.add(grade)

    try:
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
