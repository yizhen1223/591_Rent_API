#!/usr/bin/env python
# coding: utf-8

from flask import Flask, request, json, Response
from flask_restx import Resource, Api
from pymongo import MongoClient
from urllib import parse  # 若有輸入中文，則需要進行URL解碼

# MongoAPI將接收API包裝好的篩選條件
# 利用mongodb指定的collection進行查詢
# 回傳查詢結果所有欄位(除了mongodb的_id)
# limit限制回傳紀錄筆數，預設無設定則回傳50筆
class MongoAPI:
    def __init__(self, data, limit=50):
        self.client = MongoClient("mongodb://localhost:27017/")
        cursor = self.client["591_crawler"]
        self.collection = cursor["item"]
        self.data = data
        self.limit = limit

    def read(self):
        if "Filter" in self.data:
            documents = self.collection.find(filter=self.data["Filter"]).limit(self.limit)
        else:
            documents = self.collection.find().limit(self.limit)

        output = [{item: row[item] for item in row if item != '_id'} for row in documents]
        return output

app = Flask(__name__)
api = Api(app, title="591 Rent API", description="提供591租屋物件查詢之api")

# (1)選擇地區與性別要求
# 輸入指定數值後利用dict轉成指定字串
# 性別要求中可使用&符號連結不同設定，但&會被編譯成%26，需要進行URL解碼
@api.route('/region=<string:region>/gender=<string:gender>/limit=<int:limit>')
@api.param('region', description='輸入指定查詢地區(1:台北市, 2:新北市)')
@api.param('gender', description='輸入指定性別要求(0:男女皆可, 1:限男, 2:限女)，可利用&選擇多條件')
@api.param('limit', description='指定最多回傳的紀錄筆數，輸入0即為無設置')
class API_by_region_gender(Resource):
    def get(self, region, gender, limit):
        region_dict={
            "1": "台北市", "2" : "新北市"
        }
        gender_dict = {
            "0": "男女皆可", "1": "限男", "2": "限女"
        }
        gender = parse.unquote(gender)
        if "&" in gender:
            gender_ls=gender.split("&")
            gender_temp=[]
            for i in gender_ls:
                gender_temp.append(gender_dict[i])
            gender_condtion = { "$in" : gender_temp }
        else :
            gender_condtion = gender_dict[gender]

        data = {
            "Filter": {
                "地區": region_dict[region],
                "性別要求":gender_condtion
            }
        }

        db_obj = MongoAPI(data, limit)
        response = db_obj.read()
        return Response(response=json.dumps(response),
                        status=200,
                        mimetype='application/json')

# (2)利用連絡電話查詢物件
@api.route('/renter_tel=<string:renter_tel>/limit=<int:limit>', methods=['GET'])
@api.param('limit', description='指定最多回傳的紀錄筆數，輸入0即為無設置')
@api.param('renter_tel', description='可輸入出租者聯絡電話進行查詢。')
class API_by_renter_tel(Resource):
    def get(self, renter_tel, limit):
        data = {
            "Filter": {
                "聯絡電話": renter_tel
            }
        }
        db_obj = MongoAPI(data, limit)
        response = db_obj.read()
        return Response(response=json.dumps(response),
                        status=200,
                        mimetype='application/json')

# (3)查詢指定屋主身分的租屋物件
# 輸入指定數值後利用dict轉成指定字串
# 非屋主的篩選條件使用正規表達式中$ne不包含指定字串進行篩選
@api.route('/renter_id=<string:renter_id>/limit=<int:limit>')
@api.param('limit', description='指定最多回傳的紀錄筆數，輸入0即為無設置')
@api.param('renter_id', description='指定屋主身分(0:非屋主自租, 1:屋主自租)')
class API_by_renterID(Resource):
    def get(self, renter_id, limit):
        renter_id_dict = {
            "1": "屋主", "0": {"$ne": "屋主"}
        }
        data = {
            "Filter": {
                "出租者身分": renter_id_dict[renter_id]
            }
        }
        db_obj = MongoAPI(data, limit)
        response = db_obj.read()
        return Response(response=json.dumps(response),
                        status=200,
                        mimetype='application/json')

# (4)查詢指定地區、屋主姓氏與性別資訊之物件
# 除了姓氏，其餘輸入指定數值後利用dict轉成指定字串，中文姓氏需要進行URL解碼
# 使用正規表達式($regex)進行篩選
# ^(吳)：開頭為吳；(小姐|太太|阿姨)：含其中一字串
@api.route('/region=<string:region>/renter_gender=<string:renter_gender>/renter_name=<string:lastName>/limit=<int:limit>')
@api.param('region', description='輸入指定查詢地區(1:台北市, 2:新北市)')
@api.param('renter_gender', description='指定屋主性別(0:不指定, 1:女性, 2:男性)')
@api.param('lastName', description='指定屋主姓氏')
@api.param('limit', description='指定最多回傳的紀錄筆數，輸入0即為無設置')
class API_by_renter(Resource):
    def get(self, region, renter_gender, lastName, limit):
        lastName = parse.unquote(lastName)
        region_dict = {
            "1": "台北市", "2": "新北市"
        }
        renter_gender_dict = {
            "0": "", "1": "(姊|小姐|太太|阿姨)", "2": "(先生|大哥)"
        }
        renter_condition = "^%s%s" % (lastName, renter_gender_dict[renter_gender])
        data = {
            "Filter": {"出租者": { "$regex": renter_condition },
                       "出租者身分": "屋主", "地區": region_dict[region]
            }
        }
        db_obj = MongoAPI(data, limit)
        response = db_obj.read()
        return Response(response=json.dumps(response),
                        status=200,
                        mimetype='application/json')

# (5)以傳送Request進行物件篩選
@api.route('/item')
class API_by_request(Resource):
    def get(self):
        # data = request.json
        data = request.get_json()
        # data = request.args
        if data is None or data == {}:
            return Response(response=json.dumps({"Error": "Please provide connection information"}),
                            status=400,
                            mimetype='application/json')
        api_obj = MongoAPI(data)
        response = api_obj.read()
        return Response(response=json.dumps(response),
                        status=200,
                        mimetype='application/json')


if __name__ == '__main__':
    # host='0.0.0.0' 內部其他網路可以連線，測試時使用
    app.run(debug=True, port=5001, host='0.0.0.0')