from flask import Blueprint, render_template
from flask_login import login_required

student = Blueprint("student", __name__, url_prefix="/student")

@student.route("/dashboard")
@login_required
def dashboard():
    return render_template("student/dashboard.html")  # Шаблон для ученика
