from flask import Blueprint, render_template
from flask_login import login_required

parent = Blueprint("parent", __name__, url_prefix="/parent")

@parent.route("/dashboard")
@login_required
def dashboard():
    return render_template("parent/dashboard.html")  # Шаблон для родителя
