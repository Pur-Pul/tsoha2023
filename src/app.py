from flask import Flask, render_template, redirect, request, session, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, CSRFError
from werkzeug.security import generate_password_hash
from services import UserService, EditorService, ImageService, PostService
from os import getenv
import secrets
import random
import json

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL").replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#csrf = CSRFProtect()
#csrf.init_app(app)
db = SQLAlchemy(app)

user_service = UserService(db)
editor_service = EditorService(db)
image_service = ImageService(db)
post_service = PostService(db)

def validate_user_id(id):
    return user_service.get_id(session["username"]) == id

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
        return render_template("editor.html", actions=actions, action_count=len(actions))
    elif request.method == "POST":
        jsdata = request.get_json()
        pixels = []
        for item in jsdata.values():
            if isinstance(item, dict):
                pixels.append((item["x"], item["y"]))
        editor_service.color_pixels(pixels, jsdata["color"],user_service.get_id(session["username"]))

        res = make_response(jsonify({"message": "JSON recieved"}), 200)

        return res

@app.route("/editor/clear", methods=["POST"])
def clear():
    editor_service.clear_actions(user_service.get_id(session["username"]))
    return redirect("/editor")

@app.route("/editor/save_to_profile", methods=["POST"])
def save_to_profile():
    image_service.save_as_image(user_service.get_id(session["username"]))
    return redirect("/editor")

@app.route("/profile/<username>", methods=["GET"])
def profile(username):
    images={}
    for id in image_service.get_image_ids(user_service.get_id(username)):
        images[id] = json.dumps(image_service.get_image(id))
    return render_template("profile.html", images=images, username=username)

@app.route("/make-post", methods=["POST"])
def make_post():
    owner_id = image_service.get_image_owner_id(request.get_json()["id"])
    if not validate_user_id(owner_id):
        return "Invalid post request"
    post_service.make_post(request.get_json()["id"], request.get_json()["title"])
    return redirect("/profile/"+session["username"])
