from flask import Flask, render_template, redirect, request, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, CSRFError
from werkzeug.security import generate_password_hash
from services import UserService
from services import EditorService
from os import getenv
import secrets
import random

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL").replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
csrf = CSRFProtect()
csrf.init_app(app)
db = SQLAlchemy(app)

user_service = UserService(db)
editor_service = EditorService(db)

@app.route("/")
def index():
    session["register"] = False
    return render_template("index.html", message = "")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    if user_service.validate_credentials(username, password):
        session["username"] = username
        session["csrf_token"] = secrets.token_hex(16)
        return redirect("/")
    else:
        return render_template("index.html", message = "Incorrect login credentials")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        hash_value = generate_password_hash(request.form["password"])
        user_service.register(username, hash_value)
        return redirect("/")
    else:
        session["register"] = True
        return render_template("index.html")

@app.route("/editor", methods=["GET","POST"])
def editor():
    if request.method == "GET":
        if not session["username"]:
            return redirect("/")
        actions = editor_service.get_actions(user_service.get_id(session["username"]))
        actions=[]
        coords=[]
        for x in range(0,32):
            for y in range(0,32):
                coords.append((x,y))
        random.shuffle(coords)
        for i in range(0,1024):
            actions.append((i,coords[i][0],coords[i][1],"#000000"))
        print(actions)
        return render_template("editor.html", actions=actions) #[(1,1,2,"#000000"),(2,3,4,"#000000"),(3,5,6,"#000000")]
    else:
        return redirect("/")
