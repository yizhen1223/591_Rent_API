# 591_Rent_API
爬取rent.591.com.tw資料存入MongoDB，並設計RESTful API進行指定物件查詢。

## 爬蟲: crawler_591.py
**事前安裝套件**
```
pip install BeautifulSoup
pip install selenium
pip install requests
pip install time
pip install fake_useragent
pip install pymongo
```

## RESTful API設計: flask-restful-api.py
**事前安裝套件**
```
pip install flask
pip install flask_restx
```
#### (1) 指定地區；性別要求去查詢租屋物件
    /region={region}/gender={gender}/limit={limit}
  - region `string` 輸入指定查詢地區(1:台北市, 2:新北市)
  - gender `string` 輸入指定性別要求(0:男女皆可, 1:限男, 2:限女)，可利用&選擇多條件
  - limit `integer` 指定最多回傳的紀錄筆數，輸入0即為無設置

#### (2) 指定出租者聯絡電話去查詢租屋物件
    /renter_tel={renter_tel}/limit={limit}
  - renter_tel `string` 可輸入出租者聯絡電話進行查詢。
  - limit `integer` 指定最多回傳的紀錄筆數，輸入0即為無設置

#### (3) 查詢指定屋主身分的租屋物件
    /renter_id={renter_id}/limit={limit}
  - renter_id `string` 指定屋主身分(0:非屋主自租, 1:屋主自租)
  - limit `integer` 指定最多回傳的紀錄筆數，輸入0即為無設置

#### (4) 查詢指定地區、屋主姓氏與性別資訊之物件
    /region={region}/renter_gender={renter_gender}/renter_name={lastName}/limit={limit}
  - region `string` 輸入指定查詢地區(1:台北市, 2:新北市)
  - renter_gender `string` 指定屋主性別(0:不指定, 1:女性, 2:男性)
  - lastName `string` 指定屋主姓氏
  - limit `integer` 指定最多回傳的紀錄筆數，輸入0即為無設置

#### (5) 上述查詢都可以藉由Requestr將Body parameters的內容作為篩選條件進行查詢。(輸入格式為JSON)
    /item
- Body parameters
```
### 查詢【男生可承租】且【位於新北】的租屋物件 ###
{
    "Filter": {
        "地區": "新北市",
        "性別要求": {"$regex": "男女皆可|限男"}
    }
}

### 以【聯絡電話】查詢租屋物件 ###
{
    "Filter": {
        "聯絡電話": "0912-345-678"
    }
}

### 所有【非屋主自行刊登】的租屋物件 ###
{
    "Filter": {
        "出租者身分": {"$ne": "屋主"}
    }
}

### 【臺北】【屋主為女性】【姓氏為吳】所刊登的所有租屋物件 ###
{
    "Filter": {
        "出租者": {
            "$regex": "^吳(小姐|太太|阿姨)"
        },
        "出租者身分": "屋主",
        "地區": "台北市"
    }
}

```


## MongoDB Schema
- 目前資料庫設計
```
{
    '_id': {
        'type': 'object',
        'required': True,
        'example': ObjectId("615f388e871a89ce413f8b4")
    },
    '地區': {
        'type': 'string',
        'example': "台北市"
    },
    '性別要求': {
        'type': 'string',
        'example': "男女皆可"
    },
    '物件名稱': {
        'type': 'string',
        'example': "師大旁近捷運-1樓雅房共2間"
    },
    '出租者': {
        'type': 'string',
        'example': "黃先生"
    },
    '出租者身分': {
        'type': 'string',
        'example': "代理人"
    },
    '聯絡電話': {
        'type': 'string',
        'example': "0912-345-678"
    },
    '型態(Shape)': {
        'type': 'string',
        'example': "公寓"
    },
    '現況(Kind)': {
        'type': 'string',
        'example': "雅房"
    },
    'URL': {
        'type': 'string',
        'example': "https://rent.591.com.tw/home/123456789.html"
    }
}
```
**日後可改善成引用模式，讓相對多量的子實體(物件詳細資訊)去引用較少紀錄的主實體(固定篩選條件)**


## Reponse 範例: JSON格式回傳
**回傳範例檔案名稱**
- response_台北_吳姓女屋主.json
- response_非屋主刊登.json
```
[
  {
    "URL": "https://rent.591.com.tw/rent-detail-11474879.html",
    "出租者": "林小姐",
    "出租者身分": "仲介",
    "地區": "台北市",
    "型態(Shape)": "電梯大樓",
    "性別要求": "男女皆可",
    "物件名稱": "新川普*白色情人節*",
    "現況(Kind)": "獨立套房",
    "聯絡電話": "0932-210-399"
  }
]
```
- response_新北_男性可租.json

## API規格文件: html2-documentation-generated.zip
**Folder: api_document/**
- 使用SwaggerHub
- 下載後直接解壓縮，雙擊index.html即可開啟API文件


## 參考來源 Reference
- 591 租屋網 - 租屋資訊爬蟲
  - https://github.com/AlanSyue/rent591data
- How to create Restful CRUD API with Python Flask, MongoDB, and Docker.
  - https://ishmeet1995.medium.com/how-to-create-restful-crud-api-with-python-flask-mongodb-and-docker-8f6ccb73c5bc
- Quick start — Flask-RESTX 0.5.2.dev documentation
  - https://flask-restx.readthedocs.io/en/latest/quickstart.html
