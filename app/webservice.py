import os
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from app.helpers import urgent2k_token_required, service_col, medicine_col, diagnosis_col
from config import*
urgent2k_token = os.environ.get("URGENT_2K_KEY")


# creating the flask app
app = Flask(__name__)
# creating an API object
api = Api(app)

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
    if(request.method == 'GET'):
  
        data = {'message': "Welcome to the homepage of this webservice."}
        return jsonify(data)
    
@app.route('/get/services', methods = ['GET'])
def get_services():
    data = service_col.find()
    service_list = list()
    for i in data:
        service_list.append(i.get("service"))

    return jsonify({"status": True, "message":"Services have been retrieved successfully", "data": service_list })

@app.route('/get/diagnosis', methods = ['GET'])
def get_diagnosis():
    data = diagnosis_col.find()
    diagnosis_list = list()
    for i in data:
        diagnosis_list.append(i.get("diagnosis"))

    return jsonify({"status": True, "message":"Diagnosis have been retrieved successfully", "data": diagnosis_list })

@app.route('/get/drugs', methods = ['GET'])
def get_drugs():
    data = medicine_col.find({},{ "_id": 0,"price": 0 })
    medicine_list = list()
    for i in data:
        medicine_list.append(i)

    return jsonify({"status": True, "message":"List of drugs has been retrieved successfully", "data": medicine_list })

