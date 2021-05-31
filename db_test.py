import json
import datetime
d =datetime.datetime.now().strftime("%Y-%m-%d")
temp = {}
temp[d] = 1
t = json.dumps(temp, ensure_ascii=False)

print(t, type(t))