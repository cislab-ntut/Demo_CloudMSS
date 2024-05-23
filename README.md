# DEMO_CloudMSS

> This is a Django project that demonstrates the research of "Dual-Cloud Multi-Secret Sharing Architecture for Privacy Preserving Persistent Computation".
> 
> For more details, you can find the source code and technical documentation of the infrastructure in the CloudMSS project. 

## 介紹

這是一個 CloudMSS 的演示，使用 Django 框架打造的網頁應用程序。

~~~
Preliminary on "CloudMSS" repository：

- [CloudMSS](https://github.com/stanley568598/CloudMSS)
~~~

## 功能

- [x] 系統初始化：外包資料、分發共享值。
- [x] MSS 系統展示：Server 秘密重建、Client 使用 kNN 分類服務。
- [x] 門檻值轉換器

## 檔案夾說明

本專案的檔案儲存路徑：

- Django 專案
    ~~~
    DEMO_CloudMSS ( Django web )
    ~~~

- Django 套件
    ~~~
    DEMO_CloudMSS ( Django web ) >> DEMO_web
    ~~~

- Django 應用程序
    ~~~
    DEMO_CloudMSS ( Django web ) >> my_app
    ~~~

- Django 靜態資料
    ~~~
    DEMO_CloudMSS ( Django web ) >> static
    ~~~

- Django 網頁模板
    ~~~
    DEMO_CloudMSS ( Django web ) >> templates
    ~~~

- 測試資料
    ~~~~
    testing_dataset
    ~~~~

## 安裝套件

- numpy：多維陣列與矩陣運算。

- pandas：資料操縱與分析。

- math：常用的數學函式，例如 三角函數、四捨五入、指數、對數、平方根、總和。

- django：基於 Python 的 Web 框架。

## 環境部屬介紹

### 開發環境：Django 專案

~~~
- [D:\pyTest\myweb]         # 專案的容器 (根目錄)：專案名稱，可隨意命名。
    - manage.py             # 管理專案的命令列工具：用來與專案互動的命令程式。
    - db.sqlite3            # 資料庫檔案。
    -[myweb]                # 管理專案的套件目錄：Django 專案的實際 Python 套件。
        - __init__.py       # 一個空文件，代表這個目錄是一個套件。
        - settings.py       # 本專案的環境設定檔：專案設定 / 組態檔案。
        - urls.py           # 本專案的路由設定檔：專案 URL 的宣告檔案。
        - asgi.py
        - wsgi.py           # WSGI 相容伺服器設定檔案。
~~~

### 建立應用程式 application (app)


- Django 的 MTV 架構，會讓 views.py 跟 urls.py 做呼應，並將所需傳達給前端。

- 若有自己開發的 py 檔案，可放置在此目錄下，供 my_web >> myapp >> view.py 取用。

- Migration (資料遷移)：『記錄』著 models.py 裡面所創建的資料庫型態。

    - 只要 Django 專案中的 models.py 有任何的變動，都要執行一次 migration，來同步資料庫。

    - 建立的 Migration (資料遷移) 檔案，存放在應用程式 (APP) 下的 migrations 資料夾中。
    
~~~
- [D:\pyTest\myweb\myapp]   # 應用程式套件目錄
    - __init__.py           # 空文件，代表這個目錄是一個套件。
    - admin.py              # 用來管理 APP，可設定資料庫呈現的模式，會與 models.py 溝通。
    - apps.py
    - models.py             # 用來定義 Django app 的資料庫，建構你的資料庫型態。
    - tests.py
    - views.py              # 負責接收瀏覽器的請求，進行邏輯的處理後，回傳執行結果給瀏覽器。
    -[migrations]           # 用來同步 Django 專案下 models.py 中的類別 (Class) 及資料庫。
        - __init__.py       # 空文件，代表這個目錄是一個套件。
~~~

### 建立專案所需之靜態檔案 ( static ) 目錄

- 需自己新增建立 static 資料夾，包括其中的 images / css / js 資料夾。
- 在前端 templates.html 使用 {% load static %} 讀取專案的內建檔案。

~~~
- [D:\pyTest\myweb]         # 專案目錄
    -[myapp]                # 應用程式目錄
    -[myweb]                # 專案管理目錄
    -[static]               # 網頁靜態檔案目錄
        -[images]           # 圖片檔
        -[css]              # css 檔
        -[js]               # javascript 檔
    -[templates]            # 網頁樣板檔案目錄
    - manage.py             # 管理專案的命令列工具
~~~

## 環境部屬設定

### A. 編輯專案環境設定檔：myweb/settings.py

Django 已預設將常用的 app 設定為 INSTALLED_APPS 例如：auth（認證授權管理）、admin （管理者後台）… 等等，可依需求自行增減設定專案會用到的應用程式。

1. 將應用程式 myapp 設定進去：
    ~~~
    INSTALLED_APPS = [
        'django.contrib.admin',        # 管理者後台
        'django.contrib.auth',         # 認證授權管理
        'django.contrib.contenttypes', # 內容類型管理
        'django.contrib.sessions',     # session 管理
        'django.contrib.messages',     # 訊息管理
        'django.contrib.staticfiles',  # 靜態檔案管理
        'myapp',
    ]
    ~~~

2. 設定樣板目錄的路徑：( 'DIRS': [BASE_DIR / "templates"], )。
    ~~~
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [BASE_DIR / "templates"],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]
    ~~~

3. 設定語系和時間：
    ~~~
    LANGUAGE_CODE = 'zh-Hant'

    TIME_ZONE = 'Asia/Taipei'
    ~~~

4. 增加靜態檔案的設定：
    ~~~ 
    STATIC_URL = '/static/'

    STATICFILES_DIRS = [
        BASE_DIR / "static",
    ]
    ~~~

5. 可在此建立儲存全域變數：
    ~~~ 
    GLOBAL_VARIABLE = {
        "clients" : None,
        "MSS" : None,
        "n_row" : None,
        "n_column" : None,
        "service_t" : None,
        "basic_length" : 0,
    }
    ~~~

### B. 設定網址路由：myweb/urls.py

~~~
    from django.contrib import admin
    from django.urls import path
    from myapp import views

    urlpatterns = [
        path("admin/", admin.site.urls),                        # 管理者介面
        path("", views.main),                                   # 起始畫面 (index.html)：系統初始化設定。
        path("MSS_sys/", views.MSS_sys),                        # 展示 MSS 系統：系統功能導引。
        path("recover_secret/", views.recover_secret),          # 秘密重建：Cloud Server 還原操作。
        path("kNN_service/", views.kNN_service),                # kNN 分類服務：Client 發起查詢。
        path("convert_threshold/", views.convert_threshold),    # 門檻值轉換器
        path("get_op_record/", views.get_op_record,)            # 回傳 op_record (運算操作紀錄)。
    ]
~~~

### C. 設定應用程式函數的定義：myapp\views.py

- urls.py 會引用這些函式，形成與 my_app 的溝通。
    ~~~
    from myapp import views
    ~~~

- views.py 能引用我們自己撰寫的 py 檔。
    ~~~
    from my_app.secret_sharing import reconstructSecret
    from my_app.MSS_system import *
    from my_app.kNN_service import *
    ~~~

- views.py 能讀取與寫入專案的全域參數。
    ~~~
    from django.conf import settings

    settings.GLOBAL_VARIABLE["MSS"] = MSS
    settings.GLOBAL_VARIABLE["clients"] = clients

    MSS = settings.GLOBAL_VARIABLE["MSS"]
    clients = settings.GLOBAL_VARIABLE["clients"]
    ~~~

- views.py 處理 request 和 respond。
    ~~~
    def main(request):  
    
        # 回傳 index.html (起始畫面)。
        # > 獲取系統初始化的設定參數。
        # > 將資料提交 (POST) 到 "/MSS_sys/"。

        return render(request, 'index.html', locals())
    ~~~

    ~~~
    def MSS_sys(request):
        
        if request.method == 'GET':

            # 讀取全域變數，展示 MSS 系統畫面。
            # - 系統功能導引 (UI 觸發)：
            # -> Cloud Server 的 share：開啟新視窗 (GET) 到 "/recover_secret/"。
            # -> Client 的 icon：開啟新視窗 (GET) 到 "/kNN_service/"。
            
            return render(request, 'MSS_sys.html', locals())
        
        elif request.method == 'POST':

            # 讀取解析來自 index.html 的資料。
            # - 建立 MSS 初始化 ( MSS_system_init )。
            # - 將資料儲存到專案的全域變數。
            # - 重新指向 redirect (GET) 到 "/MSS_sys/"。
            
            return redirect("/MSS_sys/")
    ~~~

    ~~~
    def recover_secret(request):

        # 秘密重建：Cloud Server 還原操作。

        if request.method == 'GET':

            # 選擇參與還原的 client。
            # - 將資料提交 (POST) 到 "/recover_secret/"。
            # - 回報執行結果：
            # -> secret： alert( 還原結果 )。
            
            return render(request, 'recover_secret.html', locals())

        elif request.method == 'POST':

            # 讀取解析來自 recover_secret.html 的資料。
            # - 執行 reconstructSecret()，取得回報資料。
            # - 重新指向 redirect (GET) 到 "/recover_secret/"。

            shares = []

            shares.extend(participant_shares_list)
            shares.extend(public_shares_list)

            # print(shares)

            secret = reconstructSecret(shares)

            return redirect("/recover_secret/?pub_shares=" + Pub_text + "&secret=" + str(secret))
    ~~~

    ~~~
    def kNN_service(request):

        # kNN 分類服務：Client 發起查詢。
        
        if request.method == 'GET':

            # 獲取查詢資料與設定參數。
            # - 將資料提交 (POST) 到 "/kNN_service/"。
            # - 回報執行結果：
            # -> result： alert( 預測結果 )。
            # -> error：alert( 執行失敗 )。
            
            return render(request, 'kNN_service.html', locals())

        elif request.method == 'POST':

            # 讀取解析來自 kNN_service.html 的資料。
            # - 執行 MSS_kNN()，整理回報內容。
            # - 重新指向 redirect (GET) 到 "/kNN_service/"。
            
            result = MSS_kNN(MSS, pool, n_row, n_column, query.values, n_neighbors)

            result = ",".join(result)

            return redirect("/kNN_service/?client=" + client_text + "&result=" + result )
    ~~~

    ~~~
    def get_op_record(request):

        # 展示執行過程：協助動態更新相關欄位內容。
        # - 回傳 op_record (運算操作紀錄)。

        return JsonResponse({'data': print_operation_record})
    ~~~

    ~~~
    def convert_threshold(request):

        # 門檻值轉換器：透過網址 (http://127.0.0.1:8000/convert_threshold/) 直接進入。
        
        if request.method == 'GET':

            # 回傳 convert_threshold.html。
            # - 獲取資料集內容和門檻值設定。
            # - 將資料提交 (POST) 到 "/convert_threshold/"。

            threshold = request.GET.get("threshold")
            
            return render(request, 'convert_threshold.html', locals())

        elif request.method == 'POST':
            
            # 讀取解析來自 convert_threshold.html 的資料。
            # - 根據門檻值，產生對應資料集大小的門檻值資料。
            # - 重新指向 redirect (GET) 到 "/convert_threshold/"。

            return redirect("/convert_threshold/?threshold=" + str(text_list))
    ~~~
    
### D. 在樣板目錄下建立網頁：templates

1. 在 static\images 目錄：儲存靜態圖片。
2. 在 static\css 目錄：建立 style.css 樣式檔。
3. 在 static\js 目錄：建立 script.js 腳本檔。
4. 在 templates 樣板目錄下新增一個 hello_django.html。

    - Template 內的 {{變數}} 會透過 views.py 將變數傳送過來。
    - {% 指令 %} 是 Template 專用語言，專為呈現顯示結果所進行的判斷 / 迴圈 / 邏輯等處理。

#### 模板繼承

通常一個網站都會規劃相同的顏色、主頁標題、主頁結尾作為母版 (或稱骨架)，然後讓所有的頁面繼承這個母版，就會有同樣的風格，未來只要修改母版就能快速更換網站風格。

- 母版設計：首先設計一個簡單的網頁與樣式表作為模板繼承的參考，挖空部份區塊作為子網頁繼承之用。

    - 使用 extends 繼承母版 base.html
        ~~~
        {% extends 'base.html'%}
        ~~~

    - 使用 block main 填寫子網頁內容：
        ~~~
        {% block main %}
        <h1>{{mainTitle}}</h1>
        <p>{{mainContent}}</p>
        ...
        {% endblock %}
        ~~~

## 系統運行

### Django 的 DEBUG 模式

在 settings.py 檔案中有一個變數為 DEBUG

- 預設值是 DEBUG = True。

- 當 DEBUG = True 時的好處為

    - 如果開啟了 DEBUG 模式，那麼以後當我們修改了 Django 項目的程式碼，然後按下 ctrl + s，就會自動的重啟項目，不需要手動重啟。

    - 如果開啟了 DEBUG 模式，那麼以後 Django 專案中的程式碼出現 bug 了，那麼在瀏覽器中和控制台會列印出錯訊息。否則的我們很難找到 bug 的位置，也不方便調試程式碼。
    
- 在正式環境中，禁止開啟 DEBUG = True，因為當你的網站出錯誤時，別人能看到你的原始碼，而我們也不需要給使用者看到這些錯誤訊息。

    - 如果設定了 DEBUG = False，那麼就必須設定 settings.py 中的 ALLOWED_HOSTS。

    - ALLOWED_HOSTS：這個變數是用來設定以後別人只能透過這個變數中的 ip 位址或網域名稱來進行存取。

### 啟動網頁伺服器進行測試

- 以下指令可啟動內建的簡易網頁伺服器，以測試 Django 功能是否正常。
    ~~~
    D:\pyTest>cd myweb                        # 進入 myweb 專案目錄
    D:\pyTest\myweb>py manage.py runserver    # 啟動 web server
    ~~~

- 執行上述指令後會產生以下回應
    ~~~
    Watching for file changes with StatReloader
    Performing system checks...

    System check identified no issues (0 silenced).

    You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
    Run 'python manage.py migrate' to apply them.
    May 27, 2021 - 00:59:57
    Django version 3.2.3, using settings 'myweb.settings'
    Starting development server at http://127.0.0.1:8000/
    Quit the server with CTRL-BREAK.
    ~~~

- 此時不要關閉命令視窗，以瀏覽器開啟 http://127.0.0.1:8000/ 將開啟 Django 專案的網頁。

- 若想結束連線，可於命令視窗，按 Ctrl + C 終止執行。

### 資料格式

- 本專案可接受的資料樣態
    
    ~~~
    數值類型的資料 * n + 類別標籤 ( 不限數值類型 ) 
    ~~~

    - 範例：(逗號之間請勿填充空白格，以免程式讀取方式出錯)
        
        ~~~
        5.1,3.5,1.4,0.2,Iris-setosa
        4.9,3.0,1.4,0.2,Iris-setosa
        ~~~

- 測試資料集 ( testing_dataset ) 介紹

    - iris.data
        
        - 此資料集包含 3 個類別，每個類別有 50 個實例。
        - 每個實例都是一棵鳶尾植物的特徵。
        - 其中一類與其他兩類可線性分割，後者彼此不可線性分割。
        - 預測目標是鳶尾屬植物的分類。

        ~~~
        - Name：鳶尾花資料集
        - Attributes：
            1. Sepal length: 花萼長度 (cm)
            2. Sepal width: 花萼寬度 (cm)
            3. Petal length: 花瓣長度 (cm)
            4. Petal width: 花瓣寬度 (cm)
            5. Labels：
                - setosa: 山鳶尾
                - versicolor: 變色鳶尾
                - virginica: 維吉尼亞鳶尾
        - Size：150 (Instances) x 5 (Features)
        ~~~

    - data_banknote_authentication.data

        - 數據是從真品和偽造的類似鈔票樣本的圖像中提取的。
        - 對於數位化 (digitization)，使用通常用於印刷檢查的工業相機，最終影像的像素為 400 x 400。
        - 由於物鏡和與被調查物體的距離，因此獲得了分辨率約為 660 dpi 的灰階圖片。
        - 使用 小波變換 ( Wavelet Transform ) 工具用於從影像中提取特徵。  
        - 預測目標是為評估紙幣真偽程序而拍攝圖像的分類。

        ~~~
        - Name：鈔票真偽認證
        - Attributes：
            1. variance of Wavelet Transformed image (continuous)：小波轉換影像的變異數
            2. skewness of Wavelet Transformed image (continuous)：小波轉換影像的偏度
            3. curtosis of Wavelet Transformed image (continuous)：小波轉換影像的陡度
            4. entropy of image (continuous)：影像的熵值
            5. class (integer)：0 / 1
        - Size：1372 (Instances) x 5 (Features)
        ~~~

## Demo

0. 使用【py manage.py runserver】啟動 web server。
    
    > 在 Django 專案，打開命令提示視窗，啟動伺服器。
    
    > 注意：保持運行，請勿關閉命令視窗。 
    
    > 指令位置：DEMO_CloudMSS ( Django web )

    ![runserver](./assets/images/0.%20runserver.JPG)

1. 開啟網頁【 http://127.0.0.1:8000/ 】，進入起始畫面。

    ![index](./assets/images/1.%20index.JPG)

2. 設定參與者數量資料，按下開始輸入資料。

    ![start](./assets/images/2-1.%20開始輸入資料.JPG)
    ![start](./assets/images/2-2.%20開始輸入資料.JPG)

3. 檢查【測試資料集】：iris.data。

    ![dataset](./assets/images/3.%20測試資料集.JPG)

4. 輸入【外包資料】：保留測試用的查詢資料。

    > 情境：假設多個參與者(感測器)，他們只有自己的資料，例如各自知道某一個類別的相關特徵。

    > 接著，其他使用者想分辨一個未知事物，只要得到足夠的授權，即可完成查詢服務。

    ![outsource](./assets/images/4.%20外包資料.JPG)

5. 開啟網頁【 http://127.0.0.1:8000/convert_threshold/ 】。

    ![convert_threshold](./assets/images/5.%20門檻值轉換器.JPG)

    - 左格：輸入外包資料，下方欄位給定門檻值，按下送出。

        ![convert_threshold - input](./assets/images/5-1-1.%20門檻值轉換器.JPG)
    
    - 右格：輸出對應的門檻表。

        ![convert_threshold - output](./assets/images/5-1-2.%20門檻值轉換器.JPG)

6. 輸入【門檻值】，按下送出，開始【系統初始化】。
    
    > 選擇 ( t = 1 , t = 3 , t = 2 ) 的門檻值。
    
    ![initial](./assets/images/6.%20系統初始化.JPG)

7. MSS 系統：多個 client + 雙雲服務器。

    ![index](./assets/images/7-1.%20MSS%20系統%20%20(%20t%20=%201%20).JPG)

    > t = 1：任意一個以上的 client + Cloud Server 可還原秘密值。 
    
    ![index](./assets/images/7-2.%20MSS%20系統%20(%20t%20=%203%20).JPG)
          
    > t = 3：任意三個以上的 client + Cloud Server 可還原秘密值。 
  
    ![index](./assets/images/7-3.%20MSS%20系統%20(%20t%20=%202%20).JPG)

    > t = 2：任意兩個以上的 client + Cloud Server 可還原秘密值。 

8. 秘密重建：點擊 Cloud Server 的公用共享，跳出【秘密重建】功能。
    
    > CloudMSS 用「掩碼」將秘密轉換成「遮掩資料」，並且分別存取到 Cloud Server 1 和 Cloud Server 2。

    - Cloud Server 1：秘密重建 - 掩碼。

        ![index](./assets/images/8-1-0.%20Cloud_server_1%20UI.JPG)

        1. 自動帶入 Cloud Server 1 公用共享。

            ![index](./assets/images/8-1-1.%20秘密重建.JPG)
            ![index](./assets/images/8-1-2.%20秘密重建.JPG)

        2. 選擇參與還原工作的協力者。

            ![index](./assets/images/8-1-3.%20秘密重建.JPG)

        3. 取得「還原結果」。

            ![index](./assets/images/8-1-4.%20秘密重建.JPG)

    - Cloud Server 2：秘密重建 - 遮掩資料。

        ![index](./assets/images/8-2-0.%20Cloud_server_2%20UI.JPG)

        1. 自動帶入 Cloud Server 1 公用共享。

            ![index](./assets/images/8-2-1.%20秘密重建.JPG)
            ![index](./assets/images/8-2-2.%20秘密重建.JPG)

        2. 選擇參與還原工作的協力者。

            ![index](./assets/images/8-2-3.%20秘密重建.JPG)

        3. 取得「還原結果」。

            ![index](./assets/images/8-2-4.%20秘密重建.JPG)

    - 取得「掩碼」和「遮掩資料」的還原值，可重建秘密值。

        > 掩碼 = 1；遮掩資料 = 3；秘密 = ( 遮掩資料 / 掩碼 ) = 3

        ![index](./assets/images/8-3.%20秘密重建.JPG)

9. kNN 分類服務：點擊 Client，跳出【kNN 分類服務】功能。

    ![index](./assets/images/9-0.%20Client%20UI.JPG)
    
    - 自動帶入 Client 視角：預設「參與人數」和「k 值」。

        > 參與人數的預設值：是 kNN 至少需要滿足的門檻值。
        
        > 這裡填入的參與人數，將隨機抽取 clients 協助運算。

        ![index](./assets/images/9-1-2.%20MSS_kNN.JPG)
        ![index](./assets/images/9-1-3.%20MSS_kNN.JPG)

    - 填入【查詢資料】，按下 MSS_kNN 開始運算。

        ![index](./assets/images/9-2.%20MSS_kNN.JPG)

    - 運算過程：只會在 Cloud Server 產生資料。

        ![index](./assets/images/9-3.%20MSS_kNN.JPG)

    - 取得「預測結果」。

        ![index](./assets/images/9-4.%20MSS_kNN.JPG)

    - 對照預期的查詢輸出。

        ![index](./assets/images/9-5.%20MSS_kNN.JPG)

    - 參與人數未達門檻值。

        ![index](./assets/images/10-0.%20Fail.JPG)

        ![index](./assets/images/10-1.%20Fail.JPG)

10. 結束連線：【Ctrl + C】終止執行。

    ![index](./assets/images/11.%20Close.JPG)
