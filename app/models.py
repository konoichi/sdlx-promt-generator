from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(UserMixin, db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=True) # Temporär True für Migration
    avatar_file = db.Column(db.String(256), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    unlocked_capabilities = db.Column(db.Text, default="") # Komma-separierte Liste
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_capabilities(self):
        if not self.unlocked_capabilities:
            return []
        return [c.strip() for f in self.unlocked_capabilities.split(",") if (c := f.strip())]

    def add_capability(self, capability):
        caps = set(self.get_capabilities())
        caps.add(capability)
        self.unlocked_capabilities = ",".join(list(caps))

    def __repr__(self):
        return f"<User {self.username or self.email}>"
