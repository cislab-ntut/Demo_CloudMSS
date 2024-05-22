from ctypes import sizeof
import random 
import math
import numpy as np
import pandas as pd
import time
import os

from sklearn import datasets
from sklearn import tree
from sklearn import neighbors

from my_app.MSS_system import *

# =======

# Global Parameters

# Mersenne Prime 4th(7) 5th(13) 6th(17) 7th(19) = 127, 8191, 131071, 524287
PRIME = 2**19 - 1

# L的最小值，必需比資料最大值(包括計算後)來的大。
L_Min = 3000

random_size = 100

# ====

# Basic numbers：協助運算的已知 secret。
B_K = [ 1 ]
b_k = len(B_K)
basic_number_one_idx = 0

# =======

def MSS_system_init(train_X, train_y, user_n, thresholds):
    
    n_row = train_X.shape[0]
    n_column = train_X.shape[1]

    # # K：multi-secret list ( K < PRIME )，PRIME = 524287。
    # order = 'C'：以列為主。
    K = list( train_X.values.flatten('C') )
    t = list( thresholds.values.flatten('C') )

    # # 一般的 Basic number 是一些在模型中的常用參數。
    # # 為了讓系統能方便地快速使用，經常設定門檻值為 1，即任何一個參與者都能直接使用。
    # b_t = user_n
    # 
    # # 但是，在這個系統中 Basic number = 1 負責協助資料上傳。
    # # 若我們希望這個上傳資料必需包含上傳者才能解開，應該將 b_t 設定成 user_n。
    # b_t = user_n
    # 
    # # 或是，根據 Byzantine Problem (拜占庭問題)，將 b_t 預設成滿足 2/3 (半數以上) 的 參與者人數。
    # # 在分佈式系統中達成共識的安全性，至少需要擁有 2/3 以上的可靠和誠實的節點。
    b_t = math.ceil(user_n * 2 / 3)
    
    B_t = [b_t] * b_k

    # 加入 Basic numbers：協助運算的已知 secret。
    K = B_K + K
    t = B_t + t

    # service_t：最大的 t，即滿足條件才可使用全部資料進行訓練。
    service_t = max(t)

    # 本服務的系統預設參數資料範圍
    basic_length = len(B_K)

    # Dealer 收到 整合資料集。
    dealer = Dealer(user_n, K, t, train_y)

    # User 收到 獨立id = x座標。
    clients = []        
    for i in range(user_n):
        clients.append(Client(i))

    # 開始分發 User share & 製作 雙雲Server 的 public share。
    MSS = dealer.distribute(clients)

    del dealer

    return MSS, clients, n_row, n_column, service_t, basic_length

def MSS_kNN(MSS, participant, n_row, n_column, test_X, n_neighbors):
    
    result = []

    labels = MSS.sent_labels()

    for i in range(test_X.shape[0]):

        print("- query instance:", i)

        # STEP1 client 將 每一筆 query_instance 製成 share。
        query_share_index = []
        
        for j in range(test_X.shape[1]):
            query_share_index.append(MSS.scalar_multiplication(participant, basic_number_one_idx , test_X[i][j]))

        # STEP2 計算 dataset instance 與 此 query instance 的距離。
        distance = []

        for r in range(n_row):
            deltaSum = 0

            for c in range(n_column):

                d_attribute_index = b_k + (r * n_column) + c
                q_attribute_index = query_share_index[c]

                # STEP2-1 每個 attribute 比較大小：dataset_attribute > query_attribute = 1。
                comp = MSS.compare(participant, d_attribute_index , q_attribute_index)

                # STEP2-2 計算 difference
                difference = 0
                if comp == 1:
                    difference = MSS.minus(participant, d_attribute_index , q_attribute_index)
                else:
                    difference = MSS.minus(participant, q_attribute_index , d_attribute_index)

                # STEP3 計算距離
                delta = MSS.reconstruct_MSS_Secret(participant, difference)

                # print("c:", c , "compare:", comp , "delta:", delta)

                deltaSum += delta**2

            # os.system("pause")

            deltaSum = deltaSum**0.5

            distance.append(deltaSum)

        result += knn_classifier(distance, labels, n_neighbors)

        # STEP4 得出本次 query instance 的分類結果後，將 record 清理乾淨，節省儲存空間。
        MSS.clear()
        
    return result

def knn_classifier(distance, labels, n_neighbors):  # distance = 每筆 train instance 跟 某個 query instance 的距離

    result = []

    DAL = []                                        # DAL = DistanceAndLabel
    for i in range(len(distance)):
        d = distance[i]
        l = labels[i]
        DAL.append([ d , l ])
    
    SDAL = sorted( DAL , key=(lambda x : x[0]) )    # SDAL = Sorted_DAL  (按距離由小到大排序)
    
    predict_label = {}
    neighbor_distance = SDAL[0][0]
    neighbor_count = 0
    for i in range(len(SDAL)):
        d = SDAL[i][0]
        l = SDAL[i][1]

        if d > neighbor_distance:
            if neighbor_count > n_neighbors:
                break
            else:
                neighbor_distance = d

        if d <= neighbor_distance:
            predict_label[l] = predict_label.get(l, 0) + 1
            neighbor_count += 1

    SPL = sorted( predict_label.items() , key=(lambda x:x[1]), reverse=True )

    result.append(SPL[0][0])
    
    return result

# =======

def acc_evaluate(result, test_y):
    
    correct_rate = 0

    if(len(result) != 0):
        incorrect = 0
        for j in range(len(result)):
            if( result[j] != test_y[j] ):
                incorrect = incorrect + 1
        
        correct_rate = ( len(result) - incorrect ) / len(result) * 100
    
    return correct_rate
