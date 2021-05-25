from flask import request, flash
from functools import wraps
import json
from os import environ as env
from werkzeug.exceptions import HTTPException
import ed25519
#from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from authlib.integrations.flask_client import OAuth
#from six.moves.urllib.parse import urlencode
import sys
#from DB_handler import DBModule
# import database
app = Flask(__name__)
#DB = DBModule()
app.secret_key = "abcdefg"


auth = OAuth(app)

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


@app.route("/")
def login():
    return render_template("login.html")

@app.route("/login")
def login():
    return auth0.authorize_redirect(redirect_uri='http://15.237.112.4:5000/callback')

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
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect('/dashboard')


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in session:
        # Redirect to Login page here
            return redirect('/')
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

@app.route("/home")
def home():
    #graph = f"/graph_img.jpg"
    #return render_template("Home.html", graph=graph)
    return render_template("Home.html")

@app.route("/home/graph")
def graph():
    return render_template("Graph.html")

@app.route("/home/photo")
def photo():
    return render_template("Photo.html")
    
@app.route("/home/product")
def product():
    return render_template("Product.html")







if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
