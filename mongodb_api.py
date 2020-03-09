from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import json
import datetime
from flask_caching import Cache

now = datetime.datetime.now()
date=str(now.year)+str(now.month)+str(now.day)
date='202038'

app = Flask(__name__)

app.config["JSON_AS_ASCII"] = False
app.config["MONGO_URI"] = "mongodb://localhost:27017/591_rent_house"
app.config["CACHE_TYPE"] = 'simple'

cache = Cache(app)
cache_time=300

mongo = PyMongo(app)
collection=mongo.db[date]

@app.route("/multi", methods=['GET'])
def query_multi_conditions():
    conditions=[]
    for key in request.args:
        conditions.append({key:request.args[key]})
    data = collection.find({'$and':conditions},{'_id':0})
    result=[i for i in data]
    return jsonify(result)

# 【男生可承租】且【位於新北】
@app.route("/male_newtaipei", methods=['GET'])
@cache.cached(cache_time)
def query_male_newtaipei():
    data = collection.find({'$and':[{'regionname':'新北市'},{'sex_criteria':{'$ne':'f'}}]},{'_id':0})
    result=[i for i in data]
    return jsonify(result)

# 【非屋主自行刊登】
@app.route("/notpostbyowner", methods=['GET'])
@cache.cached(cache_time)
def query_notpostbyowner():
    data = collection.find({'identification':{'$ne':'屋主'}},{'_id':0})
    result=[i for i in data]
    return jsonify(result)

# 【臺北】【屋主為女性】【姓氏為吳】
@app.route("/taipemswu", methods=['GET'])
@cache.cached(cache_time)
def query_taipemswu():
    data = collection.find({'$and':[{'regionname':'台北市'},{'identification':'屋主'}
                                        ,{'$or':[{'name':{'$regex':'姐$'}}
                                                 ,{'name':{'$regex':'媽媽$'}}
                                                 ,{'name':{'$regex':'嬤$'}}
                                                 ,{'name':{'$regex':'太太$'}}
                                                 ,{'name':{'$regex':'女士$'}}
                                                ,{'name':{'$regex':'姨$'}}]}
                                        ,{'name':{'$regex':'^吳'}}]}
                              ,{'_id':0})
    result=[i for i in data]
    return jsonify(result)

# 【聯絡電話】
@app.route("/phone", methods=['GET'])
def query_phone():

    if 'phone' in request.args:
        phone = request.args['phone']
    else:
        return "Error: No phone provided. Please specify a phone."
    
    data = collection.find({'phone':{'$regex':'^'+phone}},{'_id':0})
    result=[i for i in data]
    return jsonify(result)
                               
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)