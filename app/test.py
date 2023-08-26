from flask import Flask, Response
from pymongo import MongoClient
import pandas as pd
import io

app = Flask(__name__)

# MongoDB connection setup
client = MongoClient('mongodb://localhost:27017/')
db = client['random_data']
collection = db['bitcoin_blockchain_history']

@app.route('/export_to_excel', methods=['GET'])
def export_to_excel():
    cursor = collection.find({},{"_id": 0})

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
        batch_size = 5000
        cursor = collection.find().batch_size(batch_size)

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


    




if __name__ == '__main__':
    app.run(debug=True)
#http://127.0.0.1:5000/export_to_excel