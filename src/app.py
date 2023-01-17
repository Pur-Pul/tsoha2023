from flask import Flask, render_template, redirect, request, session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    hash_value = generate_password_hash(request.form["password"])
    session["username"] = username
    return redirect("/")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")
