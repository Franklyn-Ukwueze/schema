import os
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_cors import CORS
from pymongo import MongoClient
from app.config import Config, MONGO_URI
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))



# from flask_pymongo import PyMongo

# Initialize application
app = Flask(__name__)

# app configuration
app.config.from_object(Config)

# Initialize Flask Api
api = Api(app)

CORS(app)
#Initialize db
client = MongoClient(os.getenv("MONGO_URI"))
db = client.election_reports
reports = db.reports

# Import the application webservice
from app import webservice, helpers ,error

# import os
# import pymongo
# from flask import Flask, jsonify, request
# from flask_pymongo import PyMongo

# app = Flask(__name__)

# mongo_uri = os.environ.get("MONGO_URI")

# myclient = pymongo.MongoClient(mongo_uri)
# mydb = myclient["cowry"]

# carts = mydb["carts"]
# orders = mydb["carts"]


# @app.route('/api/add-to-cart', methods=['POST'])
# def add_to_cart():
#     try:
#         # Retrieve user account information from request
#         user_id = request.json.get('user_id')
#         # Get the item details from the request body
#         product_id = request.json.get('product_id')
#         quantity = request.json.get('quantity')

#         if not user_id or not product_id:
#             return jsonify({'error': 'Invalid request. Please provide user_id and product_id.'}), 400
        
#         cart = carts.find_one({}, {f"{user_id}" : True})

#         # Check if the user has an existing cart
#         if not cart:
#             new_cart = {f"{user_id}" : True, "items": [{"product_id" : f"{product_id}", "quantitiy": quantity} ]}
#             carts.insert_one(new_cart)

#         elif cart:
#             filter = {f"{user_id}" : True}
#             new_items = [{"product_id" : f"{product_id}", "quantitiy": quantity}]
#             update = {"$push": {"items":{"$each": new_items}}}

#             # Update the record in the collection
#             carts.update_one(filter, update)

        

#     except Exception as e:
#         return jsonify(message=f"An exception occurred: {e}", status=False)
#     else:
#         return jsonify({'message': 'Item added to cart successfully.'}), 200

# @app.route('/submit_order', methods=['POST'])
# def submit_order():
#     # Get the order details from the request
#     order_data = request.get_json()

#     orders.insert_one(order_data)

#     response = {
#         'status': 'success',
#         'message': 'Order submitted successfully!'
#     }
#     return jsonify(response)

# if __name__ == '__main__':
#     app.run()







# import os
# from flask import Flask, jsonify, request
# from flask_pymongo import PyMongo

# # app = Flask(__name__)

# # #mongo_uri = os.environ.get("MONGO_URI")
# # mongo = PyMongo(app)

# import pymongo
# mongo_uri = os.environ.get("MONGO_URI")
# myclient = pymongo.MongoClient(mongo_uri)
# mydb = myclient["cowry"]

# mycol = mydb["carts"]

# def add_to_cart(user_id, product_id, quantity):
#     try:
#         # Retrieve user account information from request
#         #user_id = request.json.get('user_id')
#         # Get the item details from the request body
#         #product_id = request.json.get('product_id')
#         #quantity = request.json.get('quantity')

#         if not user_id or not product_id:
#             return {'error': 'Invalid request. Please provide user_id and product_id.'}
        
#         cart = mycol.find_one({}, {f"{user_id}" : True})

#         # Check if the user has an existing cart
#         if not cart:
#             new_cart = {f"{user_id}" : True, "items": [{"product_id" : f"{product_id}", "quantitiy": quantity} ]}
#             mycol.insert_one(new_cart)

#         elif cart:
#             filter = {f"{user_id}" : True}
#             new_items = [{"product_id" : f"{product_id}", "quantitiy": quantity}]
#             update = {"$push": {"items":{"$each": new_items}}}

#             # Update the record in the collection
#             mycol.update_one(filter, update)

            
#         # Add the item to the user's cart
        

#     except Exception as e:
#         return f"An exception occurred: {e}"
#     else:
#         return {'message': 'Item added to cart successfully.'}

# print(add_to_cart("1234", "2223333", 2))



# aniso8601==9.0.1
# blinker==1.6.2
# click==8.1.3
# colorama==0.4.6
# dnspython==2.3.0
# Flask==2.3.2
# Flask-Cors==3.0.10
# Flask-PyMongo==2.3.0
# Flask-RESTful==0.3.10
# itsdangerous==2.1.2
# Jinja2==3.1.2
# MarkupSafe==2.1.3
# pymongo==4.3.3
# pytz==2023.3
# six==1.16.0
# Werkzeug==2.3.6




