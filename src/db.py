from src.app import app
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from flask_wtf.csrf import CSRFProtect

app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL").replace(
    "postgres://",
    "postgresql://", 1
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
csrf = CSRFProtect()
csrf.init_app(app)
db = SQLAlchemy(app)