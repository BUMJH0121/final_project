from flask import Flask, render_template, request, jsonify
import requests
import pymysql
import time
#from scripts.weather import get_weather

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/update_weather', methods=['GET'])
def update_weather():
	'''
	Returns updated weather, called every 10 minutes
	'''
	#currentWeather = get_weather()
	return jsonify({'result' : 'success', 'currentWeather' : currentWeather})

@app.route("/result/<serialnum>/<date>", methods=['POST', 'GET'])
def result(serialnum, date):
    user_conf = {}
    user_conf['serialnum'] = serialnum
    user_conf['date'] = date
    if request.method == 'POST':
        sql = "SELECT * FROM user_face  where machine_no = '{}' and date ='{}'".format(serialnum, date)
        rows = []
        while True:
            test_db = pymysql.connect(user='root', passwd='team09', host='35.180.122.212', port=3306, db='mydb', charset='UTF8')
            cursor = test_db.cursor(pymysql.cursors.DictCursor)
            cursor.execute("set names utf8")
            cursor.execute(sql)
            rows = cursor.fetchall()
            test_db.close()
            if rows:
                break
            time.sleep(5)
            print("not exist data")
        print("DONE")
        return rows[0]
    return render_template("loading.html", data = user_conf)

@app.route("/findmachine/<machine_no>")
def findmachine(machine_no):
    flag = "기기 등록이 필요합니다."
    test_db = pymysql.connect(user='root', passwd='team09', host='35.180.122.212', port=3306, db='mydb', charset='UTF8')
    cursor = test_db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT name from user_info where machine_no = {}".format(machine_no))
    machine = cursor.fetchall()
    test_db.close()
    if machine:
        flag = ""
    return flag


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host="0.0.0.0",port=5000, debug=True)
