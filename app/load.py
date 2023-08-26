import os
import csv
from pymongo import MongoClient

# MongoDB connection setup
client = MongoClient(os.environ.get("MONGO_URI"))
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