# import pymysql
# from flask import request,Flask

# import choosing_page_func
# import show_off_page_func

# app = Flask(__name__)

# # db 접속
# def get_connection():
#     conn = pymysql.connect(host='petmeeting.cvsejgvxoucu.us-east-2.rds.amazonaws.com',
#                            user='admin', password='petmeeting123', db='petmeeting', charset='utf8')
#     return conn

# # {pet_id, user_id, Rating} 형식으로, 모든 평가 데이터를 가져온다.
# def get_default_ratings():
    
#     conn = get_connection()

#     sql = '''
#         SELECT k.PID, v.UID, v.Score FROM 
#         (SELECT p.PID, s.SID, s.UID
#         FROM petmeeting.Pet p, petmeeting.Showoff s 
#         WHERE p.UID = s.UID) AS k
#         LEFT JOIN petmeeting.Vote AS v ON k.SID = v.SID
#         WHERE !isnull(k.PID) AND !isnull(v.UID) AND !isnull(v.Score);
#     '''

#     cursor = conn.cursor()
#     cursor.execute(sql)
#     row = cursor.fetchall()

#     data_list = []

#     for obj in row:
#         data_dic = {
#             'petId': obj[0],
#             'userId': obj[1],
#          			'rating': obj[2],
#         }
#         data_list.append(data_dic)

#     conn.close()
#     return data_list

# # if __name__ == '__main__':
# #     choosing_page_func.predict()
# #     app.run()
