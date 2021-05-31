import pymysql
import json

test_db = pymysql.connect(user='root', passwd='team09', host='35.180.122.212', db='mydb', charset='utf8')
cursor = test_db.cursor(pymysql.cursors.DictCursor)
sql = "select face_detail.forehead, face_detail.cheek_R, face_detail.nose, face_detail.philtrum, face_detail.chin, face_detail.cheek_L, user_face.sym_id from face_detail join user_face on face_detail.user_face_id = user_face.user_face_id where user_face.user_id = '{}' and user_face.date = '{}'".format("oauth2|kakao|1750600619","2021-05-30 00:00:00")
cursor.execute(sql)
result = cursor.fetchall()
test_db.close()
print(result)