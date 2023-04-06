import os
from flask import Flask, jsonify, request, g
from flask_restful import Resource, Api
from helpers import urgent2k_token_required #service_col, medicine_col, diagnosis_col
from pymongo import MongoClient
from marshmallow import fields, Schema
from datetime import datetime
#from bson import ObjectId
urgent2k_token = os.environ.get("URGENT_2K_KEY")


# creating the flask app
app = Flask(__name__)
# creating an API object
api = Api(app)

client = MongoClient(os.getenv("MONGO_URI"))
db = client.schema_data
service_col = db.services
medicine_col = db.medicine
diagnosis_col = db.diagnosis

current_date = datetime.now()

def check_exp(exp_date):
    today = current_date - exp_date.utcnow()
    if today.days > 14:
        return "expired"
    else:
        return "active"


class Diagnose(Schema):
    diagnosis = fields.Str(required=True)
    facility_no = fields.Int(required=True)


class Serivces(Schema):
    services = fields.List(fields.Dict(required=True), required=True)
    facility_no = fields.Int(required=True)

class Drugs(Schema):
    drugs = fields.List(fields.Dict(required=True), required=True)
    facility_no = fields.Int(required=True)



# class Home(Resource):

#     def get(self):
#         return {'message': "Welcome to the homepage of this webservice."}
# api.add_resource(Home,'/')

# class GetServices(Resource):
    
#     def get(self):
#         data = service_col.find()
#         service_list = list()
#         for i in data:
#             service_list.append(i.get("service"))
#         return {"status": True, "message":"Services have been retrieved successfully", "data": service_list }, 200
# api.add_resource(GetServices,'/get/services')

# class GetDiagnosis(Resource):
    
#     def get(self):
#         data = diagnosis_col.find()
#         diagnosis_list = list()
#         for i in data:
#             diagnosis_list.append(i.get("diagnosis"))
#         return {"status": True, "message":"Diagnosis have been retrieved successfully", "data": diagnosis_list }, 200
# api.add_resource(GetDiagnosis,'/get/diagnosis')

# class GetDrugs(Resource):
    
#     def get(self):
#         data = medicine_col.find({},{ "_id": 0,"price": 0 })
#         medicine_list = list()
#         for i in data:
#             medicine_list.append(i)
#         return {"status": True, "message":"List of drugs has been retrieved successfully", "data": medicine_list }, 200
# api.add_resource(GetDrugs,'/get/drugs')

@app.route('/', methods = ['GET', 'POST'])
def home():
    mon = g.get('mongo')
    if(request.method == 'GET'):
        #for i in mon.db.encounters.find():
        x = mon.db.encounters.find_one()
        #data = {'message': mon.db.encounters.find() }
        return jsonify(data=x, status=True)
    
@app.route('/get/services', methods = ['GET'])
def get_services():
    data = service_col.find()
    service_list = list()
    for i in data:
        service_list.append(i.get("service"))

    return {"status": True, "message":"Services have been retrieved successfully", "data": service_list }

@app.route('/get/diagnosis', methods = ['GET'])
def get_diagnosis():
    data = diagnosis_col.find()
    diagnosis_list = list()
    for i in data:
        diagnosis_list.append(i.get("diagnosis"))

    return {"status": True, "message":"Diagnosis have been retrieved successfully", "data": diagnosis_list }

#@app.route('/get/drugs', methods = ['GET'])
def get_drugs():
    data = medicine_col.find({},{ "_id": 0,"price": 0 })
    # medicine_list = list()
    # for i in data:
    #     medicine_list.append(i)

    return {"status": True, "message":"List of drugs has been retrieved successfully", "data": data }


# @app.route("/add/encounter", methods=["POST"])
# #@api_required
# def AddEncounter():
#     mon = g.get('mongo')
#     data = request.get_json()
#     en_result = mon.db.encounters.find_one({"code": data["encounter_code"], "archive": False})
#     staff_result = mon.db.facilities.find_one({"$or": [{"oic_number": data["facility_no"]},
#                                                        {"name.id": int(data["facility_no"])}]})
#     if len(data["encounter_code"]) == 6:
#         return {"message": "You can't add service for a referral", "status": False}

#     if not en_result:
#         return {"message": "Invalid encounter code", "status": False}
#     if not staff_result:
#         return {"message": "Number not authorized", "status": False}

#     if en_result["facility"]["id"] != (staff_result["name"]["id"]):
#         return {"message": "You can't add services for encounter not created by your facility", "status": False}

#     active_encounter = check_exp(en_result["date"])
#     if active_encounter == "expired":
#         return {"message": "encounter expired", "status": False}
#     encounter_type = "services" if data["type"] == "service" else "drug"
#     Today = datetime.now()
#     mon.db.encounters.update_one({"_id": ObjectId(en_result["_id"]), "code": data["encounter_code"]}, {
#         "$push": {encounter_type: {"date": Today, "service": data["service"],
#                                "facility": en_result["facility"]}}})

#     return {"message": f"Service {data['service']['serviceName']} added", "status": True}

@app.route("/encounters/<string:code>/diagnosis", methods=["PUT"])
#@api_required
def diagnose_encounter(code):
    mon = g.get('mongo')
    
    try:
        data = request.get_json()
        payload = Diagnose().load(data)
        doc = {"date": str(current_date),
               "diagnosis": payload["diagnosis"]
               }
        query = {"active": "approved", "type": "referral"} if len(code) == 6 else {"type": "encounter"}
        record = mon.db.encounters.find_one_and_update({"code": code, "facility.id": payload["facility_no"],
                                                        "archive": False, **query},
                                                       {"$push": {"diagnosis": doc}})
        if not list(record):
            jsonify(message=f"No record found for {code}", status=False)
    except Exception as e:
        return jsonify(message=f"An exception occurred: {e}", status=False)
    else:
        return jsonify(message="diagnosis recorded", status=True)
    
@app.route('/encounters/<string:code>/services', methods=["PUT"])
#@api_required
def encounters_services(code):
    mon = g.get('mongo')
    try:
        data = request.get_json()
        payload = Serivces().load(data)
        services = []
        for x in payload["services"]:
            x.update({"date": str(current_date)})
            services.append(x)
        query = {"active": "approved", "type": "referral"} if len(code) == 6 else {"type": "encounter"}
        record = mon.db.encounters.find_one_and_update({"code": code, "facility.id": payload["facility_no"],
                                                        "archive": False, "diagnosis": {"$ne": []},**query},
                                                       {"$push": {"services": {"$each": services}}})
        if not record:
            return jsonify(message=f"No diagnosis found for {code} ", status=False)

    except Exception as e:
        return jsonify(message=f"An exception occurred: {e}", status=False)
    else:
        return jsonify(message="Services recorded", status=True)

@app.route('/encounters/<string:code>/drugs', methods=["PUT"])
#@api_required
def encounters_drugs(code):
    mon = g.get('mongo')
    try:
        data = request.get_json()
        payload = Drugs().load(data)
        drugs = []
        for x in payload["drugs"]:
            x.update({"date": str(current_date)})
            drugs.append(x)
        query = {"active": "approved", "type": "referral"} if len(code) == 6 else {"type": "encounter"}
        record = mon.db.encounters.find_one_and_update({"code": code, "facility.id": payload["facility_no"],
                                                        "archive": False, **query},
                                                       {"$push": {"drugs": {"$each":drugs}}})
        if not record:
            return jsonify(status=False, message=f"no record found for {code}")
    except Exception as e:
        return jsonify(message=f"An exception occurred: {e}", status=False)
    else:
        return jsonify(message="Drugs recorded", status=True)
    
if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)
#print(os.environ.get("URGENT_2K_KEY"))
#print(get_drugs())


# for i in mon.db.encounters.find():
#     print(i)