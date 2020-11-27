from flask import Flask, render_template, url_for, request, jsonify
import pandas as pd
import numpy as np
import math
# import pandas as pd
from surprise import Dataset
import sys
import pymysql

from surprise import Reader
from surprise import SVDpp
from surprise.model_selection import train_test_split
from collections import defaultdict

top_n = defaultdict(list)

app = Flask(__name__)

# db 접속


def get_connection():
    conn = pymysql.connect(host='petmeeting.cvsejgvxoucu.us-east-2.rds.amazonaws.com',
                           user='admin', password='petmeeting123', db='petmeeting', charset='utf8')
    return conn

# {pet_id, user_id, Rating} 형식으로, 모든 평가 데이터를 가져온다.


def get_default_ratings():

    conn = get_connection()

    sql = '''
		SELECT k.PID, v.UID, v.Score FROM 
		(SELECT p.PID, s.SID, s.UID
		FROM petmeeting.Pet p, petmeeting.Showoff s 
		WHERE p.UID = s.UID) AS k
		LEFT JOIN petmeeting.Vote AS v ON k.SID = v.SID;
    '''

    cursor = conn.cursor()
    cursor.execute(sql)
    row = cursor.fetchall()

    data_list = []

    for obj in row:
        data_dic = {
            'petId': obj[0],
            'userId': obj[1],
         			'rating': obj[2],
        }
        data_list.append(data_dic)

    conn.close()
    return data_list


# 유저별 rating을 기반으로, 가장 관련성이 높은 10개의 pet_id를 산출한다.
def get_top_n(predictions, n):

    temp = defaultdict(list)
    top_n = dict()

    # First map the predictions to each user.
    for user_id, pet_id, true_r, est, _ in predictions:
        temp[user_id].append((pet_id, est))

    # Then sort the predictions for each user and retrieve the k highest ones.
    for user_id, user_ratings in temp.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        pet_id_list = list(map(lambda x: x[0], user_ratings))

        # pet_id_list 에서 nan 값 제거
        pet_id_list_len = len(pet_id_list)
        j = -1
        for i in range(pet_id_list_len):
            j += 1
            if not isinstance(pet_id_list[j], str) and math.isnan(pet_id_list[j]):
                del pet_id_list[j]
                j = j-1

        pet_id_list = list(map(int, pet_id_list))
        top_n[user_id] = pet_id_list[:n]

    return top_n


# 기존 데이터셋으로 model을 train시키고 각 유저별 top_n을 predict한다.
def predict():
	global top_n
	global user_id
	print("--predict start--------------------------------")

	# request
	json_data = get_default_ratings()
	data = pd.DataFrame(json_data)

	reader = Reader(rating_scale=(0, 5))
	data = Dataset.load_from_df(df=data, reader=reader)

	trainset_2, testset_2 = train_test_split(data, test_size=0.3)

	algo = SVDpp()
	predictions = algo.fit(trainset_2).test(testset_2)

	top_n = get_top_n(predictions, n=10)


# choosing_page에 접속했을 때, user_id를 받아와서 top_10 pet id를 return
# /pets -> /choosing_page
# user_id = request.args.get("uid", 0) -> user_id = requests.user_id
@app.route('/choosing_page', methods=['GET', 'POST'])
def give_top_n():
	global user_id
	user_id = request.args.get("uid", 0)
	global top_n

	try:
	    return str(top_n[int(user_id)])
	except:
		return str([])


if __name__ == '__main__':
    predict()
    app.run()

# show off page 에 user가 새로운 vote를 할 때 db가 변하므로 새로 model을 train 시켜야 한다.
# @app.route('/show_off_page', methods=['GET', 'POST'])
# def new_predict():
#     global top_n
#     global user_id
#     print("--predict restart--------------------------------")

#     # request
#     json_data = get_default_ratings()

#     # new_data_set
#     data = pd.DataFrame(json_data)

#     reader = Reader(rating_scale=(0, 5))
#     data = Dataset.load_from_df(df=data, reader=reader)

#     trainset_2, testset_2 = train_test_split(data, test_size=0.3)

#     algo = SVDpp()
#     predictions = algo.fit(trainset_2).test(testset_2)

#     top_n = get_top_n(predictions, n=10)