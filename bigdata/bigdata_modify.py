#!/usr/bin/env python
# coding: utf-8

# In[1]:


# 유저 프로세스 부분 코드
# 1. json 형태로 받은 정보를 user_info와 결합하여 user_face 생성
# 2. 사용자 속성을 기반으로 코사인 유사도 
# 3. 사용자 협업 필터링
# 4. 나온 결과를 다시 DB에 저장


# In[73]:


import math
import numpy as np
import pandas as pd


# In[74]:


from scipy.spatial.distance import cosine


# In[75]:


import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import seaborn as sns


# In[76]:


from sklearn.decomposition import TruncatedSVD
from scipy.sparse.linalg import svds


# In[77]:


import pymysql
from sqlalchemy import create_engine

# MySQL Connector using pymysql
# mysql.install_as_MySQLdb()
import MySQLdb


# ## 사진을 찍은 사용자의 데이터가 들어오게 됨

# In[106]:


# lambda로 받은 데이터를 df로 만듬
import json
with open("user_data.json", "r") as st_json:
    data = json.load(st_json)
data = pd.DataFrame(data.items(), columns=['data','freq'])

# machine 번호를 받음
for i in range(len(data)) :
    if (data.loc[i][0] == 'serialnum') :
        machine = data.loc[i][1]
print(machine)

# In[107]:


#data = pd.read_csv('jsonex.csv', engine='python')
# machine 번호를 받음
#for i in range(len(data)) :
#    if (data.loc[i][0] == 'serialnum') :
#        machine = data.loc[i][1]


# In[108]:


# In[109]:


db = pymysql.connect(
    host = '35.180.122.212', 
    port=3306, user = 'root',
    password='team09',
    db = 'mydb',
    charset='utf8'
)

SQL = "SELECT sym_id, sym_name FROM prescription_data"
sym_info = pd.read_sql(SQL,db)
SQL = """SELECT user_id FROM user_info WHERE machine_no = """+str(machine)+""""""
user_info = pd.read_sql(SQL,db)
db.close()
print(user_info)
# 진단할 수 있는 sym의 종류
sym_list = sym_info['sym_name'][1:]


# In[110]:


cnt = 1
final_df = pd.DataFrame()
final_df2 = pd.DataFrame()
have_sym = []

engine = create_engine("mysql://root:"+"team09"+"@35.180.122.212:3306/mydb?charset=utf8", encoding='utf8')
conn = engine.connect()
for sym in sym_list :
    # 증상 횟수 만큼 반복하게 됨
    # temp 초기화
    temp = {}
    temp2 = {}
    cnt += 1
    
    # count의 경우 여드름만 갯수이고 나머지는 유무이므로
    # 다른 케이스로 취급함
    if (sym == '구진성여드름') :
        count = (int(data.iloc[0]['freq']) + int(data.iloc[2]['freq']) + int(data.iloc[4]['freq']) + int(data.iloc[6]['freq'])
                    + int(data.iloc[8]['freq']) + int(data.iloc[10]['freq']))
        temp2 = {
            'forehead' : [data.iloc[0]['freq']],
            'cheek_R' : [data.iloc[2]['freq']],
            'cheek_L' : [data.iloc[4]['freq']],
            'nose' : [data.iloc[6]['freq']],
            'philtrum' : [data.iloc[8]['freq']],
            'chin' : [data.iloc[10]['freq']]
        }
    elif (sym == '농포성여드름') :
        count = (int(data.iloc[1]['freq']) + int(data.iloc[3]['freq']) + int(data.iloc[5]['freq']) + int(data.iloc[7]['freq'])
                    + int(data.iloc[9]['freq']) + int(data.iloc[11]['freq']))
        temp2 = {
            'forehead' : [data.iloc[1]['freq']],
            'cheek_R' : [data.iloc[3]['freq']],
            'cheek_L' : [data.iloc[5]['freq']],
            'nose' : [data.iloc[7]['freq']],
            'philtrum' : [data.iloc[9]['freq']],
            'chin' : [data.iloc[11]['freq']]
        }
    elif (sym == '기미'):
        count = data.iloc[12:17]['freq'].sum()
        temp2 = {
            'forehead' : [data.iloc[12]['freq']],
            'cheek_R' : [data.iloc[13]['freq']],
            'cheek_L' : [data.iloc[14]['freq']],
            'nose' : [data.iloc[15]['freq']],
            'philtrum' : [data.iloc[16]['freq']],
            'chin' : [data.iloc[17]['freq']]
        }
    elif (sym =='다크서클') :
        count = int(data.iloc[-4][1])

    temp = {
        'user_id' : [user_info['user_id'][0]],
        'sym_id' : [cnt],
        'date' : [data.iloc[-1][1]],
        'machine_no' : [data.iloc[-2][1]],
        'img_url1' : [data.iloc[-3][1]],
    }
    temp = pd.DataFrame(temp)
    temp2 = pd.DataFrame(temp2)
    # 만약 검출이 되지 않았다면 DB에 넣지 않게 하기 위해
    if(count == 0) :
        continue
    # 최종 user 정보를 user_face에 입력
    temp.to_sql(name='user_face',con=engine, if_exists='append', index=False)

    db = pymysql.connect(
        host = '35.180.122.212', 
        port=3306, user = 'root',
        password='team09',
        db = 'mydb',
        charset='utf8'
    )

    SQL = """SELECT MAX(user_face_id) FROM user_face """
    user_face_id = pd.read_sql(SQL,db)
    db.close()
    
    have_sym.append(sym)
    # user_face_id.iloc[0][0] 해당하는 id는 단 하나만 존재함
    if(sym =='다크서클') :
        continue
    id_info = {'user_face_id' : [user_face_id.iloc[0][0]]}
    id_info = pd.DataFrame(id_info)
    temp2 = pd.concat([temp2,id_info], axis=1)
    temp2.to_sql(name='face_detail',con=engine, if_exists='append', index=False)
    
if (have_sym == []) :
    temp = {
        'user_id' : [user_info['user_id'][0]],
        'sym_id' : [1],
        'date' : [data.iloc[-1][1]],
        'machine_no' : [data.iloc[-2][1]],
        'img_url1' : [data.iloc[-3][1]],
    }
    temp = pd.DataFrame(temp)
    temp.to_sql(name='user_face',con=engine, if_exists='append', index=False)


# # 1. 데이터 전처리 - 스킨, 로션, 에센스 분리

# In[111]:


db = pymysql.connect(
    host = '35.180.122.212', 
    port=3306, user = 'root',
    password = 'team09',
    db = 'mydb',
    charset='utf8'
)

# 크롤링 데이터 가져오기
sql = 'SELECT * FROM product_data'
female = pd.read_sql(sql,db)

db.close()


# # 2. 사용자 관련 df 생성

# In[112]:


def make_user_df(df):
    df =df[['user_id','age','skin_type','acne','dark_circle','freckle']]
    
    #범주형 데이터 더미변수로 변환
    skintype_df = pd.get_dummies(df['skin_type'], prefix = 'skin_type')
    age_df = pd.get_dummies(df['age'],prefix='age')
    df = pd.concat([df,skintype_df,age_df],axis=1) 
    df.drop(['skin_type','age'],axis=1,inplace=True) # 더미 변환 이전 데이터 삭제
    
    #사용자 중복 데이터 제거
    df = df.drop_duplicates()
    df.reset_index(inplace=True,drop=True)
    df2 = df.copy()
    #del df2['user_id']
    
    return df


# In[113]:


user_df = make_user_df(female)


# # 3.사용자 속성을 기반으로  코사인유사도 구하기

# In[114]:


from sklearn.metrics.pairwise import cosine_similarity


# ### 여기서 사진 찍은 사용자의 데이터가 들어오게됨

# In[115]:


db = pymysql.connect(
    host = '35.180.122.212', 
    port=3306, user = 'root',
    db = 'mydb',
    password = 'team09',
    charset='utf8'
)
user_info=[]
# user_info와 user_face를 가지고 와서 유저 기본 정보 생성
# 오늘 사진에 대한 acne / dark_circle / freckle 을 위한 df를 제작하여 concat 해야됨
# 현재 id_list에는 증상이 있는 symptom의 id이기 때문에 존재 하지 않으면 증상도 없음 
# date나 img_url로 이용을 해야 될거 같음
# machine_no 끼리의 비교
# sql =  """
#         SELECT user_face.user_id, age, skin_type 
#         FROM user_info 
#         JOIN user_face WHERE user_face.img_url1 = '"""+str(data.iloc[-3][1])+"""'
#        """
sql = """
    SELECT user_info.user_id, age, skin_type
    FROM user_info JOIN user_face
    WHERE user_info.machine_no = '"""+str(machine)+"""'"""
user_info = pd.read_sql(sql,db)
db.close()

user_info = pd.DataFrame(user_info.loc[0]).T
user_info['acne'] = 0
user_info['dark_circle'] = 0
user_info['freckle'] = 0
for sym in have_sym :
    if(sym == '구진성여드름') :
        user_info['acne'] = 1
    elif(sym == '농포성여드름') :
        user_info['acne'] = 1
    elif(sym == '기미') :
        user_info['freckle'] = 1
    elif(sym =='다크서클') :
        user_info['dark_circle'] = 1


# In[116]:


# user_info가 원하는 사용자의 데이터가 됨 
# 이걸 one-hot encoding을 통해 matrix화 시키면 됨
user_info


# In[117]:


user_info['age'] = user_info['age'].astype(int)


# In[118]:


user_info['age_cut']=''


# In[119]:


if user_info['age'][0]<20:
    user_info['age_cut'][0]='10s'
    
elif user_info['age'][0]>=20 and user_info['age'][0]<25:
    user_info['age_cut'][0]='20s_early'
    
elif user_info['age'][0]>=25 and user_info['age'][0]<30:
    user_info['age_cut'][0]='20s_late'
    
elif user_info['age'][0]>=30 and user_info['age'][0]<35:
    user_info['age_cut'][0]='30s_early'
    
elif user_info['age'][0]>=35 and user_info['age'][0]<40:
    user_info['age_cut'][0]='30s_late'
    
elif user_info['age'][0]>=40 and user_info['age'][0]<45:
    user_info['age_cut'][0]='40s_early'

elif user_info['age'][0]>=45 and user_info['age'][0]<50:
    user_info['age_cut'][0]='40s_late'
    
elif user_info['age'][0]>=50:
    user_info['age_cut'][0]='50s'


# In[120]:


user_info


# In[121]:


age_X = pd.get_dummies(user_info['age_cut'],prefix='age')
skin_X = pd.get_dummies(user_info['skin_type'],prefix='skin_type')
new_data = pd.concat([user_info,skin_X,age_X],axis=1)


# In[122]:


new_data.drop(columns=['age','skin_type','age_cut'],inplace=True)


# In[123]:


new_data


# In[124]:


user_with_newdata = user_df.append(new_data).fillna(0)
user_with_newdata 


# In[125]:


del user_with_newdata['user_id']


# ## StandardScaler

# In[126]:


from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()


# In[127]:


scaled_values = scaler.fit_transform(user_with_newdata)
user_with_newdata.loc[:,:] = scaled_values
user_matrix =user_with_newdata.to_numpy()


# In[128]:


# 사용자 데이터 입력 -예시) 여드름, 다크서클, 건성, 20대초반
new_data=user_matrix[-1]
len(new_data)


# In[129]:


#new_data = np.array(new_data).reshape(-1,1)


# In[130]:


#new_data.shape


# In[131]:


user_matrix = np.delete(user_matrix,-1,0)


# In[132]:


cos_sim = cosine_similarity(user_matrix, new_data.reshape(1,-1))
cos_sim


# In[133]:


cos_sim_list = cos_sim.transpose().tolist()[0]


# In[134]:


cos_sim_list.sort()
cos_sim_list.reverse()


# In[135]:


similar_user_idx = np.argsort(cos_sim.transpose()[0])[::-1][:30]
similar_user_idx = similar_user_idx.tolist()


# In[136]:


similar_user_id_df = user_df.iloc[similar_user_idx,]
similar_user_id_list = similar_user_id_df[['user_id']] 
similar_user_id_list= similar_user_id_list.values.reshape(1,-1).tolist()[0]


# In[137]:


similar_user_id_list


# In[138]:


import re


# In[139]:


idx_list_1=[]
for u_id in similar_user_id_list:
    idx = re.search('[\d ,]+',str(female[female['user_id']==u_id].index).split('[')[1]).group()
    idx_list_1.extend(idx.split(', '))


# # 4. 잠재요인 협업필터링

# In[140]:


user_prod = female.pivot_table('score', index='user_id', columns='prod_name',aggfunc='mean')
user_prod.fillna(0, inplace=True)
user_prod


# In[141]:


user_id_df = pd.DataFrame(user_prod.index)
user_id_idx_df = pd.DataFrame([i for i in range(len(user_id_df))],columns=['idx'])
user_idx_df = pd.concat([user_id_idx_df, user_id_df],axis=1)
user_idx_df


# In[142]:


# matrix는 pivot_table 값을 numpy matrix로 만든 것 
matrix = user_prod.values


# In[143]:


# user_ratings_mean은 사용자의 평균 평점 
user_ratings_mean = np.mean(matrix, axis = 1)


# In[144]:


# R_user_mean : 사용자-아이템에 대해 사용자 평균 평점을 뺀 것.
matrix_user_mean = matrix - user_ratings_mean.reshape(-1, 1)


# In[145]:


pd.DataFrame(matrix_user_mean, columns = user_prod.columns).head()


# In[146]:


# scipy에서 제공해주는 svd.  
# U 행렬, sigma 행렬, V 전치 행렬을 반환.

U, sigma, Vt = svds(matrix_user_mean, k = 24)


# In[147]:


print(U.shape)
print(sigma.shape)
print(Vt.shape)


# In[148]:


sigma = np.diag(sigma)
sigma.shape


# In[149]:


# U, Sigma, Vt의 내적을 수행하면, 다시 원본 행렬로 복원이 된다. 
# 거기에 + 사용자 평균 rating을 적용한다. 
svd_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_ratings_mean.reshape(-1, 1)


# In[150]:


df_svd_preds = pd.DataFrame(svd_user_predicted_ratings, columns = user_prod.columns)
df_svd_preds.head()


# In[151]:


df_svd_preds.shape


# In[152]:


def recommend_items(df_svd_preds, user_id, ori_df, num_recommendations=10):
    
    #현재는 index로 적용이 되어있으므로 user_id - 1을 해야함.
    user_row_number = user_idx_df[user_idx_df.user_id ==user_id].index[0]
    
    # 최종적으로 만든 pred_df에서 사용자 index에 따라 제품 데이터 정렬 -> 제품 평점이 높은 순으로 정렬 됌
    sorted_user_predictions = df_svd_preds.iloc[user_row_number].sort_values(ascending=False)

    recommendations = ori_df
    
    # 사용자의 제품 평점이 높은 순으로 정렬된 데이터와 위 recommendations을 합친다. 
    recommendations = recommendations.merge(pd.DataFrame(sorted_user_predictions).reset_index(), on = 'prod_name')
    
    #상품 추천을 위한 중복 제품 삭제
    recommendations.drop(['user_id','score','age','skin_type','website','acne','freckle','dark_circle','product_data_id'],axis=1,inplace=True)
    recommendations.drop_duplicates(inplace=True)

    # 컬럼 이름 바꾸고 정렬해서 return
    recommendations = recommendations.rename(columns = {user_row_number: 'Predictions'}).sort_values('Predictions', ascending = False).iloc[:num_recommendations, :]
                      

    return recommendations


# In[153]:


#사용자와 유사한 user가 추천받을 제품 목록
result_df = recommend_items(df_svd_preds, similar_user_id_list[0], female, 30)
for i in range(1,len(similar_user_id_list)):
    predictions = recommend_items(df_svd_preds, similar_user_id_list[i], female, 30)
    result_df = pd.concat([result_df,predictions])


# In[154]:


result_df


# In[155]:


def recommend_each_category(df,category,num=5):
    category_df = df[df['category']==category].sort_values(by='Predictions',ascending=False)
    del category_df['Predictions']
    category_df.drop_duplicates(inplace=True)
    #category_df.reset_index(drop=True,inplace=True)
    return category_df.head(num)


# In[156]:


recommend1 = recommend_each_category(result_df,'스킨/토너')


# In[157]:


recommend2 = recommend_each_category(result_df,'로션/에멀젼')


# In[158]:


recommend3 = recommend_each_category(result_df,'에센스/세럼')


# In[159]:


final_recommend = pd.DataFrame()
final_recommend = pd.concat([final_recommend,recommend1])
final_recommend = pd.concat([final_recommend,recommend2])
final_recommend = pd.concat([final_recommend,recommend3])


# In[160]:


final_recommend['product_data_id'] = final_recommend.index


# In[161]:


# product_data_id 컬럼을 저장하기 위해 index 추가
final_index = final_recommend.index+1
final_index_list = final_index.tolist()
final_recommend['product_data_id'] = final_index_list
final_recommend.reset_index(inplace=True, drop=True)
final_recommend


# In[171]:


## 나온 결과를 INSERT할 부분임
# 3개를 합치고 datetime을 추가해서 넣어버리기
# 사진정보의 user_id / product_data_id(prod_name) / date

engine = create_engine("mysql://root:"+"team09"+"@35.180.122.212:3306/mydb?charset=utf8", encoding='utf8')
conn = engine.connect()
final_recommend = final_recommend[['product_data_id']]
final_recommend['user_id'] = user_info['user_id'][0]
final_recommend['date'] = data.iloc[-1][1]
final_recommend.to_sql(name='product_result',con=engine, if_exists='append', index=False)

