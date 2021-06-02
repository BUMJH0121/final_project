from flask import Flask, request
import json
import requests
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "HI bigdata"


@app.route('/picture/<serialnum>/<date>', methods=['POST'])
def picture(serialnum, date):
    data = json.loads(request.get_data(), encoding='utf-8')
    print(data['url'])
    os.chdir("../bigdata")
    with open("user_data.json", "w", encoding="utf-8") as make_file:
        json.dump(data ,make_file)
    os.system("python user_process.py")
    return "200"

@app.route('/result/<serialnum>/<date>')
def result(serialnum, date):
    try:
        with open("../bigdata/data.json", "r", encoding="utf-8") as f:
            result_data = json.load(f)
            result = json.dumps(result_data, ensure_ascii=False)
            return result
    except:
        return "Not yet"

@app.route('/remove')
def remove():
    os.chdir("../bigdata")
    os.system("rm data.json")
    os.system("rm data_m.json")
    os.system("rm user_data.json")
    return "200"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
