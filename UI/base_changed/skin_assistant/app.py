from flask import request
from functools import wraps
import json
from os import environ as env
from werkzeug.exceptions import HTTPException

#from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
import pymysql
#from DB_handler import DBModule
# import database
app = Flask(__name__)
#DB = DBModule()
app.secret_key = "abcdefg"


oauth = OAuth(app)

auth0 = oauth.register(
        'auth0',
        client_id='7CwVk5EnKG8UQ9x0ZsksvdJvTDe0BhcZ',
        client_secret='_T9bx1apHo1-ATAr1BeyqBoDfsZMow43K7l7ZzKB-cwp71vv1gxnxo3BjWKBZORQ',
        api_base_url='https://team09-final.eu.auth0.com',
        access_token_url='https://team09-final.eu.auth0.com/oauth/token',
        authorize_url='https://team09-final.eu.auth0.com/authorize',
        client_kwargs={
        'scope': 'openid profile email',
        },
)


@app.route("/login")
def login():
    return auth0.authorize_redirect(redirect_uri='http://127.0.0.1:5000/callback')

@app.route("/logout")
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {'returnTo': url_for('home', _external=True), 'client_id': '7CwVk5EnKG8UQ9x0ZsksvdJvTDe0BhcZ'}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

# Here we're using the /callback route.
@app.route('/callback')
def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()
    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    print(session['jwt_payload'])
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect('/home')


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in session:
        # Redirect to Login page here
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated


@app.route('/dashboard')
@requires_auth
def dashboard():
        return render_template('dashboard.html',
                               userinfo=session['profile'],
                               userinfo_pretty=json.dumps(session['jwt_payload'], indent=4))



@app.route("/signin")
def signin():
    return render_template("signin.html")

@app.route("/signin_done")
def signin_done():
    uid = request.args.get("id")
    pwd = request.args.get("pwd")
  #  if DB.signin(_id_=uid, pwd=pwd):
  #      return redirect(url_for("home"))
  #  else:
  #      return redirect(url_for("signin"))

@app.route("/")
@app.route("/home")
def home():
    user_name = session.get('profile', None)
    print(user_name)
    #graph = f"/graph_img.jpg"
    #return render_template("Home.html", graph=graph)
    return render_template("Home.html", usern = user_name)

@app.route("/home/graph")
@requires_auth
def graph():
    user_name = session.get('profile', None)
    return render_template("Graph.html", usern = user_name)

@app.route("/home/photo")
@requires_auth
def photo():
    user_name = session.get('profile', None)
    

    return render_template("Photo.html", usern = user_name)
    
@app.route("/home/product")
@requires_auth
def product():
    user_name = session.get('profile', None)
    return render_template("Product.html", usern = user_name)

@app.route("/mypage")
@requires_auth
def mypage():
    user_name = session.get('profile', None)
    test_db = pymysql.connect(user='root', passwd='team09', host='35.180.122.212', db='mydb', charset='utf8')
    cursor = test_db.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT gender FROM user_info where name = '{}'".format(user_name['name'])
    cursor.execute(sql)
    result = cursor.fetchall()
    flag = "False"
    if result:
        flag = "True"
    return render_template("Mypage.html", flag = flag, usern = user_name)

@app.route("/register", methods=["POST"])
def register():
    if request.method == 'POST':
        user = session.get('profile', None)
        res = request.form.to_dict()
        test_db = pymysql.connect(user='root', passwd='team09', host='35.180.122.212', db='mydb', charset='utf8')
        cursor = test_db.cursor(pymysql.cursors.DictCursor)
        sql = "INSERT INTO user_info (user_id, skin_type, age, gender, machine_no, name) VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(user['user_id'],res['skin_type'],res['age'],res['gender'],res['machine_no'],user['name'])
        cursor.execute(sql)
        test_db.commit()
    return redirect("/mypage")



if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
