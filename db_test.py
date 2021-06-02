import pymysql

test_db = pymysql.connect(user='root', passwd='team09', host='35.180.122.212', db='mydb', charset='utf8')
cursor = test_db.cursor(pymysql.cursors.DictCursor)
sql = "select distinct img_url1, date from user_face where machine_no = (select machine_no from user_info where user_id = '{}') limit 30".format("google-oauth2|107217289318141912711")
cursor.execute(sql)
result = cursor.fetchall()


test_db.close()
print(result)