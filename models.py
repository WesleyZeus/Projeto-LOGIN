from db import db
from flask_login import UserMixin

class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(db.String(80), unique=True)
    senha = db.Column(db.String())

    def get_id(self):
        return str(self.id) 