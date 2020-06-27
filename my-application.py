import os 

from flask import Flask, render_template, request, url_for, redirect, session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_session import Session
from search import *

app = Flask(__name__)

engine = create_engine("postgres://rjmwjpklbssodm:fc5d900a9df31462fab30b7fd752dc1bdbf0432a1931f652be1eb0d5d97510c2@ec2-52-44-55-63.compute-1.amazonaws.com:5432/d8itmsoa2csvlk")
db =  scoped_session(sessionmaker(bind=engine))
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"
app.secret_key = "hello"
Session(app)


@app.route("/")
def index():
    if not "user_id" in session:
        session["user_id"]=False
    if session["user_id"]:
        return redirect(url_for("book"))
    else:
        return render_template("login.html")


@app.route("/book", methods=["POST", "GET"])
def book():
    if request.method == "POST":
        name = request.form.get("name")
        session["user"] = name
        password = request.form.get("password")
        if not session["user_id"]:
            if name == '' or name is None:
                return render_template("login.html", message="Invalid Username")
            if db.execute("SELECT username, password FROM username WHERE username = :user", {"user":name}).rowcount == 0:
                return render_template("login.html", message="Invalid user")
            else:
                user = db.execute("SELECT username, password FROM username WHERE username = :user", {"user":name}).fetchone()
                if user.password == password :
                    session["user_id"] = True
                    return render_template("book.html", message='')
                else:
                    return render_template("login.html", message="Invalid password")
        else:
            return render_template("book.html", message='')
    if request.method == "GET":
        if session["user_id"]:
            return render_template("book.html", message='')
        else:
            return render_template("login.html",message="Please login first")

@app.route("/logout", methods=["POST","GET"])
def logout():
    if "user_id" in session:
         session["user_id"] = False 
    return redirect(url_for("index"))

@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html")

@app.route("/welcome", methods=["POST"])
def welcome():
    newusername = request.form.get("newname")
    newpassword = request.form.get("newpassword")
    if newusername =="" or newpassword =="" :
        return render_template("register.html", message="Please input valid username or password")
    elif not db.execute("SELECT username FROM username WHERE username = :user", {"user":newusername}).rowcount == 0:
        return render_template("register.html", message="Username already exists")
    else:
        users = db.execute("SELECT username, password FROM username").fetchall()
        id=0
        for user in users:
            id+=1
        db.execute("INSERT INTO username (username, id, password) VALUES (:user, :id, :password)", {"user":newusername, "id":id, "password":newpassword})
        db.commit()
        return redirect(url_for("index"))

@app.route("/search", methods=["POST", "GET"])
def search_book():
    try:
        if request.method == "GET":
            return redirect(url_for("index"))
        if session["user_id"]:
            if request.method == "POST":
                name = request.form.get("search")
            books_found = search(name)
            if books_found == []:
                return render_template ("book.html", message="No books found")
            else:
                return render_template("book.html", books_found=books_found, message='')
        else:
            return redirect(url_for('index'))
    except ValueError:
        return redirect(url_for('index'))

@app.route("/searching/<string:name>", methods=["GET"])
def searching(name):
    try:
        books_found = search(name)
        if books_found == []:
            return render_template ("book.html", message="No books found")
        else:
            return render_template("book.html", books_found=books_found, message='')
    except ValueError:
        return render_template("book.html", message="No books found")

@app.route("/review/<string:name>", methods=["POST", "GET"])
def review(name):
    if session["user_id"]:
        if name == "error":
            return render_template("review.html", message="Please submit your review")
        else:
            try:
                book = search(name)
                reviews=db.execute("SELECT * FROM review WHERE book_id=:book",{"book":session["book_id"]})
                for b in book:
                    session["book_title"] = b.title 
                    session["book_id"] = b.id
                    rating=b.rating
                return render_template("review.html",rating=rating, book=book, user=session["user"], reviews=reviews)
            except TypeError:
                return render_template("review.html", message="Sorry some error accured")
    else:
        return redirect(url_for('index'))

@app.route("/submit_review", methods=["POST", "GET"])
def submit_review():
    if session["user_id"]:
        if request.method == "Get":
            return redirect(url_for('review/error'))
        elif request.method == "POST":
            user_review=db.execute("SELECT * FROM review WHERE book_id=:id",{"id":session["book_id"]})
            title =session["book_title"]
            for user in user_review:
                if user.user_id == session["user"]:
                    return redirect(url_for('review', name=title))
            rating = request.form.get("rating")
            review = request.form.get("review")
            print(type(rating))
            book_info=db.execute("SELECT rating, review_count FROM book WHERE title=:title",{"title":title}).fetchall()
            for info in book_info:
                rating = int(rating)
                if info.rating == 0:
                    new_rating = rating
                else:
                    new_rating = (info.rating + rating)/2
                review_count = info.review_count + 1
                print(type(info.rating))
            db.execute("INSERT INTO review (revieW, book_id, user_id) VALUES (:review, :book_id, :user_id)", {"review":review, "book_id":session["book_id"], "user_id":session["user"]})
            db.execute("UPDATE book SET rating=:rating, review_count=:review_count WHERE id=:id", {"rating":new_rating, "review_count":review_count, "id":session["book_id"]})
            db.commit() 
            return redirect(url_for('review', name=title))

if __name__ == '__main__':  
    app.run(threaded=True, port=5000)
