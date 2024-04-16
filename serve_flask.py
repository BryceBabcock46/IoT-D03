from flask import Flask, send_file,jsonify, request, render_template
import mariadb
import secret
import sim_data
import random
import json
from tabulate import tabulate
from predict import predict_activity

app = Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.template_folder = 'html'

def get_db_connection():

    try:
        conn = mariadb.connect(
            host = secret.db_host,
            database = secret.db_name,
            user = secret.user,
            password = secret.password
        )
        print("Database connection established successfully")
        return conn
    except mariadb.Error as e:
        print(f"Error connecting to DB!: {e}")
        return None

def create_table(conn):
    try:
        cursor = conn.cursor()

        cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS accelTable (
                    entry_id INT AUTO_INCREMENT PRIMARY KEY,
                    device_id INT,
                    x_val FLOAT,
                    y_val FLOAT,
                    z_val FLOAT
                )
            """)
        conn.commit()
        print("Table created or exists without issues")

        #print schema
    except mariadb.Error as e:
        print(f"Error creating table: {e}")

def print_table(cursor, table):
    cursor.execute(f"SELECT  * FROM {table}")
    print (tabulate(cursor, headers=[q[0] for q in cursor.description]))


def add_sim_data(conn):

    try:
        cursor = conn.cursor()
        values = sim_data.sim_data()
        dev_id = random.randint(1,10)
        x_val = values[0]
        y_val = values[1]
        z_val = values[2]

        cursor.execute(
            f"""
                INSERT INTO accelTable (device_id, x_val, y_val, z_val)
                VALUES ({dev_id}, {x_val}, {y_val}, {z_val})
            """)
        
        conn.commit()

    except mariadb.Error as e:
        print(f"Error adding data: {e}")

#81 is the threshold to avoid domain error with log func
def fetch_raw_data(device_id='all', limit=500):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        if device_id == 'all':
            cursor.execute("SELECT * FROM downstairsTBL ORDER BY entry_id DESC LIMIT ?", (limit,))
        else:
            cursor.execute("SELECT * FROM downstairsTBL WHERE device_id = ? ORDER BY entry_id DESC LIMIT ?", (device_id, limit))
        data = cursor.fetchall()
        return data
    except mariadb.Error as e:
        print(f"Error fetching data: {e}")
        return []
    
def calculate_last_10_entries_average(data):
    last_10_entries = data[-10:]
    if not last_10_entries:
        return {'x_val': 0, 'y_val': 0, 'z_val': 0}
    x_vals = [entry['x_val'] for entry in last_10_entries]
    y_vals = [entry['y_val'] for entry in last_10_entries]
    z_vals = [entry['z_val'] for entry in last_10_entries]
    avg_x = sum(x_vals) / len(x_vals)
    avg_y = sum(y_vals) / len(y_vals)
    avg_z = sum(z_vals) / len(z_vals)
    return {'x_val': avg_x, 'y_val': avg_y, 'z_val': avg_z}

@app.route('/')
def index():
    return render_template('main.html')

    
@app.route('/predict', methods=['POST'])
def predict():
    data = fetch_raw_data()
    print("Data here")
    print(data)
    predicted_activity = predict_activity(data)
    return jsonify({'predicted_activity': predicted_activity})
    
@app.route('/data')
def get_data():
    device_id = request.args.get('device_id', 'all')
    data = fetch_raw_data(device_id)
    return jsonify(data)

@app.route('/average_data')
def get_average_data():
        device_id = request.args.get('device_id', 'all')
        data = fetch_raw_data(device_id)
        last_10_avg = calculate_last_10_entries_average(data)
        return jsonify(last_10_avg)


if __name__ == '__main__':
    conn = get_db_connection()
    if conn:
        create_table(conn)
        for _ in range(10):
            add_sim_data(conn)
        conn.close()
    app.run(host= '0.0.0.0', port=5025)







# #run get from database with the given query and send the data back to the user by returning it 
# @app.route('/data')
# def get_data():
#     headers = dict(request.headers)
#     query = headers["query"]

#     pass 

# # run insert to database and senbd the objects in the data variable to the database
# @app.route('/insert')
# def send_data():
#     headers = dict(request.headers)
#     data = headers["data"]
#     pass 
# #   # Create a dictionary representing the JSON response
# #     data = {
# #         'message': 'This is a JSON response from Flask server',
# #         'status': 'success'
# #     }
# #     # Return the dictionary as JSON using jsonify
# #     return jsonify(data)



