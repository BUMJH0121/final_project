from logging import debug
from flask import Flask, render_template, request, jsonify
# from flask_mqtt import Mqtt
import requests
import json
import time

from scripts.weather import get_weather
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
    currentWeather = get_weather()
    return jsonify({'result' : 'success', 'currentWeather' : currentWeather})

@app.route("/result/<serialnum>/<date>", methods=['POST', 'GET'])
def result(serialnum, date):
    user_conf = {}
    user_conf['serialnum'] = serialnum
    user_conf['date'] = date
    results = []
    if request.method == 'POST':
        while True:
            res = requests.get("http://15.236.41.37:5000/result/{}/{}".format(serialnum, date))
            if res.text != "Not yet":
                requests.get("http://15.236.41.37:5000/remove")
                results = json.loads(res.text)
                break
        data = {}
        for i in range(4):
            data[results[i]['item']] = {
            'num':results[i]['element1'],
            'pre':results[i]['element2'].split(',')
        }
        return render_template('resultspage1.html', data=data, results=json.dumps(results, ensure_ascii=False))
    return render_template("loading.html", data = user_conf)

@app.route('/recommend', methods=['POST'])
def recommend_result():
    res = request.form['data']
    result = json.loads(res)
    results = json.loads(result)
    if results[-1]['item'] == 'all_in_one':
        gender = 'm'
    else:
        gender = 'f'
    data={}
    for i in range(4,len(results)):
        data[results[i]['item']] = {
            'imgurl':results[i]['element1'],
            'price':results[i]['element2'],
            'name':results[i]['element3'],
        }
    return render_template('resultspage2.html', data=data, gender=gender)

if __name__ == '__main__':
    # app.run(debug=True)
	app.run(host="0.0.0.0",port=5000, debug=True)
