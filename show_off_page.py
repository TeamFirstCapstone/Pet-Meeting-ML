from sklearn.decomposition import TruncatedSVD
from scipy.sparse.linalg import svds
import string

from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import math
from surprise import Dataset
import sys

from surprise import Reader
from surprise.model_selection import cross_validate
from surprise import SVDpp
from surprise.model_selection import train_test_split
from collections import defaultdict

import utils

pet_ID_list=[]


app = Flask(__name__)

# show_off_page 에서 유저가 pet post를 선택할 때마다,
# 이전의 유저의 선호 데이터를 기반으로
# 해당 pet과 관련된 top 10 pet id 를 return 한다.
# 그럼으로써 pet post를 추천받는다.
# 단, 관련도에 따라 10개 이하일 수 있다.
def predict():
    global petId
    global corr
    # get_pet_id = request.args.get("pid", 0)
    data = pd.DataFrame(utils.get_default_ratings())

    # print(data)

    user_pet_rating = data.pivot_table('rating', index='userId',
                                       columns='petId').fillna(0)

    pet_user_rating = user_pet_rating.values.T

    algo = TruncatedSVD(n_components=12)
    matrix = algo.fit_transform(pet_user_rating)

    corr = np.corrcoef(matrix)

    petId = user_pet_rating.columns
    # pet_ID_list = list(petId)

    # ##
    # print(pet_ID_list)
    # ##

    # coffey_hands = pet_ID_list.index(get_pet_id)

    # corr_coffey_hands = corr[coffey_hands]
    # pet_id_list = list(petId[(corr_coffey_hands >= 0.9)])[:10]

    # print(pet_id_list)


@app.route('/show_off_page', methods=['GET', 'POST'])
def give_pet_id_list():
    global get_pet_id
    get_pet_id = request.args.get("pid", 0)
    global petId
    global corr

    pet_ID_list = list(petId)

    ##
    print(pet_ID_list.index(2))
    ##

    coffey_hands = pet_ID_list.index(int(get_pet_id))

    corr_coffey_hands = corr[coffey_hands]
    pet_id_list = list(petId[(corr_coffey_hands >= 0.9)])[:10]

    # print(pet_id_list)

    return str(pet_id_list)


if __name__ == '__main__':
    predict()
    # index()
    app.run()
