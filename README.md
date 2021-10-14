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


## MongoDB Schema

有更好的改善空間

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
**PATH: api_document/**
- 使用Swagger
- 下載後直接解壓縮，雙擊index.html即可開啟API文件


### Reference
- 591 租屋網 - 租屋資訊爬蟲
  - https://github.com/AlanSyue/rent591data
- How to create Restful CRUD API with Python Flask, MongoDB, and Docker.
  - https://ishmeet1995.medium.com/how-to-create-restful-crud-api-with-python-flask-mongodb-and-docker-8f6ccb73c5bc
- Quick start — Flask-RESTX 0.5.2.dev documentation
  - https://flask-restx.readthedocs.io/en/latest/quickstart.html
