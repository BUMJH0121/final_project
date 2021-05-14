from flask import Flask, redirect, render_template, url_for, request, flash, session
import sys
from DB_handler import DBModule
# import database
app = Flask(__name__)
DB = DBModule()
app.secret_key = "abcdefg"

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/login_done", methods=["get"])
def login_done():
    uid = request.args.get("id")
    pwd = request.args.get("pwd")
    if DB.login(uid, pwd):
        session["uid"] = uid
        return redirect(url_for("mypage"))
    else:
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    pass

@app.route("/signin")
def signin():
    return render_template("signin.html")

@app.route("/signin_done")
def signin_done():
    uid = request.args.get("id")
    pwd = request.args.get("pwd")
    if DB.signin(_id_=uid, pwd=pwd):
        return redirect(url_for("mypage"))
    else:
        return redirect(url_for("signin"))

@app.route("/mypage")
def mypage():
    graph = f"/graph_img.jpg"
    return render_template("mypage.html", graph=graph)

@app.route("/mypage/photo")
def photo():
    return render_template("photo.html")
    
@app.route("/mypage/product")
def product():
    return render_template("product.html")







if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
