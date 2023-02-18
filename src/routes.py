import json
from flask import render_template, redirect, request, session, jsonify, make_response, flash
from flask_wtf.csrf import CSRFError

from services import UserService, EditorService, ImageService, PostService, ReplyService, InvalidUserNameException, InvalidPasswordException
from app import app

user_service = UserService()
editor_service = EditorService()
image_service = ImageService()
post_service = PostService()
reply_service = ReplyService()

def sign(value):
    return (value > 0) - (value < 0)

def validate_user_id(user_id):
    return user_service.get_id(session["username"]) == user_id

@app.errorhandler(CSRFError)
def handle_csrf_error(error):
    return render_template('csrf_error.html', reason=error.description), 400

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
    flash("Incorrect login credentials")
    return render_template("index.html")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            user_service.register(username, password)
            return redirect("/")
        except (InvalidUserNameException, InvalidPasswordException) as error:
            flash(str(error))
            return render_template("index.html")
        
    session["register"] = True
    return render_template("index.html")

@app.route("/editor", methods=["GET","POST"])
def editor():
    if request.method == "GET":
        try:
            actions = editor_service.get_actions(user_service.get_id(session["username"]))
            return render_template("editor.html", actions=actions, action_count=len(actions))
        except KeyError:
            flash("You need to login first.")
            return redirect("/")

    jsdata = request.get_json()
    if 'undo' not in jsdata.keys():
        pixels = []
        for item in jsdata.values():
            if isinstance(item, dict):
                pixels.append((item["x"], item["y"]))

        editor_service.color_pixels(
            pixels,
            jsdata["color"],
            user_service.get_id(session["username"])
        )
        response = jsonify({"message" : "brush saved"})
    else:
        actions = editor_service.undo_action(user_service.get_id(session["username"]))
        response = jsonify(actions)
    return make_response(response, 200)

@app.route("/editor/clear", methods=["POST"])
def clear():
    editor_service.clear_actions(user_service.get_id(session["username"]))
    return redirect("/editor")

@app.route("/editor/save_to_profile", methods=["POST"])
def save_to_profile():
    image_service.save_as_image(user_service.get_id(session["username"]))
    return redirect("/editor")

@app.route("/profile/", methods=["GET"])
def profile_redirect():
    try:
        session['username']
    except KeyError:
        flash("You need to login first.")
        return redirect("/")
    
    return redirect("/profile/"+session["username"])
    

@app.route("/profile/<username>", methods=["GET"])
def profile(username):
    try: 
        session['username']
    except KeyError:
        flash("You need to login first.")
        return redirect("/")

    images={}
    if username==session["username"]:
        images = image_service.get_user_images(user_service.get_id(username))
    return render_template("profile.html", images=images, username=username)


@app.route("/make-post", methods=["POST"])
def make_post():
    owner_id = image_service.get_image_owner_id(request.get_json()["id"])
    if not validate_user_id(owner_id):
        return "Invalid post request"
    
    post_id = post_service.make_post(request.get_json()["id"], request.get_json()["title"])
    reply_service.create_reply_section(post_id)

    res = make_response(jsonify({"message": "post made"}), 200)
    return res

@app.route("/posts", methods=["GET"])
def posts_redirect():
    return redirect("/posts/"+"new")

@app.route("/posts/<option>", methods=["GET"])
def posts(option):
    if not option:
        option = "new"
    posts = post_service.get_posts(option)
    images = []
    for post in posts:
        images.append(image_service.get_image(post.image_id))
    return render_template("posts.html", posts=posts, images=images)

@app.route("/post/<int:post_id>", methods=["GET"])
def post(post_id):
    post = post_service.get_post(post_id)
    if post is None:
        return make_response("404: Post does not exist", 404)
    image = image_service.get_image(post.image_id)
    replies = reply_service.get_post_replies(post_id)
    return render_template("post.html", post=post, image=image, replies=replies)

@app.route("/post/<int:post_id>/reply", methods=["POST"])
def make_post_reply(post_id):
    try:
        session['username']
    except KeyError:
        return make_response(jsonify({"message":"You need to login first"}), 202)
    reply_service.create_post_reply(post_id, user_service.get_id(session["username"]), request.get_json()["content"])
    return redirect("/post/"+str(post_id))

@app.route("/post/<int:post_id>/vote", methods=["POST"])
def make_post_vote(post_id):
    try:
        session['username']
    except KeyError:
        return make_response(jsonify({"message":"You need to login first"}), 202)
    points = sign(request.get_json()["value"])
    reply_service.create_post_vote(post_id, user_service.get_id(session["username"]), points)
    return redirect("/post/"+str(post_id))
