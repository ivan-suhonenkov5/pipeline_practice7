from flask import Blueprint, render_template
from flask_login import login_required

methodologist = Blueprint("methodologist", __name__, url_prefix="/methodologist")

@methodologist.route("/dashboard")
@login_required
def dashboard():
    return render_template("methodologist/dashboard.html")  # Шаблон для методиста
