#!/usr/bin/env python
# coding: utf-8

# In[1]:


import math
import numpy as np
import pandas as pd
import sys
import pymysql
# In[2]:


from scipy.spatial.distance import cosine

# In[3]:


import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import seaborn as sns

# In[204]:


from matplotlib import font_manager, rc
import sys

#if sys.platform in ["win32", "win64"]:
#    font_name = "malgun gothic"
#elif sys.platform == "darwin":
#    font_name = "AppleGothic"

#rc('font',family=font_name)

# # 1. 데이터 전처리

# In[4]:


glowpick = pd.read_csv('glowpick.csv')

# In[5]:


glowpick.head()

# ### 사용자 관련 feature만 남기기

# In[6]:


glow_df = glowpick[['user_id','age','skin_type','gender']]

# In[7]:


glow_df.head()

# ### skin_type, gender -> one_hot encoding

# In[8]:


skin_df = pd.get_dummies(glow_df['skin_type'], prefix = 'skin_type')
gender_df = pd.get_dummies(glow_df['gender'],prefix='gender')

# In[9]:


glow_df = pd.concat([glow_df,skin_df,gender_df],axis=1)
glow_df.head()

# In[10]:


glow_df

# In[11]:


glow_df.drop(['skin_type','gender'],axis=1,inplace=True)

# In[12]:


glow_df.head()

# ### -중복 행 제거

# In[13]:


glow_df = glow_df.drop_duplicates()

# In[14]:


glow_df.reset_index(inplace=True, drop=True)
glow_df

# In[15]:


glow_matrix = glow_df.copy()

# In[16]:


del glow_matrix['user_id']

# In[ ]:




# ### - 데이터 표준화 

# In[17]:


from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
scaled_values = scaler.fit_transform(glow_matrix)
glow_matrix.loc[:,:] = scaled_values

# In[18]:


glow_matrix.head()

# In[19]:


glow_matrix = glow_matrix.to_numpy()
glow_matrix

# # 2.사용자 속성을 기반으로  코사인유사도 구하기

# In[20]:


from sklearn.metrics.pairwise import cosine_similarity

# In[21]:


# 새로운 데이터 입력
new_data=[0.27118644, 0, 1, 0, 0,0,1, 0]

# In[22]:


new_data = np.array(new_data).reshape(-1,1)

# In[23]:


new_data.shape

# In[101]:


cos_sim = cosine_similarity(glow_matrix, new_data.reshape(1,-1))
cos_sim

# In[102]:


similar_user_idx = np.argsort(cos_sim.transpose()[0])[::-1][:10]
similar_user_idx = similar_user_idx.tolist()
similar_user_idx

# In[103]:


similar_user_id_df = glow_df.iloc[similar_user_idx,]
similar_user_id_list = similar_user_id_df[['user_id']] 
similar_user_id_list= similar_user_id_list.values.reshape(1,-1).tolist()[0]

# In[104]:


similar_user_id_list

# # 3. 사용자 기반 협업필터링

# In[105]:


user_prod = glowpick.pivot_table('score', index='user_id', columns='prod_name')
user_prod.fillna(0, inplace=True)
user_prod

# In[106]:


# 유저와 유저 간의 유사도
user_based_collab = cosine_similarity(user_prod, user_prod)
user_based_collab = pd.DataFrame(user_based_collab, index=user_prod.index, columns=user_prod.index)
user_based_collab

# In[107]:


# 코사인 유사도 가장 높은 유저 15명이 평가한 제품

# In[110]:


import re

# In[114]:


idx_list_1 = []

# In[115]:


for u_id in similar_user_id_list:
    idx = re.search('[\d ,]+',str(glowpick[glowpick['user_id']==u_id].index).split('[')[1]).group()
    idx_list_1.extend(idx.split(', '))


# In[140]:


idx_list_1 = list(map(int, idx_list_1))
print(idx_list_1)

# In[142]:


user1_df = glowpick.iloc[idx_list_1,]
user1_df.head()

# In[ ]:




# In[ ]:


# 코사인 유사도 높은 유저와 비슷한 유저 30명이 평가한 제품

# In[150]:


user_collab_id = []

# In[161]:


for u_id in similar_user_id_list:
    user_collab_id.extend(user_based_collab[u_id].sort_values(ascending=False)[:11].index.tolist())

# In[162]:


idx_list_2 =[]

# In[163]:


for u_id in user_collab_id:
    idx = re.search('[\d ,]+',str(glowpick[glowpick['user_id']==u_id].index).split('[')[1]).group()
    idx_list_2.extend(idx.split(', '))

# In[164]:


idx_list_2 = list(map(int, idx_list_2))

# In[165]:


user2_df = glowpick.iloc[idx_list_2,]
user2_df.head()

# In[170]:


user2_df.head(15)

# In[171]:


user1_df.head()

# In[172]:


collab_filter = pd.concat([user1_df,user2_df])

# In[179]:


collab_filter.reset_index(inplace=True,drop=True)
collab_filter.head()

# In[180]:


collab_filter = collab_filter.drop_duplicates()
collab_filter.shape

# In[199]:


# 제품별 score count
collab_filter.pivot_table('user_id',index='prod_name', columns='score',aggfunc='count').fillna(0)

# In[ ]:


#sns.heatmap(tip2, cmap='Blues', annot=True) 
#plt.show()

# In[206]:


count_df = collab_filter.pivot_table('user_id',index='prod_name', columns='score',aggfunc='count').fillna(0)

# In[207]:


#sns.heatmap(count_df, cmap='Blues', annot=True) 
#plt.show()

# In[210]:


# 제품별 score count
mean_df = collab_filter.pivot_table('score',index='brand_name',aggfunc='mean').fillna(0)


# In[194]:


top5 =collab_filter.groupby('prod_name')[['score']].mean().sort_values(ascending=False,by='score')
reco = top5[:5]

# In[ ]:

test_db = pymysql.connect(user='root', passwd='', host='35.180.122.212', port=3306, db='DB', charset='utf8')
cursor = test_db.cursor()
sql = "INSERT INTO test (machine, url, date, data) VALUES ('{}', '{}', '{}', '{}')".format(sys.argv[1], sys.argv[2], sys.argv[3].split('.')[0], reco)
print(sql)
cursor.execute(sql)
test_db.commit()
test_db.close()
