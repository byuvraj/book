from flask import Flask, render_template, request, session
from model import *
from flask_session import Session
 
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]=os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"
Session(app)
db.init_app(app)

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/book", methods=["POST", "GET"])
def book():
    if session.get("login") is None:
        session["login"] = 0
    if request.method == "POST":
        users = User.query.all()
        username = request.form.get("name")
        password = request.form.get("password")
        if not username is None:
            user = User.query.get(username)
            if user is None:
                return render_template("login.html", message="Invalid username")
            elif user.password == password:
                session["login"]=1
                return render_template("book.html", name=username)
            else:
                return render_template("login.html", message="Invalid password")
    if request.method == "GET":
        if session["login"] == 1 :
            return render_template("book.html")
        else:
            return render_template("login.html", message="Please login instead")
      
@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html")

@app.route("/welcome", methods=["POST"])
def welcome():
    newusername = request.form.get("newname")
    newpassword = request.form.get("newpassword")
    user = User.query.get(newusername)
    if newusername == "" :
        return render_template("register.html", message="Enter valid username or password")
    elif not user is None :
        return render_template("register.html", message="Username already exists")
    elif newpassword == "" :
        return render_template("register.html", message="Enter valid username or password")
    else:
        users = User.query.all()
        id=0
        for user in users :
            id+=1
        newuser = User(username=newusername, id=id , password=newpassword)
        try:
            db.session.add(newuser)
            db.session.commit()
            return render_template("welcome.html", message="Welcome", newusername=newusername )
        except TypeError:
            return render_template("welcome.html", message="Some error accured try again later")