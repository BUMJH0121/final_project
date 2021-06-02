from flask import Flask, request
import json
import os

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'HI'


@app.route('/picture/<serialnum>/<date>', methods=['POST'])
def picture(serialnum, date):
    data = json.loads(request.get_data(), encoding='utf-8')
    print(data['url'])
    os.system("/AI/ai.sh {} {} {}".format(serialnum, data['url'], date))
    return "200"

@app.route('/healthy')
def healthy():
    return "200"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
