from flask import Flask, Response, request, jsonify
from pymongo import MongoClient
import pandas as pd
import io
import os
from flask_mail import Mail, Message

app = Flask(__name__)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ.get("EMAIL")
app.config['MAIL_PASSWORD'] = os.environ.get("EMAIL_PASSWORD")
mail = Mail(app)



# MongoDB connection setup
client = MongoClient(os.environ.get('MONGO_URI'))
db = client['random_data']
collection = db['bitcoin_blockchain_history']

@app.route('/export_to_excel', methods=['GET'])
def export_to_excel():
    

    def generate():
        # chunk_size = 500  # Number of records to process in one iteration
        # count = 0

        # # Creating output and writer (pandas excel writer)
        # out = io.BytesIO()
        # writer = pd.ExcelWriter(out, engine='openpyxl')

        # while True:
        #     data = [entry for entry in cursor.skip(count).limit(chunk_size)]
        #     if not data:
        #         break

        #     df = pd.DataFrame(data)
            

        #     excel_chunk = df.to_excel(excel_writer=writer,index=False)
        #     yield excel_chunk
        #     # excel_bytes = df.to_excel(index=False, excel_writer=writer)
        #     # yield excel_bytes

        #     count += chunk_size
        
    # def generate_excel():
    #     # Initialize a buffer to hold Excel file data
    #     excel_buffer = io.BytesIO()

    #     # Set up Excel writer
    #     excel_writer = pd.ExcelWriter(excel_buffer, engine='xlsxwriter')

    #     # Retrieve data from MongoDB
    #     cursor = collection.find({},{"_id": 0})
    #     batch_size = 1000  # Adjust the batch size based on your needs

    #     for idx, document in enumerate(cursor):
    #         # Process and write data to Excel
    #         pd.DataFrame([document]).to_excel(excel_writer, sheet_name=f'Sheet{idx}', index=False)

    #         # Write data in batches to Excel to optimize performance
    #         if (idx + 1) % batch_size == 0:
    #             #excel_writer.close()
    #             excel_buffer.seek(0)
    #             yield excel_buffer.read()
    #             excel_buffer.truncate(0)

    #     # Save any remaining data
    #     #excel_writer.close()
    #     excel_buffer.seek(0)
    #     yield excel_buffer.read()

    #     # Close the buffer
    #     excel_buffer.close()
    # Flask create response
    #resp = make_response(out.getvalue())
    # Query MongoDB collection in batches
        batch_size = 2000
        cursor = collection.find({},{"_id": 0}).batch_size(batch_size)

        # Initialize an empty DataFrame
        dfs = []

        for idx, record in enumerate(cursor):
            # Append the current record to the list of DataFrames
            dfs.append(pd.DataFrame([record]))

            # If the batch size is reached, write to Excel and clear the list
            if (idx + 1) % batch_size == 0:
                excel_buffer = io.BytesIO()
                pd.concat(dfs, ignore_index=True).to_excel(excel_buffer, index=False)
                excel_buffer.seek(0)
                yield excel_buffer.read()
                dfs = []

        # Write any remaining records to Excel
        if dfs:
            excel_buffer = io.BytesIO()
            pd.concat(dfs, ignore_index=True).to_excel(excel_buffer, index=False)
            excel_buffer.seek(0)
            yield excel_buffer.read()
    
    response = Response(generate(), content_type='application/x-xls')
    response.headers['Content-Disposition'] = 'attachment; filename=data.xlsx'
    return response




CHUNK_SIZE = 1000  # Number of records to fetch in each iteration

def generate_data_chunks():
    offset = 0
    while True:
        data_chunk = list(collection.find().skip(offset).limit(CHUNK_SIZE))
        if not data_chunk:
            break
        yield data_chunk
        offset += CHUNK_SIZE

@app.route('/export_and_email', methods=['POST'])
def export_and_email():
    data = request.get_json()
    email = data.get("email")
    if not email:
        return jsonify({'error': 'Email address not provided'}), 400

    # Create Excel file
    excel_file_path = 'data.xlsx'
    writer = pd.ExcelWriter(excel_file_path, engine='xlsxwriter')

    # Fetch data from MongoDB in chunks and write to Excel
    for chunk_num, data_chunk in enumerate(generate_data_chunks(), start=1):
        df_chunk = pd.DataFrame(data_chunk)
        sheet_name = f'Sheet_{chunk_num}'
        df_chunk.to_excel(writer, sheet_name, index=False)

    #writer.save()

    # Send email
    msg = Message('Data Export', sender='your_sender_email', recipients=[email])
    with app.open_resource(excel_file_path) as excel_file:
        msg.attach('data.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', excel_file.read())
    mail.send(msg)

    return jsonify({'message': 'Exported data and sent email'}), 200

if __name__ == '__main__':
    app.run(debug=True)


    




if __name__ == '__main__':
    app.run(debug=True)
#http://127.0.0.1:5000/export_to_excel