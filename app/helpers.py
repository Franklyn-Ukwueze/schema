import os
#import openpyxl
#import pandas as pd
from pymongo import MongoClient
from functools import wraps
from flask import request

# client = MongoClient(os.getenv("MONGO_URI"))
# db = client.schema_data
# service_col = db.services
# medicine_col = db.medicine
# diagnosis_col = db.diagnosis

urgent2k_token = os.environ.get("URGENT_2K_KEY")
#base_url = os.getenv("SAFEPAY_URL")

# decorator function frequesting api key as header
def urgent2k_token_required(f):
    @wraps(f)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            return {"status": False, "message": "Access token is missing at " + request.url, "data": None}, 401

        if token == urgent2k_token:
            return f(*args, **kwargs)
        else:
            return {"status": False, "message": "Invalid access token at " + request.url, "data": None}, 401

    return decorated


# os.getcwd()
# os.chdir("C:/Users/DELL/Downloads") #this changes our CWD, if the excel sheet is not in CWD

# file = 'PLASCHEMA Service Tariff.xlsx'
# data = pd.ExcelFile(file)
#print(data.sheet_names) #this returns the all the sheets in the excel file
# ['Sheet1']
# ps = openpyxl.load_workbook('PLASCHEMA Medicine List.xlsx')
# sheet = ps['Sheet1']
# sheet.max_row 

# for row in range(5, sheet.max_row -9):
#     drug = sheet['B' + str(row)].value
#     dosage_form = sheet['C' + str(row)].value
#     strength = sheet['D' + str(row)].value
#     price = sheet['E' + str(row)].value

#     data = {"drug": drug, "dosage_form": dosage_form, "strength": strength, "price": price}
#     #print(data)
#     medicine_col.insert_one(data)
# print("done")

# for row in range(2, sheet.max_row + 1):
#     diagnosis = sheet['A' + str(row)].value


#     data = {"diagnosis": diagnosis}
#     diagnosis_col.insert_one(data)
# #print(data)
# print("done")

def return_services():
    data = service_col.find()
    service_list = list()
    for i in data:
        service_list.append(i.get("service"))

    print(service_list)

def return_diagnosis():
    data = diagnosis_col.find()
    diagnosis_list = list()
    for i in data:
        diagnosis_list.append(i.get("diagnosis"))

    print(diagnosis_list)
        
def return_drugs():
    data = medicine_col.find({},{ "_id": 0,"price": 0 })
    medicine_list = list()
    for i in data:
        medicine_list.append(i)

    print(medicine_list)
        
# def enrollment_summary():
#     mon = g.get('mongo')
#     record = mon.db.hmos.find({}, {"_id": 0, "name.name": 1, "total_assigned": 1, "total_enrolled": 1, "number_dep": 1})
#     cats = mon.db.categories.aggregate([{"$match": {"subcategory": {"$exists": True}, }},
#                                         {"$group": {"_id": "$subcategory",
#                                                     "Total Enrolled": {"$sum": "$total_enrolled"},
#                                                     "Enrolled Dependents": {"$sum": "$number_dep"},
#                                                     "Total Nominal": {"$sum": "$nominal_total"},
#                                                     "Number of items": {"$sum": 1}}}])
#     df1 = pd.DataFrame(cats)
#     data = []
#     for hmo in list(record):
#         hmo["name"] = hmo["name"]["name"]
#         data.append(hmo)
#     df = pd.DataFrame(data)
#     df.set_index('name', inplace=True)
#     df["Assigned Enrolled Diff"] = df["total_assigned"] - df["total_enrolled"]
#     df["Principal & Dependents"] = df["total_enrolled"] + df["number_dep"]
#     df1["Assigned Enrolled Diff"] = df1["Total Nominal"] - df1["Total Enrolled"]
#     df1["Principal & Dependents"] = df1["Total Enrolled"] + df1["Enrolled Dependents"]
#     df1.loc['Total'] = df1.sum(numeric_only=True, axis=0)
#     df.loc['Total'] = df.sum(numeric_only=True, axis=0)
#     df = df.rename(
#         columns={"total_assigned": 'Assigned', "total_enrolled": 'Enrolled', "number_dep": "Dependents", "name": "Hmo"})
#     df1 = df1.rename(columns={"_id": 'Subcategory'})
#     df1 = df1.reindex(
#         columns=["Subcategory", "Number of items", 'Total Nominal', "Total Enrolled", "Assigned Enrolled Diff",
#                  "Enrolled Dependents", "Principal & Dependents"])
#     # Creating output and writer (pandas excel writer)
#     out = io.BytesIO()
#     writer = pd.ExcelWriter(out, engine='openpyxl')

#     # Export data frame to excel
#     df.to_excel(excel_writer=writer, sheet_name='HMO summary')
#     df1.to_excel(excel_writer=writer, sheet_name='category summary', index=False)
#     writer.save()
#     writer.close()

#     # Flask create response
#     r = make_response(out.getvalue())

#     # Defining correct excel headers
#     r.headers[
#         "Content-Disposition"] = f"attachment; filename=Enrollment_summary{datetime.today().strftime('%Y-%m-%d')}.xlsx"
#     r.headers["Content-type"] = "application/x-xls"

#     return r

# def category_data(category):
# mon = g.get('mongo')
# cat = mon.db.categories.distinct("name.id", {"sector": category.title()})

# record = mon.db.enrollments.find({"subcategoryitem.id":{"$in":cat}},
#                                     {"_id": 0, "subcategoryitem.name": 1, "date_of_birth": 1, "name": 1, "hmo.name": 1,
#                                     "submission_id": 1, "enrollment_id": 1, "phone_number": 1, "blood_group": 1,
#                                     "gender": 1, "dependents": 1, "facility.name": 1,"sub_status":1})
# records = list(record)
# if record is None or len(records) == 0:
#     return {"message": f"No information Available for {category}", "status": False}

# data = []
# depp = []
# for rec in records:
#     rec["hmo"] = rec["hmo"]["name"]
#     rec["mda"] = rec["subcategoryitem"]["name"]
#     rec["facility"] = rec["facility"]["name"]
#     if "dependents" in rec:
#         for dep in rec["dependents"]:
#             depen = {}
#             if type(dep) != str:
#                 depen["name"] = dep["name"]
#             else:
#                 depen["name"] = dep
#             depen["submission_id"] = rec["submission_id"]
#             depp.append(depen)
#         del rec["dependents"]
#     del rec["subcategoryitem"]
#     data.append(rec)

# df = pd.DataFrame(data)
# dd = pd.DataFrame(depp)

# # Creating output and writer (pandas excel writer)
# out = io.BytesIO()
# writer = pd.ExcelWriter(out, engine='openpyxl')

# # Export data frame to excel
# df.to_excel(excel_writer=writer, sheet_name="principal", index=False)
# dd.to_excel(excel_writer=writer, sheet_name="dependants", index=False)
# writer.save()
# writer.close()

# # Flask create response
# resp = make_response(out.getvalue())
# # Defining correct excel headers
# resp.headers[
#     "Content-Disposition"] = f"attachment; filename={category.replace(' ', '_')}_{datetime.today().strftime('%Y-%m-%d')}.xlsx"
# resp.headers["Content-type"] = "application/x-xls"

<<<<<<< HEAD
# return resp
# import eventlet
=======
return resp
import eventlet
>>>>>>> 374d2d9bc43694ac8d29712c313ae0d26db839da

# @app.route('/get_large_data', methods=['GET'])
# def get_large_data():
#     # Retrieve data from MongoDB
#     data = list(collection.find({}))  # Customize your query if needed

#     # Create an Excel file
#     wb = openpyxl.Workbook()
#     ws = wb.active

#     for index, item in enumerate(data, start=1):
#         ws.cell(row=index, column=1, value=item['field1'])  # Customize for your data structure

#     excel_filename = 'large_data.xlsx'
#     wb.save(excel_filename)

#     # Send the Excel file to the client
#     return send_file(excel_filename, as_attachment=True)

# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching
# app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
# app.config['JSONIFY_MIMETYPE'] = 'application/json;charset=utf-8'

<<<<<<< HEAD
# eventlet.monkey_patch()

# from flask import Flask, Response, render_template
# from flask_pymongo import PyMongo
# import pandas as pd
# import io
# import gevent
# from gevent.queue import Queue

# app = Flask(__name__)
# app.config['MONGO_URI'] = 'mongodb://localhost:27017/mydb'  # Update with your MongoDB URI
# mongo = PyMongo(app)

# def fetch_data():
#     cursor = mongo.db.collection.find()  # Update with your collection name and query if needed
#     data = list(cursor)
#     return data

# def generate_excel(data):
#     output = io.BytesIO()
#     df = pd.DataFrame(data)
#     df.to_excel(output, engine='openpyxl', index=False)
#     output.seek(0)
#     return output

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/download')
# def download():
#     data = fetch_data()
#     excel_data = generate_excel(data)

#     def generate():
#         yield excel_data.read(8192)  # Adjust buffer size as needed

#         while True:
#             chunk = excel_data.read(8192)
#             if not chunk:
#                 break
#             yield chunk

#     return Response(generate(), mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# if __name__ == '__main__':
#     app.run(debug=True)

# #return_diagnosis()
import csv
from pymongo import MongoClient

# MongoDB connection setup
client = MongoClient('mongodb://localhost:27017/')
db = client['random_data']
collection = db['bitcoin_blockchain_history']

# CSV file path
csv_file_path = 'C:/Users/DELL/schema/app/bitcoin_blockchain_history.csv'

# Open and read the CSV file
with open(csv_file_path, 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    csv_data = [row for row in csv_reader]

# Insert data into MongoDB collection
collection.insert_many(csv_data)

# Close the MongoDB connection
client.close()
=======
eventlet.monkey_patch()

from flask import Flask, Response, render_template
from flask_pymongo import PyMongo
import pandas as pd
import io
import gevent
from gevent.queue import Queue

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mydb'  # Update with your MongoDB URI
mongo = PyMongo(app)

def fetch_data():
    cursor = mongo.db.collection.find()  # Update with your collection name and query if needed
    data = list(cursor)
    return data

def generate_excel(data):
    output = io.BytesIO()
    df = pd.DataFrame(data)
    df.to_excel(output, engine='openpyxl', index=False)
    output.seek(0)
    return output

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download')
def download():
    data = fetch_data()
    excel_data = generate_excel(data)

    def generate():
        yield excel_data.read(8192)  # Adjust buffer size as needed

        while True:
            chunk = excel_data.read(8192)
            if not chunk:
                break
            yield chunk

    return Response(generate(), mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == '__main__':
    app.run(debug=True)
>>>>>>> 374d2d9bc43694ac8d29712c313ae0d26db839da

