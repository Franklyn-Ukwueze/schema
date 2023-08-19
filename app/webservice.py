import os
from flask import Flask, jsonify, request, g
from flask_restful import Resource, Api, reqparse
from flask_pymongo import PyMongo
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

mongo_uri = os.environ.get("MONGO_URI_2")
mongo = PyMongo(app, uri=mongo_uri)


current_date = datetime.now()

def check_exp(exp_date):
    today = current_date - exp_date.utcnow()
    if today.days > 14:
        return "expired"
    else:
        return "active"


class Diagnose(Schema):
    diagnosis = fields.List(fields.Dict(required=True), required=True)
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

class GetServices(Resource):
    
   def get(self):
        data = mongo.db.services.find({},{ "_id": 0})
        service_list = list()
        for i in data:
            service_list.append(i.get("serviceName"))
        return {"status": True, "message":"Services have been retrieved successfully", "data": service_list }, 200
api.add_resource(GetServices,'/get/services')

class GetDiagnosis(Resource):
    
    def get(self):
        data = mongo.db.diagnosis.find({},{ "_id": 0})
        diagnosis_list = list()
        for i in data:
            diagnosis_list.append(i.get("diagnosis"))
        return {"status": True, "message":"Diagnosis have been retrieved successfully", "data": diagnosis_list }, 200
api.add_resource(GetDiagnosis,'/get/diagnosis')

class GetDrugs(Resource):
    
   def get(self):
        data = mongo.db.drug.find({},{ "_id": 0,"price": 0 })
        medicine_list = list()
        for i in data:
            medicine_list.append(i.get("drugName"))
        return {"status": True, "message":"List of drugs has been retrieved successfully", "data": medicine_list }, 200
api.add_resource(GetDrugs,'/get/drugs')

class GetDrugTotal(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('drug_list', 
                    type=list,
                    required=True,
                    help="Enter list of drugs and field cannot be left blank")
    
 
    def get(self):
        payload = GetDrugTotal.parser.parse_args()
        drug_list = payload["drug_list"]
        price_list = list()
        for drug in drug_list:
            record = mongo.db.drug.find_one({"drugName" : drug })
            price_list.append(record.get("price"))
        total = sum(price_list)
        return {"status": True, "message":f"Price total for drugs is NGN{total}", "data":total }, 200
api.add_resource(GetDrugTotal,'/get/drugs/total')

class GetServiceTotal(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('service_list', 
                    type=list,
                    required=True,
                    help="Enter list of services and field cannot be left blank")
    
 
    def get(self):
        payload = GetServiceTotal.parser.parse_args()
        service_list = payload["service_list"]
        price_list = list()
        for service in service_list:
            record = mongo.db.services.find_one({"serviceName" : service })
            price_list.append(record.get("price"))
        total = sum(price_list)
        return {"status": True, "message":f"Price total for services is NGN{total}", "data":total }, 200
api.add_resource(GetServiceTotal,'/get/services/total')


@app.route('/', methods = ['GET', 'POST'])
def home():
    if(request.method == 'GET'):
        
        data = {'message': "welcome to the homepage of this webservice"}
        return jsonify(data)
    
# @app.route('/get/services', methods = ['GET'])
# def get_services():
#     data = service_col.find()
#     service_list = list()
#     for i in data:
#         service_list.append(i.get("service"))

#     return {"status": True, "message":"Services have been retrieved successfully", "data": service_list }

# @app.route('/get/diagnosis', methods = ['GET'])
# def get_diagnosis():
#     data = diagnosis_col.find()
#     diagnosis_list = list()
#     for i in data:
#         diagnosis_list.append(i.get("diagnosis"))

#     return {"status": True, "message":"Diagnosis have been retrieved successfully", "data": diagnosis_list }

# @app.route('/get/drugs', methods = ['GET'])
# def get_drugs():
#     data = medicine_col.find({},{ "_id": 0,"price": 0 })
#     medicine_list = list()
#     for i in data:
#         medicine_list.append(i)

#     return {"status": True, "message":"List of drugs has been retrieved successfully", "data": data }


# @app.route("/add/encounter", methods=["POST"])
# #@api_required
# def AddEncounter():
#     
#     data = request.get_json()
#     en_result = mongo.db.encounters.find_one({"code": data["encounter_code"], "archive": False})
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
#     mongo.db.encounters.update_one({"_id": ObjectId(en_result["_id"]), "code": data["encounter_code"]}, {
#         "$push": {encounter_type: {"date": Today, "service": data["service"],
#                                "facility": en_result["facility"]}}})

#     return {"message": f"Service {data['service']['serviceName']} added", "status": True}

@app.route("/encounters/<string:code>/diagnosis", methods=["POST"])
#@api_required
def diagnose_encounter(code):
    
    try:
        data = request.get_json()
        payload = Diagnose().load(data)
        diagnosis = []
        for x in payload["diagnosis"]:
            x.update({"date": str(current_date)})
            diagnosis.append(x)
        query = {"active": "approved", "type": "referral"} if len(code) == 6 else {"type": "encounter"}
        record = mongo.db.encounters.find_one_and_update({"code": code, "facility.id": payload["facility_no"],
                                                        "archive": False, **query},
                                                       {"$push": {"diagnosis": diagnosis}})
        if not list(record):
            jsonify(message=f"No record found for {code}", status=False)
    except Exception as e:
        return jsonify(message=f"An exception occurred: {e}", status=False)
    else:
        return jsonify(data=diagnosis, message=f"diagnosis recorded for encounter code {code}", status=True)
    
@app.route('/encounters/<string:code>/services', methods=["POST"])
#@api_required
def encounters_services(code):

    try:
        data = request.get_json()
        payload = Serivces().load(data)
        services = []
        for x in payload["services"]:
            x.update({"date": str(current_date)})
            services.append(x)
        query = {"active": "approved", "type": "referral"} if len(code) == 6 else {"type": "encounter"}
        record = mongo.db.encounters.find_one_and_update({"code": code, "facility.id": payload["facility_no"],
                                                        "archive": False, "diagnosis": {"$ne": []},**query},
                                                       {"$push": {"services": {"$each": services}}})
        if not record:
            return jsonify(message=f"No diagnosis found for {code} ", status=False)

    except Exception as e:
        return jsonify(message=f"An exception occurred: {e}", status=False)
    else:
        return jsonify(data=services, message=f"Services recorded for encounter code {code}", status=True)

@app.route('/encounters/<string:code>/drugs', methods=["POST"])
#@api_required
def encounters_drugs(code):

    try:
        data = request.get_json()
        payload = Drugs().load(data)
        drugs = []
        for x in payload["drugs"]:
            x.update({"date": str(current_date)})
            drugs.append(x)
        query = {"active": "approved", "type": "referral"} if len(code) == 6 else {"type": "encounter"}
        record = mongo.db.encounters.find_one_and_update({"code": code, "facility.id": payload["facility_no"],
                                                        "archive": False, **query},
                                                       {"$push": {"drugs": {"$each":drugs}}})
        if not record:
            return jsonify(status=False, message=f"no record found for {code}")
    except Exception as e:
        return jsonify(message=f"An exception occurred: {e}", status=False)
    else:
        return jsonify(data=drugs, message=f"Drugs recorded for encounter code {code}", status=True)
    
@app.route('/search/services/<string:keyword>', methods=["GET"])
def search_services(keyword):
        
    try:
        services = list()
        record = mongo.db.services.find({"serviceName": {"$regex": keyword, "$options": "i"}}, {"_id": 0, "serviceName": 1, "serviceCode":1, "price":1})
        for i in record:
            services.append(i)
    except Exception as e:
        return jsonify(message=f"An exception occurred: {e}", status=False)
    else:
        return jsonify(data=services, message=f"List of services similar to {keyword} retreived successfully", status=True)  
    
@app.route("/all/encounter", methods=["GET"])
def all_encounter():
    mon = g.get('mongo')
    encounter = mon.db.encounters.find({}, {"_id": 0})

    return {"data": list(encounter), "status": "true"}


@app.route("/enrollments/<var>", methods=["GET"])
def al_enrollmentss(var):
    mon = g.get('mongo')
    var = var.lower()
    count = mon.db.summary.find_one({f"enrollee_{var}": {"$exists": True}}, {"_id": 0, f"enrollee_{var}": 1})

    return jsonify(data=count, status=True)


@app.route("/facility/<var>", methods=["GET"])
def all_facility(var):
    mon = g.get('mongo')
    var = var.lower()
    count = mon.db.summary.find_one({f"facility_{var}": {"$exists": True}}, {"_id": 0, f"facility_{var}": 1})
    return jsonify(data=count, status=True)


@app.route("/encounter/<var>", methods=["GET"])
def all_encounters(var):
    mon = g.get('mongo')
    var = var.lower()
    count = mon.db.summary.find_one({f"encounter_{var}": {"$exists": True}}, {"_id": 0, f"encounter_{var}": 1})
    return jsonify(data=count, status=True)


def generate_id(gender):
    mon = g.get('mongo')
    gen = {"female": "2", "male": "1"}
    sex = gen[gender.lower()] if gender.lower() in gen else "0"
    wards = Nan.values()
    ward = random.choice(list(wards))
    p = create_code(6)
    enrid = p + ward + sex
    code = mon.db.subscriptions.find_one({"enrollment_id": enrid})
    while code:
        p = create_code(6)
        enrid = p + ward + sex
        code = mon.db.subscriptions.find_one({"enrollment_id": enrid})
    return enrid

def subscriptions(subcat, info, duration=False):
    mon = g.get('mongo')
    data = {"name": info["name"], "passport":info["passport"], "lga":info["lga"],
           "subcategoryitem":info["subcategoryitem"],"hmo":info["hmo"], "facility":info["facility"],
           "enrollment_id":info["enrollment_id"], "date_of_birth":info["date_of_birth"],"submission_id": info.get("submission_id", "None")
    , "submission_time": info["submission_time"], "principal_s_submission_id": info.get("principal_s_submission_id", "None")}

    sub = mon.db.categories.find_one({"name.id": int(subcat)}, {"sector": 1, "subcategory": 1})
    dur = duration or 12
    date = datetime.today() + relativedelta(months=+int(dur))
    sub_status = {"Formal": False, "Informal": date, "General": date, "Equity": date,
                  "Organized Private Sector (Neca)": date}
    sub_statuss = sub_status[sub["subcategory"]] if sub["subcategory"] in sub_status else sub_status[
        sub["sector"]]
    data["expiry_date"] = sub_statuss
    dates = parser.parse(str(datetime.today())) #"submission_id", "principal_s_submission_id"]
    if duration:
        if (duration is not None) and (duration != str(0)):
            data["payments"] = [
                {"paymentref": data["submission_id"], "transaction_date": dates, "duration": int(duration)}]
            data["total_duration"] = int(duration)
        else:
            data["payments"] = "payments by psg" if (sub["subcategory"] == "Formal") else "payments by ops/sponsored"
            data["total_duration"] = 12
    else:
        payment = mon.db.payments.find_one({data["principal_s_submission_id"]:"True"},{"_id":0, "duration":1})
        if not payment:
            data["payments"] = "payments by psg" if (sub["subcategory"] == "Formal") else "payments by ops/sponsored"
            data["total_duration"] = 12
        else:
            data["payments"] = [
                    {"paymentref": data["submission_id"], "transaction_date": dates, "duration": payment["duration"]}]
            data["total_duration"] = payment["duration"]

    doc = {"name": data["name"], "passport":data["passport"], "lga":data["lga"],
           "subcategoryitem":data["subcategoryitem"],"hmo":data["hmo"], "facility":data["facility"],
           "enrollment_id":data["enrollment_id"], "date_of_birth":data["date_of_birth"],"payments":data["payments"],
           "total_duration": data["total_duration"], "expiry_date":data["expiry_date"],
           "submission_time": data["submission_time"]}

    mon.db.subscriptions.insert_one(doc)       

def fileuploads():
    mon = g.get('mongo')
    hmo_name = request.form["hmo_name"]
    hmo_id = request.form["hmo_id"]
    email = request.form["email"]
    cat_id = request.form["subcategoryitemid"]
    cat_name = request.form["subcategoryitemname"]
    cat = request.form["category"]
    subcat = request.form["subcategory"]
    file = request.files.get('file')
    df = pd.read_excel(file, engine='openpyxl')

    # check column headers
    new_columns = []
    col1 = ["name", "gender", "date_of_birth", "dofa"]
    for col in df.columns:
        col = col.replace("_", " ")
        col = col.strip()
        col = col.lower()
        col = col.replace(" ", "_")
        new_columns.append(col)

    if "psn" in new_columns and (subcat == "Local Government Area"):
        col1.append("psn")
    no_col = [x for x in col1 if x not in new_columns]

    if "psn" not in new_columns and (subcat == "Local Government Area"):
        return {"message": "the field PSN is not found", "status": False}
    if len(no_col) > 0 and (cat == "Formal"):
        return {"message": f"the following fields where not found in the file {no_col}", "status": False}
    if ("name" not in new_columns) and (cat != "Formal"):
        return {"message": "The file doesn't contain a name column", "status": False}
    if df.shape[0] >= 500:
        return {"message": "can not uplaod more than 100 records at a time", "status": False}
    if df.shape[0] == 0:
        return {"message": "can not upload empty file", "status": False}

    if (cat == "Formal"):
        checks = ["name", "gender", "date_of_birth"]
    elif (cat != "Formal"):
        checks = ["name"]

    df.columns = new_columns
    df["date"] = str(datetime.today())
    df["status"] = "Not_Merged"
    has_null = df[df[checks].isnull().any(axis=1)]
    no_null = df[~df[checks].isnull().any(axis=1)]

    if "psn" in df.columns:
        no_null.rename(columns={'psn': 'submission_id'}, inplace=True)
    else:
        no_null.loc[:, "submission_id"] = no_null.apply(lambda x: hmo_id + str(randint(0, 999999)).zfill(6), axis=1)

    data = no_null.to_dict("records")


    bulk = mon.db.nominal.initialize_ordered_bulk_op()
    for doc in data:
        doc[cat_id] = doc["submission_id"]
        doc["hmo"] = {"name": hmo_name, "id": int(hmo_id)}
        doc["subcategoryitem"] = {"name": cat_name, "id": int(cat_id)}
        bulk.insert(doc)

    bulk.execute()

    mon.db.hmos.update_one({"name.name": hmo_name.title()}, {"$inc": {"total_assigned": no_null.shape[0]}})
    mon.db.categories.update_one({f"{int(cat_id)}": {"$exists": True}}, {"$inc": {"nominal_total": no_null.shape[0]}})
    # file_name = str(datetime.today().strftime('%d%m%Y'))
    out = io.BytesIO()
    writer = pd.ExcelWriter(out, engine='openpyxl')
    has_null.to_excel(writer, index=False, sheet_name='incomplete data')
    no_null.to_excel(writer, index=False, sheet_name='complete data')
    # writer.save()
    writer.close()
    message = f'Please find attached new submission ids created by {email}'
    send_mail(out.getvalue(), "nominal_file.xlsx", message, "for nominal roles")

    return {"message": "file uploaded", "status": True}

@app.route('/file/upload', methods=["POST"])
def checkfile():
    return fileuploads()

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)
#print(os.environ.get("URGENT_2K_KEY"))
#print(encounters_services(12345678))


#for i in encounters.find():
#print(mongo.db.encounters.find_one())