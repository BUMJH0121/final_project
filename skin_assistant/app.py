from flask import request
from functools import wraps
import json
from os import environ as env
from werkzeug.exceptions import HTTPException
import pandas as pd
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
    user_id = user_name['user_id']
    
    dbconn = pymysql.connect(
    host='35.180.122.212',
    port=3306, user = 'root',
    password = 'team09',
    db = 'mydb',
    charset='utf8'
    )
    cursor = dbconn.cursor(pymysql.cursors.DictCursor)
    
    # 증상, 원인에 대한 sql
    sql = "SELECT distinct user_face.date, prescription_data.sym_id, prescription_data.sym_name,prescription_data.symptom, prescription_data.cause, prescription_data.caution, prescription_data.solution FROM prescription_data JOIN user_face WHERE user_face.date = (select MAX(date) from user_face) and user_face.sym_id = prescription_data.sym_id  limit 3" 
    cursor.execute(sql)
    result = cursor.fetchall()
    # 이미지 위 증상별 부위 개수 sql
    sqls = "SELECT distinct  face_detail.forehead, face_detail.cheek_R, face_detail.nose, face_detail.philtrum, face_detail.chin, face_detail.cheek_L, user_face.sym_id FROM face_detail JOIN user_face WHERE user_face.date = (select MAX(date) from user_face) and user_face.user_face_id = face_detail.user_face_id  limit 1" 
    cursor.execute(sqls)
    results = cursor.fetchall()
    find = [0, 0, 0, 0, 0]
    t_forehead = 0
    t_nose = 0
    t_cheekl = 0
    t_cheekr = 0
    t_chin = 0
    for t in results:
        if t['sym_id'] == 1:
            find[0] = 1
        elif t['sym_id'] == 2:
            find[1] = 1
            t_forehead = t_forehead + t['forehead']
            t_nose = t_nose + t['nose']
            t_cheekl = t_cheekl + t['cheek_L']
            t_cheekr = t_cheekr + t['cheek_R']
            t_chin = t_chin + t['chin']
        elif t['sym_id'] == 3:
            find[2] = 1
            t_forehead = t_forehead + t['forehead']
            t_nose = t_nose + t['nose']
            t_cheekl = t_cheekl + t['cheek_L']
            t_cheekr = t_cheekr + t['cheek_R']
            t_chin = t_chin + t['chin'] 
        elif t['sym_id'] == 4:
            find[3] = 1
        elif t['sym_id'] == 5:
            find[4] = 1
    sql1 = "select distinct date from user_face ORDER BY date DESC limit 30;"
    sql2 = "select sym_id, date from user_face ORDER BY date DESC;"
    cursor.execute(sql1)
    date = cursor.fetchall()
    cursor.execute(sql2)
    sym = cursor.fetchall()

    darkcircle = dict()
    freckle = dict()

    for day in date:
        for i in sym:
            if i['date']==day['date']:
                if i['sym_id']==4:
                    freckle[day['date'].strftime('%Y-%m-%d')]=1
                    break
                else:
                    freckle[day['date'].strftime('%Y-%m-%d')]=0

    for day in date:
        for i in sym:
            if i['date']==day['date']:
                if i['sym_id']==5:
                    darkcircle[day['date'].strftime('%Y-%m-%d')]=1
                    break
                else:
                    darkcircle[day['date'].strftime('%Y-%m-%d')]=0

    recent_30days = list()
    for i in date:
        day = i['date'].strftime('%Y-%m-%d')
        recent_30days.append(day)

    sql = "SELECT user_face.user_face_id, sym_id, date, forehead, cheek_R, cheek_L, nose, philtrum, chin FROM user_face left JOIN face_detail ON user_face.user_face_id=face_detail.user_face_id Where user_id=%s"  # 생성
    row_count = cursor.execute(sql, (user_id))  # 변수명 맞춰줘야 함
    if row_count > 0:  # select된 결과가 있으면
        user_info = cursor.fetchall()  # row 객체 가져오기
        print('user_info: ', user_info)
    else:
        print('User does not exist')

    data = pd.DataFrame(user_info)

    data['sum'] = data['forehead'] + data['cheek_R'] + data['nose'] + data['philtrum'] + data['chin'] + data['cheek_L']


    # 최근 일주일 데이터 가져오기
    from datetime import date, timedelta as td
    x = date.today()
    y = date.today() - td(6)

    filtered_df = data.loc[data["date"].between(y, x)]

    week = []
    delta = x - y

    for i in range(delta.days + 1):
        week.append((x - td(days=i)).strftime("%Y-%m-%d"))

    filtered_df.drop(columns=['cheek_L', 'cheek_R', 'chin', 'nose', 'philtrum', 'forehead'], inplace=True)

    code2_df = filtered_df[filtered_df['sym_id'] == 2]
    code3_df = filtered_df[filtered_df['sym_id'] == 3]

    code2_df.drop(columns=['sym_id', 'user_face_id'], inplace=True)
    code3_df.drop(columns=['sym_id', 'user_face_id'], inplace=True)

    code2_df['date'] = code2_df['date'].astype(str)
    code3_df['date'] = code3_df['date'].astype(str)

    new2 = code2_df['date'].tolist()
    new3 = code3_df['date'].tolist()
    for day in week:
        if (day in new2):
            pass
        else:
            temp = {'date': [day],
                    'sum': [0]}
            temp2 = pd.DataFrame(temp)
            code2_df = pd.concat([code2_df, temp2])

    for day in week:
        if (day in new3):
            pass
        else:
            temp = {'date': [day],
                    'sum': [0]}
            temp2 = pd.DataFrame(temp)
            code3_df = pd.concat([code3_df, temp2])

    day2 = []
    value2 = []
    value3 = []

    code2_df = code2_df.sort_values('date')
    code3_df = code3_df.sort_values('date')

    day2 = [day for day in code2_df['date']]
    value2 = [value for value in code2_df['sum']]
    value3 = [value for value in code3_df['sum']]
    ################## 일주일 끝 ##############################
    ## 한달 시작#

    x = date.today()
    y = date.today() - td(30)

    filtered_df = data.loc[data["date"].between(y, x)]

    week = []
    delta = x - y

    for i in range(delta.days + 1):
        week.append((x - td(days=i)).strftime("%Y-%m-%d"))

    filtered_df.drop(columns=['cheek_L', 'cheek_R', 'chin', 'nose', 'philtrum', 'forehead'], inplace=True)

    code4_df = filtered_df[filtered_df['sym_id'] == 2]
    code5_df = filtered_df[filtered_df['sym_id'] == 3]

    code4_df.drop(columns=['sym_id', 'user_face_id'], inplace=True)
    code5_df.drop(columns=['sym_id', 'user_face_id'], inplace=True)

    code4_df['date'] = code4_df['date'].astype(str)
    code5_df['date'] = code5_df['date'].astype(str)

    new4 = code4_df['date'].tolist()
    new5 = code5_df['date'].tolist()
    for day in week:
        if (day in new4):
            pass
        else:
            temp = {'date': [day],
                    'sum': [0]}
            temp2 = pd.DataFrame(temp)
            code4_df = pd.concat([code4_df, temp2])

    for day in week:
        if (day in new5):
            pass
        else:
            temp = {'date': [day],
                    'sum': [0]}
            temp2 = pd.DataFrame(temp)
            code5_df = pd.concat([code5_df, temp2])

    day4 = []
    value4 = []
    value5 = []

    code4_df = code4_df.sort_values('date')
    code5_df = code5_df.sort_values('date')

    day4 = [day for day in code4_df['date']]
    value4 = [value for value in code4_df['sum']]
    value5 = [value for value in code5_df['sum']]
    return render_template("Graph.html", usern = user_name, **locals())

@app.route("/home/photo")
@requires_auth
def photo():
    user_name = session.get('profile', None)
    user_id = user_name['user_id']
    test_db = pymysql.connect(user='root', passwd='team09', host='35.180.122.212', db='mydb', charset='utf8')
    cursor = test_db.cursor(pymysql.cursors.DictCursor)
    sql = "select distinct img_url1, date from user_face where machine_no = (select machine_no from user_info where user_id = '{}') limit 30".format(user_id)
    cursor.execute(sql)
    result = cursor.fetchall()
    test_db.close()
    for i in result:
        i['date'] = i['date'].strftime('%Y-%m-%d')
    length = min(9, len(result))
    return render_template("Photo.html", usern = user_name, length=length, result=sorted(result, key=lambda r: r['date'], reverse=True))
    
@app.route("/home/product")
@requires_auth
def product():
    user = session.get('profile', None)
    user_id = user['user_id']
    test_db = pymysql.connect(user='root', passwd='team09', host='35.180.122.212', db='mydb', charset='utf8')
    cursor = test_db.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT prod_name, brand, price, img_url, category,gender from product_data join product_result on product_data.product_data_id=product_result.product_data_id where product_result.date = (select MAX(date) from product_result) and product_result.user_id = '{}' order by product_result.product_result_id DESC limit 15".format(user_id)
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
    return render_template("Product.html", usern = user, cate1 = cate1, cate2 = cate2, cate3 = cate3, c1=c1, c2=c2, c3=c3)

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
