from ast import Or
from asyncio.windows_events import NULL

import random
import math
from tokenize import tabsize 
import numpy as np
import pandas as pd
import time

from my_app.secret_sharing import generateShares, reconstructSecret

from my_app.multi_secret_sharing import generate_Participant_Share, generate_Public_Shares

# ====

# Global Parameters

# Mersenne Prime 4th(7) 5th(13) 6th(17) 7th(19) = 127, 8191, 131071, 524287
PRIME = 2**19 - 1

# L的最小值，必需比資料最大值(包括計算後)來的大。
L_Min = 3000

random_size = 100

# Basic Tools

def _extended_gcd(a, b):
    """
    Division in integers modulus p means finding the inverse of the denominator modulo p. 
    < Note: inverse of A is B such that (A * B) % p == 1 >
    this can be computed via extended Euclidean algorithm (擴展歐幾里得算法，又叫「輾轉相除法」): 
    http://en.wikipedia.org/wiki/Modular_multiplicative_inverse#Computation
    """
    x = 0
    last_x = 1
    y = 1
    last_y = 0

    while b != 0:
        quot = a // b
        a, b = b, a % b

        x, last_x = last_x - quot * x, x
        y, last_y = last_y - quot * y, y
        
    return last_x, last_y

def _divmod(num, den, p):
    # Compute num / den modulo prime p
    invert, _ = _extended_gcd(den, p)
    return num * invert

def share_list_addition(a, b):
    c = []
    for i in range(len(a)):
        x = a[i][0]
        for j in range(len(b)):
            if x == b[j][0]:
                y = (a[i][1] + b[j][1]) % PRIME
                break
        c.append([ x , y ])
    return c

def share_list_minus(a, b):
    c = []
    for i in range(len(a)):
        x = a[i][0]
        for j in range(len(b)):
            if x == b[j][0]:
                y = (a[i][1] - b[j][1]) % PRIME
                break
        c.append([ x , y ])
    return c

def share_list_constant_multiplication(a, value):
    c = []
    for i in range(len(a)):
        c.append([ a[i][0], (a[i][1] * value) % PRIME ])
    return c

# ====

class Dealer:
        
    def __init__(self, Participants, secrets, secrets_participant_threshold, labels):
        self.n = Participants
        # self.data = secrets
        self.data = np.rint(secrets).astype(np.int32)
        self.t = secrets_participant_threshold
        self.labels = labels

    def distribute(self, clients):

        MSS = MSS_system(self.n, len(self.data), self.t, clients, self.labels)
        
        server_1 = MSS.call_server_1()
        server_2 = MSS.call_server_2()

        Participant_Share = generate_Participant_Share(self.n)

        for i in range(len(Participant_Share)):
            clients[i].get_share(Participant_Share[i])

        pseudo_secret_1 = np.random.randint(1, random_size, size = len(self.data))
        pseudo_secret_2 = pseudo_secret_1 * np.array(self.data) % PRIME

        Public_Shares_1 = generate_Public_Shares(Participant_Share, pseudo_secret_1, self.t)
        Public_Shares_2 = generate_Public_Shares(Participant_Share, pseudo_secret_2, self.t)
        
        server_1.get_share(Public_Shares_1)
        server_2.get_share(Public_Shares_2)

        # print("Participants:" , self.n)
        # print("Participant_Share:", Participant_Share)
        # print()
        # print("Secrets:" , self.data)
        # print("pseudo_secret_1:" , pseudo_secret_1)
        # print("pseudo_secret_2:" , pseudo_secret_2)

        return MSS

class Client:
    
    def __init__(self, id):
        self.id = id
        self.share = None

    def sent_id(self):
        return self.id

    def get_share(self, Participant_Share):
        self.share = Participant_Share

    def sent_d_share(self, share_a):
        point_x = self.share[0]
        point_y = (self.share[1] - share_a[1]) % PRIME
        share_d = [ point_x , point_y ]
        return share_d

    def sent_e_share(self, share_y, share_b):
        point_x = self.share[0]
        point_y = (share_y[1] - share_b[1]) % PRIME
        share_e = [ point_x , point_y ]
        return share_e
    
    def sent_xy_share(self, share_a, share_b, share_c, d, e):
        point_x = self.share[0]
        point_y = ( e * (self.share[1] - share_a[1]) + d * share_b[1] + e * share_a[1] + share_c[1] ) % PRIME
        share_xy = [ point_x , point_y ]
        return share_xy

class MSS_system:

    def __init__(self, n, k, t, clients, labels):
        self.n = n                      # 參與者 數量
        self.k = k                      # secret 數量
        self.t = t                      # secret threshold

        self.server_1 = self.Server_1(self, labels)
        self.server_2 = self.Server_2(self)
        self.RG = self.Randomness_Generator(self, clients)

        self.revert = t
        # self.operation_record = {}      # operation 紀錄

    def call_server_1(self):
        return self.server_1
    
    def call_server_2(self):
        return self.server_2

    def call_RG(self):
        return self.RG

    def call_global_parameter(self):
        return self.n, self.k, self.t

    def update_threshold(self, t):
        self.t = t
    
    def sent_labels(self):
        return self.server_1.sent_labels()

    class Server_1:
        
        def __init__(self, MSS_system, labels):
            self.MSS = MSS_system
            self.share = None
            self.labels = labels
            self.operation_record = {}      # operation 紀錄
        
        def get_share(self, Public_Share):
            self.share = Public_Share

        def sent_d_share(self, i, num, share_a_list):
            share_d = share_list_minus(self.share[i], share_a_list)
            return share_d[0 : num]
        
        def sent_e_share(self, i, num, share_y_list, share_b_list):
            share_e = share_list_minus(share_y_list, share_b_list)
            return share_e[0 : num]
        
        def sent_xy_share(self, i, num, share_a_list, share_b_list, share_c_list, d, e):
            share_de_list = share_list_constant_multiplication( share_list_minus(self.share[i], share_a_list), e )
            share_bd_list = share_list_constant_multiplication( share_b_list, d )
            share_ae_list = share_list_constant_multiplication( share_a_list, e )
            share_xy_list = share_list_addition( share_list_addition(share_de_list, share_bd_list), share_list_addition(share_ae_list, share_c_list) )
            return share_xy_list[0 : num]
        
        def get_operation_record(self, new_threshold, new_record):

            n , k , t = self.MSS.call_global_parameter()

            operation_index = len(t)

            self.MSS.update_threshold(t + [ new_threshold ])

            self.operation_record[operation_index] = new_record

            return operation_index

        def call_operation_record(self , i):
            return self.operation_record[i]
        
        def print_operation_record(self):

            n , k , t = self.MSS.call_global_parameter()

            operation_record = self.operation_record

            exception_keywords = ["participants", "operand_a", "operand_b"]
            
            respond = []

            respond.append("- Original Secret index: 0 - " + str(k - 1) )

            respond.append("- Operation record：")

            if len(operation_record) == 0:
                respond.append("None operation！")
            else:
                for operation_id in operation_record:
                    
                    temp_text = "-- index: " + str(operation_id)
                    
                    for key in operation_record[operation_id]:
                        if key not in exception_keywords:
                            temp_text = temp_text + " , " + str(key) + ": " + str(operation_record[operation_id][key])

                    temp_text = temp_text + " , participants threshold: " + str(t[operation_id])

                    respond.append(temp_text)

            return respond

        def clear_operation_record(self):
            self.operation_record = {}
        
        def sent_labels(self):
            return self.labels

        # ====

        # MSS Protocols
        
        def addition(self, participants, a, b):
            
            RG = self.MSS.call_RG()
            n , k , t = self.MSS.call_global_parameter()
        
            a_randomness_index_1, a_randomness_index_2 = RG.poly_randomness(a)

            collect_shares_a_1 , collect_shares_a_2 = self.MSS.collect_shares(participants , a , a_randomness_index_1, a_randomness_index_2)

            pseudo_secret_a_1 = reconstructSecret(collect_shares_a_1)

            b_randomness_index_1, b_randomness_index_2 = RG.poly_randomness(b)
            
            collect_shares_b_1 , collect_shares_b_2 = self.MSS.collect_shares(participants , b , b_randomness_index_1, b_randomness_index_2)

            pseudo_secret_b_1 = reconstructSecret(collect_shares_b_1)

            # ====
            
            operation_threshold = max(t[a] , t[b])
            
            operation_index = len(t)

            self.MSS.update_threshold(t + [ operation_threshold ])

            self.operation_record[operation_index] = {
                "info (index operation index)": str(a) + " + "+ str(b),
                "operation": "+",
                "operand_a": (a , a_randomness_index_1 , a_randomness_index_2),
                "operand_b": (b , b_randomness_index_1 , b_randomness_index_2),
                "pseudo_secret_a_1": pseudo_secret_a_1,
                "pseudo_secret_b_1": pseudo_secret_b_1,
                "participants": participants
            }

            return operation_index

        def multiplication(self, participants, a, b):

            RG = self.MSS.call_RG()
            n , k , t = self.MSS.call_global_parameter()

            a_randomness_index_1, a_randomness_index_2 = RG.poly_randomness(a)

            collect_shares_a_1 , collect_shares_a_2 = self.MSS.collect_shares(participants , a , a_randomness_index_1, a_randomness_index_2)

            pseudo_secret_a_1 = reconstructSecret(collect_shares_a_1)

            b_randomness_index_1, b_randomness_index_2 = RG.poly_randomness(b)
            
            collect_shares_b_1 , collect_shares_b_2 = self.MSS.collect_shares(participants , b , b_randomness_index_1, b_randomness_index_2)

            pseudo_secret_b_2 = reconstructSecret(collect_shares_b_2)

            # ==== 

            operation_threshold = max(t[a] , t[b])
            
            operation_index = len(t)

            self.MSS.update_threshold(t + [ operation_threshold ])

            self.operation_record[operation_index] = {
                "info (index operation index)": str(a) + " * "+ str(b),
                "operation": "*",
                "operand_a": (a , a_randomness_index_1 , a_randomness_index_2),
                "operand_b": (b , b_randomness_index_1 , b_randomness_index_2),
                "pseudo_secret_a_1": pseudo_secret_a_1,
                "pseudo_secret_b_2": pseudo_secret_b_2,
                "participants": participants
            }

            return operation_index

        def minus(self, participants, a, b):

            RG = self.MSS.call_RG()
            n , k , t = self.MSS.call_global_parameter()
        
            a_randomness_index_1, a_randomness_index_2 = RG.poly_randomness(a)

            collect_shares_a_1 , collect_shares_a_2 = self.MSS.collect_shares(participants , a , a_randomness_index_1, a_randomness_index_2)

            pseudo_secret_a_1 = reconstructSecret(collect_shares_a_1)

            b_randomness_index_1, b_randomness_index_2 = RG.poly_randomness(b)
            
            collect_shares_b_1 , collect_shares_b_2 = self.MSS.collect_shares(participants , b , b_randomness_index_1, b_randomness_index_2)

            pseudo_secret_b_1 = reconstructSecret(collect_shares_b_1)

            # ====
            
            operation_threshold = max(t[a] , t[b])
            
            operation_index = len(t)

            self.MSS.update_threshold(t + [ operation_threshold ])

            self.operation_record[operation_index] = {
                "info (index operation index)": str(a) + " - "+ str(b),
                "operation": "-",
                "operand_a": (a , a_randomness_index_1 , a_randomness_index_2),
                "operand_b": (b , b_randomness_index_1 , b_randomness_index_2),
                "pseudo_secret_a_1": pseudo_secret_a_1,
                "pseudo_secret_b_1": pseudo_secret_b_1,
                "participants": participants
            }

            return operation_index

        def compare(self, participants, a, b):
            
            RG = self.MSS.call_RG()
            n , k , t = self.MSS.call_global_parameter()

            l_share , r1_share , r2_share = RG.compare_random_shares(participants)
            # print("l_share , r1_share , r2_share: ", l_share , r1_share , r2_share)

            # =============

            operation_index_a_MINUS_b = self.minus(participants, a , b)
            # print("a_MINUS_b =", self.MSS.reconstruct_MSS_Secret(participants, operation_index_a_MINUS_b))

            operation_index_a_MINUS_b_ADD_l = self.addition(participants, operation_index_a_MINUS_b , l_share)
            # print("a_MINUS_b_ADD_l =", self.MSS.reconstruct_MSS_Secret(participants, operation_index_a_MINUS_b_ADD_l))

            m = self.MSS.reconstruct_MSS_Secret(participants, operation_index_a_MINUS_b_ADD_l)
            l = self.MSS.reconstruct_MSS_Secret(participants, l_share)

            # 使比較的基準對象，從還原的數值l，轉變成 h，不會產生隱私洩漏問題。
            # # 否則，對於知道 差值m 的 資料a或b之擁有者，能輕易推得另一個數字之值。
            operation_index_m_MUL_r1 = self.multiplication(participants, operation_index_a_MINUS_b_ADD_l , r1_share)
            operation_index_m_MUL_r1_add_r2 = self.addition(participants, operation_index_m_MUL_r1 , r2_share)
            # print("m_MUL_r1 =", self.MSS.reconstruct_MSS_Secret(participants, operation_index_m_MUL_r1))
            # print("m_MUL_r1_add_r2 =", self.MSS.reconstruct_MSS_Secret(participants, operation_index_m_MUL_r1_add_r2))
            
            operation_index_l_MUL_r1 = self.multiplication(participants, l_share , r1_share)
            operation_index_l_MUL_r1_add_r2 = self.addition(participants, operation_index_l_MUL_r1 , r2_share)
            # print("l_MUL_r1 =", self.MSS.reconstruct_MSS_Secret(participants, operation_index_l_MUL_r1))
            # print("l_MUL_r1_add_r2 =", self.MSS.reconstruct_MSS_Secret(participants, operation_index_l_MUL_r1_add_r2))

            """
            此處，r1 , r2 是為 原始秘密 增加 隨機值，以免 比較運算的還原值 洩漏 原始秘密之間的關聯性。
            => r1 = 隨機倍化，r2 = 隨機常數 -> 將他們做成 share，再用 MSS multiplication 和 MSS addition 改變 秘密內容。
            ==> 此處，若是 能透過 scalar_multiplication 直接對資料進行 r1倍化，有機會省去 MSS multiplication 的計算。
                但是，對於 執行 compare 的角色來說，r1 極有可能需要是明文，因此這個優化提議可能有問題。
                因此，維持原型 讓 RG 先將 r1 分發成 share 再來計算。
            """

            s = self.MSS.reconstruct_MSS_Secret(participants, operation_index_m_MUL_r1_add_r2)
            h = self.MSS.reconstruct_MSS_Secret(participants, operation_index_l_MUL_r1_add_r2)

            # print("s:" , s)
            # print("h:" , h)

            return s > h

    class Server_2:
        
        def __init__(self, MSS_system):
            self.MSS = MSS_system
            self.share = None
            # self.operation_record = {}      # operation 紀錄
        
        def get_share(self, Public_Share):
            self.share = Public_Share

        def sent_d_share(self, i, num, share_a_list):
            share_d = share_list_minus(self.share[i], share_a_list)
            return share_d[0 : num]
        
        def sent_e_share(self, i, num, share_y_list, share_b_list):
            share_e = share_list_minus(share_y_list, share_b_list)
            return share_e[0 : num]
        
        def sent_xy_share(self, i, num, share_a_list, share_b_list, share_c_list, d, e):
            share_de_list = share_list_constant_multiplication( share_list_minus(self.share[i], share_a_list), e )
            share_bd_list = share_list_constant_multiplication( share_b_list, d )
            share_ae_list = share_list_constant_multiplication( share_a_list, e )
            share_xy_list = share_list_addition( share_list_addition(share_de_list, share_bd_list), share_list_addition(share_ae_list, share_c_list) )
            return share_xy_list[0 : num]

    # ====

    class Randomness_Generator:

        def __init__(self, MSS_system, clients):
            self.MSS = MSS_system
            self.clients = clients
            self.randomness_record = {}     # randomness 紀錄

        def poly_randomness(self, i, num = 1):

            n, k, t = self.MSS.call_global_parameter()

            # ====

            num = num % PRIME

            r = np.random.randint(1, random_size)
            # print('r:' , r)

            r1 = r % PRIME
            r2 = (r * num) % PRIME

            share_r1 = generateShares(2 * n + 1 - t[i] , t[i] , r1)
            share_r2 = generateShares(2 * n + 1 - t[i] , t[i] , r2)

            # ====

            a1 = np.random.randint(1, random_size)
            b1 = np.random.randint(1, random_size)
            c1 = (a1 * b1) % PRIME 

            share_a1 = generateShares(2 * n + 1 - t[i] , t[i] , a1)
            share_b1 = generateShares(2 * n + 1 - t[i] , t[i] , b1)
            share_c1 = generateShares(2 * n + 1 - t[i] , t[i] , c1)

            randomness_index_1 = len(self.randomness_record)

            self.randomness_record[randomness_index_1] = {
                # "r": r,
                "share_r": share_r1,
                "share_a": share_a1,
                "share_b": share_b1,
                "share_c": share_c1
            }

            a2 = np.random.randint(1, random_size)
            b2 = np.random.randint(1, random_size)
            c2 = (a2 * b2) % PRIME 

            share_a2 = generateShares(2 * n + 1 - t[i] , t[i] , a2)
            share_b2 = generateShares(2 * n + 1 - t[i] , t[i] , b2)
            share_c2 = generateShares(2 * n + 1 - t[i] , t[i] , c2)
            
            randomness_index_2 = len(self.randomness_record)

            self.randomness_record[randomness_index_2] = {
                # "r": r,
                "share_r": share_r2,
                "share_a": share_a2,
                "share_b": share_b2,
                "share_c": share_c2
            }
            
            return randomness_index_1, randomness_index_2

        def sent_randomness(self, index):
            randomness_record = self.randomness_record[index]

            share_r = randomness_record["share_r"]
            share_a = randomness_record["share_a"]
            share_b = randomness_record["share_b"]
            share_c = randomness_record["share_c"]

            return share_r, share_a, share_b, share_c

        def print_randomness_record(self):
            
            print("Randomness_Generator Record:")
            print()

            randomness_record = self.randomness_record

            exception_keywords = ["share_a", "share_b", "share_c", "share_de"]

            if len(randomness_record) == 0:
                print("None randomness！")
            else:
                for randomness_id in randomness_record:
                    print("-- index:" , randomness_id , end = ' ')

                    for key in randomness_record[randomness_id]:
                        if key not in exception_keywords:
                            print(" , " , key , ":" , randomness_record[randomness_id][key] , end = ' ')
                    
                    print()

        def clear_randomness_record(self):
            self.randomness_record = {}

        def scalar_multiplication(self, participants, i, num):

            ## 雖然 poly_randomness 可以直接做到 scalar_multiplication 的效果，但是不支援修改 operation_index。
            ## 因此，當使用 scalar_multiplication 進行 uploading data 時，需要利用  MSS.multiplication 來完成資料上傳。
            #  這邊，為了在 operation_record 區分 "info (scalar operation index)"，所以不直接呼叫 MSS.multiplication。
    
            n, k, t = self.MSS.call_global_parameter()
            
            server_1 = self.MSS.call_server_1()

            # ====

            num = int(round(num))

            basic_number_one_index = 0

            scalar_index_1, scalar_index_2 = self.poly_randomness(basic_number_one_index, num)

            collect_shares_a_1 , collect_shares_a_2 = self.MSS.collect_shares(participants , basic_number_one_index , scalar_index_1, scalar_index_2)

            pseudo_secret_a_1 = reconstructSecret(collect_shares_a_1)

            b_randomness_index_1, b_randomness_index_2 = self.poly_randomness(i)
            
            collect_shares_b_1 , collect_shares_b_2 = self.MSS.collect_shares(participants , i , b_randomness_index_1, b_randomness_index_2)

            pseudo_secret_b_2 = reconstructSecret(collect_shares_b_2)

            # ==== 

            operation_threshold = max(t[0] , t[i])

            operation_record = {
                "info (scalar operation index)": str(num) + " * "+ str(i),
                "operation": "*",
                "operand_a": (0 , scalar_index_1, scalar_index_2),
                "operand_b": (i , b_randomness_index_1 , b_randomness_index_2),
                "pseudo_secret_a_1": pseudo_secret_a_1,
                "pseudo_secret_b_2": pseudo_secret_b_2,
                "participants": participants
            }

            operation_index = server_1.get_operation_record(operation_threshold, operation_record)

            return operation_index
        
        def compare_random_shares(self, participants):

            ## 問題：如何產生 l、r1、r2 的 share 作為計算的中間值。
            ## 做法：預設一些公開的計算用的 secret = 1，再 self.scalar_multiplication => l , r1, r2。

            r2 = random.randint(1, random_size)
            r1 = random.randint(1, 50)

            # 2lr + r' < PRIME
            L_max = round(((PRIME - r2) / r1) / 2)
            l = random.randint(L_Min, L_max)

            # print()
            # print("l =" , l , ", r1 =" , r1 , ", r2 =" , r2)

            l_index = self.scalar_multiplication(participants, 0 , l)
            r1_index = self.scalar_multiplication(participants, 0 , r1)
            r2_index = self.scalar_multiplication(participants, 0 , r2)

            # print("l_index , r1_index , r2_index:", l_index , r1_index , r2_index)

            return l_index , r1_index , r2_index

    # ====

    # MSS Protocols

    def addition(self, participants, a, b):

        operation_index = self.server_1.addition(participants, a, b)

        return operation_index

    def multiplication(self, participants, a, b):

        operation_index = self.server_1.multiplication(participants, a, b)

        return operation_index
    
    def minus(self, participants, a, b):
        
        operation_index = self.server_1.minus(participants, a, b)

        return operation_index

    def collect_shares(self, participants, i , randomness_index_1 , randomness_index_2):
    
        n , k , t = self.n , self.k , self.t

        # 本輪 randomness 參數
        share_y1, share_a1, share_b1, share_c1 = self.RG.sent_randomness(randomness_index_1)
        share_y2, share_a2, share_b2, share_c2 = self.RG.sent_randomness(randomness_index_2)

        # 本輪  server 需要給出的 public share 數量
        public_num = 0
        if len(participants) < t[i]:
            raise Exception("Need more participant share！")
        else: 
            public_num = n + 1 - len(participants)

        # =======

        collect_shares_1 = []
        collect_shares_2 = []

        if i < k:

            ## 非運算 ( index i < k，origin secret = {0, ..., k-1} )：

            #  乘上 本輪 randomness 參數 提供 share 的 隨機化，避免 本輪的 share 可用來 恢復 非本輪的 secret。

            #  (y = r 乘上 randomness) server 先計算 x-a , y-b 提供 d , e 給 client，即可不知道 x , y 但計算 xy。
            
            # ====

            ## 模擬 server_1 操作。
            #  (x = origin secret，y = 乘上 randomness r)，各方在本地端計算 share_xy = 隨機化 origin secret 的 share。
            #  --> server 先計算 x-a , y-b 提供 d , e 給 client，即可不知道 x , y 但計算 xy。

            share_d1 = []
            share_e1 = []
            for client in  participants:
                id = client.sent_id()

                # 模擬 client 各自收到 randomn a 的 share，將自己的 share masked 再傳出。
                share_d1.append(client.sent_d_share(share_a1[id]))

                # 模擬 client 各自收到 y 的 share 和 randomn b 的 share，將 y share 用 b share masked 再傳出。
                share_e1.append(client.sent_e_share(share_y1[id], share_b1[id]))

            # 模擬 server 收到 randomn a 的 share，將每個 public share 計算成 [x-a]_{pub}。
            share_d1 = share_d1 + self.server_1.sent_d_share(i, public_num, share_a1[ n : ])

            # 模擬 server 收到 y 的 share 和 randomn b 的 share，將每個 public share 計算成 [y-b]_{pub}。
            share_e1 = share_e1 + self.server_1.sent_e_share(i, public_num, share_y1[ n : ], share_b1[ n : ])

            d1 = reconstructSecret(share_d1) % PRIME
            e1 = reconstructSecret(share_e1) % PRIME

            for client in  participants:
                id = client.sent_id()
                collect_shares_1.append( client.sent_xy_share(share_a1[id], share_b1[id], share_c1[id], d1, e1) )     # 模擬 client 各自計算 share (= 乘上 randomness) 再傳出。
            
            collect_shares_1 = collect_shares_1 + self.server_1.sent_xy_share( i, public_num, share_a1[ n : ], share_b1[ n : ], share_c1[ n : ], d1, e1 )

            # ==

            ## 模擬 server_2 操作。
            #  (y = r 乘上 randomness) server 先計算 x-a , y-b 提供 d , e 給 client，即可不知道 x , y 但計算 xy。

            share_d2 = []
            share_e2 = []
            for client in  participants:
                id = client.sent_id()

                # 模擬 client 各自收到 randomn a 的 share，將自己的 share masked 再傳出。
                share_d2.append(client.sent_d_share(share_a2[id]))

                # 模擬 client 各自收到 y 的 share 和 randomn b 的 share，將 y share 用 b share masked 再傳出。
                share_e2.append(client.sent_e_share(share_y2[id], share_b2[id]))

            # 模擬 server 收到 randomn a 的 share，將每個 public share 計算成 [x-a]_{pub}。
            share_d2 = share_d2 + self.server_2.sent_d_share(i, public_num, share_a2[ n : ])

            # 模擬 server 收到 y 的 share 和 randomn b 的 share，將每個 public share 計算成 [y-b]_{pub}。
            share_e2 = share_e2 + self.server_2.sent_e_share(i, public_num, share_y2[ n : ], share_b2[ n : ])

            d2 = reconstructSecret(share_d2) % PRIME
            e2 = reconstructSecret(share_e2) % PRIME

            for client in  participants:
                id = client.sent_id()
                collect_shares_2.append( client.sent_xy_share(share_a2[id], share_b2[id], share_c2[id], d2, e2) )     # 模擬 client 各自計算 share (= 乘上 randomness) 再傳出。
            
            collect_shares_2 = collect_shares_2 + self.server_2.sent_xy_share( i, public_num, share_a2[ n : ], share_b2[ n : ], share_c2[ n : ], d2, e2 )
            
            # =======

        else:

            ## 模擬 運算 ( index i >= k，origin secret = {0, ..., k-1} )
            
            operation_record = self.server_1.operation_record[i]

            for client in operation_record["participants"]:
                if client not in participants:
                    raise Exception("Need particular operation participants！")
            
            ( a , a_randomness_index_1 , a_randomness_index_2 ) = operation_record["operand_a"]
            ( b,  b_randomness_index_1 , b_randomness_index_2 ) = operation_record["operand_b"]

            # 遞迴呼叫：找到最底層的 origin secret，用 持續計算 回傳出 operand 來 運算。
            operation_shares_a_1, operation_shares_a_2 = self.collect_shares(participants , a , a_randomness_index_1, a_randomness_index_2)
            operation_shares_b_1, operation_shares_b_2 = self.collect_shares(participants , b , b_randomness_index_1, b_randomness_index_2)
            
            ## 模擬 各方 的 運算結果
            if operation_record["operation"] == "+":
                pseudo_secret_a_1 = operation_record["pseudo_secret_a_1"]
                pseudo_secret_b_1 = operation_record["pseudo_secret_b_1"]
                
                collect_shares_1 = share_list_constant_multiplication(operation_shares_a_1, pseudo_secret_b_1)
                collect_shares_2 = share_list_addition(share_list_constant_multiplication(operation_shares_a_2, pseudo_secret_b_1) , share_list_constant_multiplication(operation_shares_b_2, pseudo_secret_a_1))
            elif operation_record["operation"] == "-":
                pseudo_secret_a_1 = operation_record["pseudo_secret_a_1"]
                pseudo_secret_b_1 = operation_record["pseudo_secret_b_1"]
                
                collect_shares_1 = share_list_constant_multiplication(operation_shares_a_1, pseudo_secret_b_1)
                collect_shares_2 = share_list_minus(share_list_constant_multiplication(operation_shares_a_2, pseudo_secret_b_1) , share_list_constant_multiplication(operation_shares_b_2, pseudo_secret_a_1))
            elif operation_record["operation"] == "*":
                pseudo_secret_a_1 = operation_record["pseudo_secret_a_1"]
                pseudo_secret_b_2 = operation_record["pseudo_secret_b_2"]

                collect_shares_1 = share_list_constant_multiplication(operation_shares_b_1, pseudo_secret_a_1)
                collect_shares_2 = share_list_constant_multiplication(operation_shares_a_2, pseudo_secret_b_2)
            else:
                raise Exception("Unrecognizable operation！")

            # ==

            ## 乘上 本輪 randomness 參數 提供 share 的 隨機化，避免 本輪的 share 可用來 恢復 非本輪的 secret。
            #  (x = 運算結果 的 share，y = 乘上 randomness r)，各方在本地端計算 share_xy = 隨機化 運算結果。
            #  -> 可避免 本次恢復所需的 計算結果 share，用在補充 其他輪次不滿足恢復 threshold 的情境。 

            # 模擬 server_1、participants 操作。
            share_d1 = share_list_minus(collect_shares_1, share_a1)
            share_e1 = share_list_minus(share_y1, share_b1)

            d1 = reconstructSecret(share_d1) % PRIME 
            e1 = reconstructSecret(share_e1) % PRIME 

            share_de_1 = share_list_constant_multiplication( share_d1, e1 )
            share_bd_1 = share_list_constant_multiplication( share_b1, d1 )
            share_ae_1 = share_list_constant_multiplication( share_a1, e1 )
            share_xy_1 = share_list_addition( share_list_addition(share_de_1, share_bd_1), share_list_addition(share_ae_1, share_c1) )

            collect_shares_1 = share_xy_1

            # 模擬 server_2、participants 操作。
            share_d2 = share_list_minus(collect_shares_2, share_a2)
            share_e2 = share_list_minus(share_y2, share_b2)

            d2 = reconstructSecret(share_d2) % PRIME 
            e2 = reconstructSecret(share_e2) % PRIME 

            share_de_2 = share_list_constant_multiplication( share_d2, e2 )
            share_bd_2 = share_list_constant_multiplication( share_b2, d2 )
            share_ae_2 = share_list_constant_multiplication( share_a2, e2 )
            share_xy_2 = share_list_addition( share_list_addition(share_de_2, share_bd_2), share_list_addition(share_ae_2, share_c2) )

            collect_shares_2 = share_xy_2

        # =======

        return collect_shares_1 , collect_shares_2

    def reconstruct_MSS_Secret(self, participants, i):

        randomness_index_1, randomness_index_2 = self.RG.poly_randomness(i)

        collect_shares_1 , collect_shares_2 = self.collect_shares(participants, i , randomness_index_1, randomness_index_2)

        pseudo_secret_1 = reconstructSecret(collect_shares_1)
        pseudo_secret_2 = reconstructSecret(collect_shares_2)

        # print("i:", i , ", pseudo_secret_1:", pseudo_secret_1 , ", pseudo_secret_2:", pseudo_secret_2)

        secret = _divmod(pseudo_secret_2, pseudo_secret_1, PRIME)

        return secret % PRIME
    
    def print_operation_record(self):

        secret = self.server_1.print_operation_record()

    def scalar_multiplication(self, participants, i, num):      # Request Generation：Uploading query data
        
        operation_index = self.RG.scalar_multiplication(participants, i, num)

        return operation_index

    def compare(self, participants, a, b):
        
        result = self.server_1.compare(participants, a, b)

        # print("a =", self.reconstruct_MSS_Secret(participants, a))
        # print("b =", self.reconstruct_MSS_Secret(participants, b))
        # print("compare(a > b) =", result)

        return result
    
    # 結束一階段的運算後，確認不會在用到過去的計算結果，即可將 record 清理乾淨，節省儲存空間。
    def clear(self):
        self.update_threshold(self.revert)
        
        server_1 = self.call_server_1()
        server_1.clear_operation_record()

        RG = self.call_RG()
        RG.clear_randomness_record()

# ====

if __name__ == '__main__':

    print("\n====\n")

    # # n：參與者數量
    # n = 1
    # n = 30
    n = 10

    # # K：multi-secret list ( K < PRIME )
    # K = [0, 1]
    K = [0, 1, 130, 20, 1500, 700, 400, 2100, 2800, 1300]

    # # t：threshold list for each secret (1 <= t <= n)。
    # t = [0, 0]
    # t = [0, 11, 30, 4, 7, 13, 10]             # n = 30；threshold 非固定。
    t = [4, 4, 4, 4, 4, 4, 4, 4, 4, 4]          # n = 10；threshold 固定 (以求便於計算，可設置成非固定)。

    # Basic numbers
    B_K = [ 1 ]
    B_t = [ 1 ]

    K = B_K + K
    t = B_t + t

    # # k：secret 數量
    k = len(K)
    b_k = len(B_K)

    dealer = Dealer(n, K, t, None)

    clients = []        
    for i in range(n):
        clients.append(Client(i))

    MSS = dealer.distribute(clients)

    print("\n====\n")

    # 隨機參與者：人數 = t[i]。
    pool = random.sample(clients, t[-1])


    # 測試：每筆secret還原狀況
    test_1 = True

    for i in range(k):
        reconstruct = MSS.reconstruct_MSS_Secret(pool, i)

        if(reconstruct != K[i]):
            test_1 = False
            print("Error: Secret = " , K[i] , ", Reconstruct = " , reconstruct)
    
    if (test_1 == True):
        print("Test_1: All reconstruct success.")
    else:
        print("Test_1: There is some reconstruct error.")

    print("\n====\n")

    # 測試：原始 secret 運算狀況

    i , j = (b_k + 2) , (b_k + 3)

    operation_index_1 = MSS.addition(pool, i , j)
    reconstruct = MSS.reconstruct_MSS_Secret(pool, operation_index_1)

    print("Secret addition:" , MSS.reconstruct_MSS_Secret(pool, i) , "+" , MSS.reconstruct_MSS_Secret(pool, j))
    print("Reconstructed secret:", reconstruct)
    print()

    i , j = (b_k + 2) , (b_k + 3)

    operation_index_2 = MSS.multiplication(pool, i , j)
    reconstruct = MSS.reconstruct_MSS_Secret(pool, operation_index_2)

    print("Secret multiplication:" , MSS.reconstruct_MSS_Secret(pool, i) , "*" , MSS.reconstruct_MSS_Secret(pool, j))
    print("Reconstructed secret:", reconstruct)
    print()

    print("\n====\n")

    # 測試：運算結果 與 原始 secret 運算狀況

    i , j = (operation_index_1) , (b_k + 3)

    operation_index = MSS.addition(pool, i , j)
    reconstruct = MSS.reconstruct_MSS_Secret(pool, operation_index)

    print("Secret addition:" , MSS.reconstruct_MSS_Secret(pool, i) , "+" , MSS.reconstruct_MSS_Secret(pool, j))
    print("Reconstructed secret:", reconstruct)
    print()

    i , j = (operation_index_1) , (b_k + 3)

    operation_index = MSS.multiplication(pool, i , j)
    reconstruct = MSS.reconstruct_MSS_Secret(pool, operation_index)

    print("Secret multiplication:" , MSS.reconstruct_MSS_Secret(pool, i) , "*" , MSS.reconstruct_MSS_Secret(pool, j))
    print("Reconstructed secret:", reconstruct)
    print()

    i , j = (operation_index_1) , (operation_index_2)

    operation_index = MSS.addition(pool, i , j)
    reconstruct = MSS.reconstruct_MSS_Secret(pool, operation_index)

    print("Secret addition:" , MSS.reconstruct_MSS_Secret(pool, i) , "+" , MSS.reconstruct_MSS_Secret(pool, j))
    print("Reconstructed secret:", reconstruct)
    print()

    i , j = (operation_index_1) , (operation_index_2)

    operation_index = MSS.multiplication(pool, i , j)
    reconstruct = MSS.reconstruct_MSS_Secret(pool, operation_index)
    
    print("Secret multiplication:" , MSS.reconstruct_MSS_Secret(pool, i) , "*" , MSS.reconstruct_MSS_Secret(pool, j))
    print("Reconstructed secret:", reconstruct)
    print()

    i , j = (operation_index_1) , (operation_index_2)

    operation_index = MSS.addition(pool, i , j)
    reconstruct = MSS.reconstruct_MSS_Secret(pool, operation_index)

    print("Secret addition:" , MSS.reconstruct_MSS_Secret(pool, i) , "+" , MSS.reconstruct_MSS_Secret(pool, j))
    print("Reconstructed secret:", reconstruct)
    print()

    i , j = (operation_index_1) , (operation_index_2)

    operation_index = MSS.multiplication(pool, i , j)
    reconstruct = MSS.reconstruct_MSS_Secret(pool, operation_index)
    
    print("Secret multiplication:" , MSS.reconstruct_MSS_Secret(pool, i) , "*" , MSS.reconstruct_MSS_Secret(pool, j))
    print("Reconstructed secret:", reconstruct)
    print()

    i , j = (b_k + 0) , (b_k + 1)

    operation_index = MSS.addition(pool, i , j)
    reconstruct = MSS.reconstruct_MSS_Secret(pool, operation_index)

    print("Secret addition:" , MSS.reconstruct_MSS_Secret(pool, i) , "+" , MSS.reconstruct_MSS_Secret(pool, j))
    print("Reconstructed secret:", reconstruct)
    print()

    i , j = (b_k + 0) , (b_k + 1)

    operation_index = MSS.multiplication(pool, i , j)
    reconstruct = MSS.reconstruct_MSS_Secret(pool, operation_index)
    
    print("Secret multiplication:" , MSS.reconstruct_MSS_Secret(pool, i) , "*" , MSS.reconstruct_MSS_Secret(pool, j))
    print("Reconstructed secret:", reconstruct)
    print()

    i , j = (b_k + 1) , (b_k + 0)

    operation_index = MSS.addition(pool, i , j)
    reconstruct = MSS.reconstruct_MSS_Secret(pool, operation_index)

    print("Secret addition:" , MSS.reconstruct_MSS_Secret(pool, i) , "+" , MSS.reconstruct_MSS_Secret(pool, j))
    print("Reconstructed secret:", reconstruct)
    print()

    i , j = (b_k + 1) , (b_k + 0)

    operation_index = MSS.multiplication(pool, i , j)
    reconstruct = MSS.reconstruct_MSS_Secret(pool, operation_index)
    
    print("Secret multiplication:" , MSS.reconstruct_MSS_Secret(pool, i) , "*" , MSS.reconstruct_MSS_Secret(pool, j))
    print("Reconstructed secret:", reconstruct)
    print()

    print("\n====\n")

    MSS.print_operation_record()

    # RG = MSS.call_RG()
    # RG.print_randomness_record()

    print("\n====\n")

    i , j = (b_k + 3) , (b_k + 2)

    operation_index = MSS.minus(pool, i , j)
    reconstruct = MSS.reconstruct_MSS_Secret(pool, operation_index)

    print("Secret minus:" , MSS.reconstruct_MSS_Secret(pool, i) , "-" , MSS.reconstruct_MSS_Secret(pool, j))
    print("Reconstructed secret:", reconstruct)
    print()

    i , j = (b_k + 3) , (operation_index_1)

    operation_index = MSS.minus(pool, i , j)
    reconstruct = MSS.reconstruct_MSS_Secret(pool, operation_index)

    print("Secret minus:" , MSS.reconstruct_MSS_Secret(pool, i) , "-" , MSS.reconstruct_MSS_Secret(pool, j))
    print("Reconstructed secret:", reconstruct)
    print()

    i , j = (operation_index_1) , (operation_index_2)

    operation_index = MSS.minus(pool, i , j)
    reconstruct = MSS.reconstruct_MSS_Secret(pool, operation_index)

    print("Secret minus:" , MSS.reconstruct_MSS_Secret(pool, i) , "-" , MSS.reconstruct_MSS_Secret(pool, j))
    print("Reconstructed secret:", reconstruct)
    print()

    i , j = (b_k + 2) , (b_k + 3)

    operation_index = MSS.minus(pool, i , j)
    reconstruct = MSS.reconstruct_MSS_Secret(pool, operation_index)

    print("Secret minus:" , MSS.reconstruct_MSS_Secret(pool, i) , "-" , MSS.reconstruct_MSS_Secret(pool, j))
    print("Reconstructed secret:", reconstruct)
    print()

    i , j = (operation_index_1) , (b_k + 3)

    operation_index = MSS.minus(pool, i , j)
    reconstruct = MSS.reconstruct_MSS_Secret(pool, operation_index)

    print("Secret minus:" , MSS.reconstruct_MSS_Secret(pool, i) , "-" , MSS.reconstruct_MSS_Secret(pool, j))
    print("Reconstructed secret:", reconstruct)
    print()

    i , j = (operation_index_2) , (operation_index_1)

    operation_index = MSS.minus(pool, i , j)
    reconstruct = MSS.reconstruct_MSS_Secret(pool, operation_index)

    print("Secret minus:" , MSS.reconstruct_MSS_Secret(pool, i) , "-" , MSS.reconstruct_MSS_Secret(pool, j))
    print("Reconstructed secret:", reconstruct)
    print()

    print("\n====\n")

    scalar_error = 0
    
    '''
    for test in range(100):

        i = 0
        num = random.randint(1 , PRIME-1)

        ## scalar 的計算結果只能在正數計算，否則還原結果將出錯。
        #  因此，當需要負數的倍數時，請先 scalar 正數，再 minus。

        operation_index = MSS.scalar_multiplication(pool, i , num)

        reconstruct = MSS.reconstruct_MSS_Secret(pool, operation_index)
    
        if(reconstruct != ((num * -1) % PRIME)):
            scalar_error = scalar_error + 1
            print("[ERROR] Secret Scalar：" , "num = " + str(((num * -1) % PRIME)) , ", result = " , reconstruct)
    '''

    num = PRIME+2
    operation_index = MSS.scalar_multiplication(pool, 0 , num)
    reconstruct = MSS.reconstruct_MSS_Secret(pool, operation_index)

    print("Secret scalar: secret =" , MSS.reconstruct_MSS_Secret(pool, 0) , ", num =" , num % PRIME)
    print("Reconstructed secret:", reconstruct)
    print()

    for test in range(1000):
    
        i = 0
        num = random.randint(1 , PRIME-1)

        operation_index = MSS.scalar_multiplication(pool, i , num)

        reconstruct = MSS.reconstruct_MSS_Secret(pool, operation_index)
    
        if(reconstruct != num):
            scalar_error = scalar_error + 1
            print("[ERROR] Secret Scalar：" , "num = " + str(num) , ", result = " , reconstruct)
    
    if (scalar_error == 0):
        print("Scalar Test: All success.")
    else:
        print("\nScalar Test: There is " + str(scalar_error) + " error exist.")

    print("\n====\n")

    compare_error = 0

    echo = 100

    for test in range(echo):

        i = random.randint( b_k + 2 , k )
        j = random.randint( b_k + 2 , k )

        result = MSS.compare(pool, i , j)
    
        if((MSS.reconstruct_MSS_Secret(pool, i) > MSS.reconstruct_MSS_Secret(pool, j)) != result):
            compare_error = compare_error + 1
            print("[ERROR] Secret Compare：" , MSS.reconstruct_MSS_Secret(pool, i) , ">" , MSS.reconstruct_MSS_Secret(pool, j) , "=" , result)
    
    if (compare_error == 0):
        print("\nCompare Test: All success.")
    else:
        print("\nCompare Test: There is " + str(compare_error) + " error exist.")

    print("\n====\n")
    
    # MSS.print_operation_record()

    # print("\n====\n")