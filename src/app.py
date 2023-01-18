from flask import Flask, render_template, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from services import UserService
from os import getenv

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL").replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

user_service = UserService(db)

@app.route("/")
def index():
    return render_template("index.html", message = "")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    if user_service.validate_credentials(username, password):
        session["username"] = username
        return redirect("/")
    else:
        return render_template("index.html", message = "Incorrect login credentials")
    

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    hash_value = generate_password_hash(request.form["password"])
    user_service.register(username, hash_value)
