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
    db = pymysql.connect(user='root', passwd='team09', host='35.180.122.212', db='mydb', charset='utf8')
    sql = "SELECT * FROM face_detail"
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute(sql)
    data = cursor.fetchall()
    return render_template("Graph.html", usern = user_name, graph=json.dumps(data))

@app.route("/home/photo")
@requires_auth
def photo():
    user_name = session.get('profile', None)
    test_db = pymysql.connect(user='root', passwd='team09', host='35.180.122.212', db='mydb', charset='utf8')
    cursor = test_db.cursor(pymysql.cursors.DictCursor)
    sql = "select distinct img_url1, date from user_face where machine_no = '{}' limit 30".format("1000000032965b6f")
    cursor.execute(sql)
    result = cursor.fetchall()
    test_db.close()
    for i in result:
        i['date'] = i['date'].strftime('%Y-%m-%d')
    return render_template("Photo.html", usern = user_name, result=sorted(result, key=lambda r: r['date'], reverse=True))
    
@app.route("/home/product")
@requires_auth
def product():
    user = session.get('profile', None)
    user_id = user['user_id']
    test_db = pymysql.connect(user='root', passwd='team09', host='35.180.122.212', db='mydb', charset='utf8')
    cursor = test_db.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT prod_name, brand, price, img_url, category,gender from product_data join product_result on product_data.product_data_id=product_result.product_data_id where product_result.date = (select MAX(date) from product_result) and product_result.user_id = '{}' order by product_result.product_result_id DESC limit 15".format("oauth2|kakao|1750600619")
    cursor.execute(sql)
    result = cursor.fetchall()
    user_gender = result[0]['gender']
    if user_gender =='f':
        c1, c2, c3 = '스킨/토너','로션/에멀젼','에센스/세럼'
    else:
        c1, c2, c3 = '스킨/로션','에센스/크림','올인원'
    cate1,cate2,cate3 = list(),list(),list()
    for i in range(len(result)):
        if result[i]['category']==c1:
            cate1.append([result[i]['img_url'],result[i]['brand'],result[i]['prod_name'],result[i]['price']])
        elif result[i]['category']==c2:
            cate2.append([result[i]['img_url'],result[i]['brand'],result[i]['prod_name'],result[i]['price']])
        elif result[i]['category']==c3:
            cate3.append([result[i]['img_url'],result[i]['brand'],result[i]['prod_name'],result[i]['price']])
    test_db.close()
    return render_template("Product.html", usern = user, cate1 = cate1, cate2 = cate2, cate3 = cate3)

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
