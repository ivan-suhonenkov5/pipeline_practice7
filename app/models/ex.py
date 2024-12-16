from ..extensions import db
from datetime import datetime, timezone
import sqlalchemy.orm as so
import sqlalchemy as sa


class Post4(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    subject = db.Column(db.String(250))
    student = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.now(timezone.utc))