from flask import Flask, render_template, request, jsonify
import requests

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

@app.route('/result/<serial>/<date>')
def result(serial, date):
    return f'myserial:{serial}, today is {date}'

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host="192.168.35.106",port=5000, debug=True)