from django.shortcuts import render, redirect

from django.http import HttpResponse
from django.http import Http404
# from django.shortcuts import get_object_or_404, get_list_or_404 # 快捷函数

from django.http import JsonResponse
import json
import urllib
import urllib.parse

from django.contrib import auth

from django.conf import settings

import pandas as pd
import random

from my_app.secret_sharing import reconstructSecret
from my_app.MSS_system import *
from my_app.kNN_service import *

# Create your views here.

def main(request):

    return render(request, 'index.html', locals())

def MSS_sys(request):
    
    if request.method == 'GET':
        
        clients = settings.GLOBAL_VARIABLE["clients"]

        MSS = settings.GLOBAL_VARIABLE["MSS"]

        basic_length = settings.GLOBAL_VARIABLE["basic_length"]

        cloud_server_1 = MSS.call_server_1().share[ basic_length : ]
        cloud_server_2 = MSS.call_server_2().share[ basic_length : ]

        return render(request, 'MSS_sys.html', locals())
    
    elif request.method == 'POST':

        num = int(request.POST.get("num"))

        textarea_K = []
        textarea_t = []

        for i in range(num):
            input_K = request.POST.get( "textarea_K_" + str(i) ).strip()
            input_t = request.POST.get( "textarea_t_" + str(i) ).strip()
    
            if(input_K != ""):
                textarea_K.append( input_K )
            if(input_t != ""):
                textarea_t.append( input_t )

        # print(textarea_K)
        # print(textarea_t)
        
        li_K = []
        for text_K in textarea_K:
            temp_K = pd.DataFrame( [ x.split(',') for x in text_K.split('\r\n') ] )
            li_K.append(temp_K)

        df_K = pd.DataFrame()
        if(li_K != []):
            df_K = pd.concat(li_K, axis=0, ignore_index = True)

        # print(df_K)

        li_t = []
        for text_t in textarea_t:
            temp_t = pd.DataFrame( [ x.split(',') for x in text_t.split('\r\n') ] )
            li_t.append(temp_t)

        df_t = pd.DataFrame()
        if(li_t != []):
            df_t = pd.concat(li_t, axis=0, ignore_index = True)

        # print(df_t)

        # ====

        df_data = pd.DataFrame()
        df_label = pd.DataFrame()

        if(not df_K.empty):
            df_data = df_K.drop(df_K.columns[-1], axis=1)
            df_label = df_K[df_K.columns[-1]]

        label = df_label.values

        for idx in df_data:
            df_data[idx] = pd.to_numeric(df_data[idx], errors='coerce')
            df_t[idx] = pd.to_numeric(df_t[idx], errors='coerce')

        # ====

        MSS, clients, n_row, n_column, service_t, basic_length = MSS_system_init(df_data, label, num, df_t)

        settings.GLOBAL_VARIABLE["clients"] = clients
        settings.GLOBAL_VARIABLE["MSS"] = MSS
        settings.GLOBAL_VARIABLE["n_row"] = n_row
        settings.GLOBAL_VARIABLE["n_column"] = n_column
        settings.GLOBAL_VARIABLE["service_t"] = service_t
        settings.GLOBAL_VARIABLE["basic_length"] = basic_length

        print(n_row, n_column, service_t)
        
        return redirect("/MSS_sys/")

def kNN_service(request):
    
    if request.method == 'GET':

        result_text = request.GET.get("result")

        if(result_text != None):

            result = result_text.split(",")

        error = request.GET.get("error")

        client = request.GET.get("client")

        service_t = settings.GLOBAL_VARIABLE["service_t"]

        MSS = settings.GLOBAL_VARIABLE["MSS"]

        cloud_server_1 = MSS.call_server_1()
        
        return render(request, 'kNN_service.html', locals())

    elif request.method == 'POST':

        client_text = request.POST.get("client_text").strip()
    
        query_text = request.POST.get("query").strip()

        participant_text = request.POST.get("participant").strip()

        n_neighbors_text = request.POST.get("n_neighbors").strip()
        
        query = pd.DataFrame( [ x.split(',') for x in query_text.split('\r\n') ] )

        for idx in query:
            query[idx] = pd.to_numeric(query[idx], errors='coerce')
        
        participant = int(participant_text)

        n_neighbors = int(n_neighbors_text)

        service_t = settings.GLOBAL_VARIABLE["service_t"]

        if(participant < service_t):

            return redirect("/kNN_service/?client=" + client_text + "&error=Please give more clients to reach the threshold.")
        
        else:

            MSS = settings.GLOBAL_VARIABLE["MSS"]

            clients = settings.GLOBAL_VARIABLE["clients"]

            pool = random.sample(clients, participant)

            n_row = int(settings.GLOBAL_VARIABLE["n_row"])
            n_column = int(settings.GLOBAL_VARIABLE["n_column"])

            result = MSS_kNN(MSS, pool, n_row, n_column, query.values, n_neighbors)

            result = ",".join(result)

            return redirect("/kNN_service/?client=" + client_text + "&result=" + result )

def get_op_record(request):

    MSS = settings.GLOBAL_VARIABLE["MSS"]

    cloud_server_1 = MSS.call_server_1()

    print_operation_record = cloud_server_1.print_operation_record()

    # print(print_operation_record)

    return JsonResponse({'data': print_operation_record})

def recover_secret(request):
    
    if request.method == 'GET':

        Pub = request.GET.get("pub_shares")

        secret = request.GET.get("secret")

        clients = settings.GLOBAL_VARIABLE["clients"]
        
        return render(request, 'recover_secret.html', locals())

    elif request.method == 'POST':
    
        Pub_text = request.POST.get("pub_shares")

        participant_shares_text = request.POST.get("selected_clients_text")

        # print(participant_shares_text)
        # print(Pub_text)

        participant_shares_list = eval(participant_shares_text)
        
        public_shares_list = eval(Pub_text)

        # print(participant_shares_list)
        # print(public_shares_list)

        shares = []

        shares.extend(participant_shares_list)
        shares.extend(public_shares_list)

        # print(shares)

        secret = reconstructSecret(shares)

        return redirect("/recover_secret/?pub_shares=" + Pub_text + "&secret=" + str(secret))

def convert_threshold(request):
    
    if request.method == 'GET':

        threshold = request.GET.get("threshold")
        
        return render(request, 'convert_threshold.html', locals())

    elif request.method == 'POST':
        
        data_text = request.POST.get("data").strip()

        t = int(request.POST.get("t").strip())
        
        data = pd.DataFrame( [ x.split(',') for x in data_text.split('\r\n') ] )

        if(not data.empty):
            data = data.drop(data.columns[-1], axis=1)

        for idx in data:
            data[idx] = t
        
        # 將 DataFrame 轉換成一列一列的文字
        text_list = []
        for index, row in data.iterrows():
            text = ','.join([str(value) for value in row.values])
            text_list.append(text)

        text_list = "\r\n".join(text_list)

        return redirect("/convert_threshold/?threshold=" + str(text_list))
