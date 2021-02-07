from flask import Flask,request, jsonify
import pandas as pd
import math
from surprise import Dataset
from surprise import Reader
from surprise import SVDpp
from surprise.model_selection import train_test_split
from collections import defaultdict
import pymysql
import csv

top_n = defaultdict(list)

item_list=[]

app = Flask(__name__)

# Class For Mysql Database OOP
import re
import pymysql
 
# ## DB 싱글톤
# class Singleton(type):
#     _instances = {}
#     def __call__(cls, *args, **kwargs):
#         if cls not in cls._instances:
#             cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
#         else:
#             cls._instances[cls].__init__(*args, **kwargs)
 
#         return cls._instances[cls]
 
# class Database(metaclass=Singleton):
 
    # def __init__(self, dbName):
    #     self.db = pymysql.connect(host='petmeeting.cvsejgvxoucu.us-east-2.rds.amazonaws.com',
    #                               user='admin',
    #                               password='petmeeting123',
    #                               db=dbName,
    #                               charset='utf8')
    #     self.cursor = self.db.cursor(pymysql.cursors.DictCursor)
 
#     def execute(self, query, args={}):
#         self.cursor.execute(query, args)
 
#     def executeOne(self, query, args={}):
#         self.cursor.execute(query, args)
#         row = self.cursor.fetchone()
#         return row
 
#     def executeAll(self, query, args={}):
#         self.cursor.execute(query, args)
#         row = self.cursor.fetchall()
#         return row

#     def close(self):
#         self.db.close()
 
#     def commit(self):
#         self.db.commit()

# db = Database('petmeeting')

# {pet_id, user_id, Rating} 형식으로, 모든 평가 데이터를 가져온다.
def get_default_ratings():
    
    # db = Database('petmeeting')

    # sql = '''
    #     SELECT k.PID, v.UID, v.Score FROM 
    #     (SELECT p.PID, s.SID, s.UID
    #     FROM petmeeting.Pet p, petmeeting.Showoff s 
    #     WHERE p.UID = s.UID) AS k
    #     LEFT JOIN petmeeting.Vote AS v ON k.SID = v.SID
    #     WHERE !isnull(k.PID) AND !isnull(v.UID) AND !isnull(v.Score);
    # '''

    # row = db.executeAll(sql)
    data_list = []
    new_data_list=[]

    with open('./inputs/ratings.csv','r') as  f:
        reader = csv.reader(f)

        for row in reader:
            # print(row)
            data_list.append(row)
            # print(row)

        # for obj in reader:
        #     data_dic = {
        #         'petId': obj['petId'],
        #         'userId': obj['userId'],
        #         'rating': obj['rating'],
        #     }
        #     data_list.append(data_dic)

        del(data_list[0])

        for row in data_list:
            row = [float (i) for i in row]
            temp={
                'petId':row[0],
                'userId':row[1],
                'rating':row[2]
            }
            new_data_list.append(temp)
            
    # print(data_list[0])

    # print(new_data_list)

    return data_list

    # data_list = []

    # for obj in row:
    #     data_dic = {
    #         'petId': obj['PID'],
    #         'userId': obj['UID'],
    #      	'rating': obj['Score'],
    #     }
    #     data_list.append(data_dic)

    # return data_list

#item list 얻기
# def get_item_data_list():
#     global item_list
#     data_list = []
#     # new_data_list=[]

#     with open('./inputs/movies.csv','r') as  f:
#         reader = csv.reader(f)

#         for row in reader:
#             data_list.append(row)

#         del(data_list[0])

#         item_list=data_list
    
#     return item_list
        

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

	# dataset import
	rating_data = pd.DataFrame(get_default_ratings()) 
    

	reader = Reader(rating_scale=(0, 5))
	data = Dataset.load_from_df(df=rating_data, reader=reader)

	trainset_2, testset_2 = train_test_split(data, test_size=0.3)

	# print("--test2--------------------------------")


	algo = SVDpp()
	predictions = algo.fit(trainset_2).test(testset_2)

	# print("--test1--------------------------------")

	top_n = get_top_n(predictions, n=10)

	print("--predict end--------------------------------")

# def find_item(item_id_list):

    
    
#     for item_id in item_id_list:
#         for row in item_list:
#             if row[0] == item_id:
                


# choosing_page에 접속했을 때, user_id를 받아와서 top_10 pet id를 return
# /pets -> /choosing_page
@app.route('/choosing_page', methods=['GET', 'POST'])
def give_top_n():
	global user_id
	user_id = request.args.get("uid", 0)

	# item_data = pd.DataFrame(get_item_data_list())

	global item_list

	global top_n

	# try:
	#     return jsonify(result=top_n[int(user_id)])

	item_id_list = top_n[user_id]

	# item_list = find_item(item_id_list)
    
	try:
	    return jsonify(item_id=item_id_list)
        
	except:
		return jsonify(result=[])

# show off page 에 user가 새로운 vote를 할 때 db가 변하므로 새로 model을 train 시켜야 한다.
@app.route('/show_off_page', methods=['GET', 'POST'])
def update():
    global top_n
    global user_id
    new_vote = request.args.get("vote", 0) # 새로 vote가 되면 1을 얻는다.

    if new_vote == '1':

        predict()

    return ""

if __name__ == '__main__':

    predict()

    print("------------predict process was done. app start----------------")

    # print(top_n)

    app.run()

    # predict()

    # app.run(host='0.0.0.0')

    