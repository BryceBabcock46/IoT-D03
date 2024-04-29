from flask import Flask, send_file,jsonify, request, render_template
import mariadb
import secret
import sim_data
import random
import json
from tabulate import tabulate
from predict import initt_prediction, plot_graph
from flask_cors import CORS
import socket
import threading


app = Flask(__name__)
CORS(app)
# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address and port
server_socket.bind(('0.0.0.0', 5026))

# Listen for incoming connections
server_socket.listen(5)

print("Socket server started")


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
            cursor.execute("SELECT * FROM accelTable ORDER BY entry_id DESC LIMIT ?", (limit,))
        else:
            cursor.execute("SELECT * FROM accelTable WHERE device_id = ? ORDER BY entry_id DESC LIMIT ?", (device_id, limit))
        data = cursor.fetchall()
        return data
    except mariadb.Error as e:
        print(f"Error fetching data: {e}")
        return []
    
def insert_data(data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Insert data into the database
        cursor.execute("INSERT INTO accelTable (x_val, y_val, z_val) VALUES (?, ?, ?)",
                    (data['x_val'], data['y_val'], data['z_val']))
        conn.commit()
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

def calculate_data_summary(data):
    first_10_rows = data[:10]
    last_10_rows = data[-10:]
    return {'first_10_rows': first_10_rows, 'last_10_rows': last_10_rows}

def handle_socket_data(conn):
    try:
        while True:
            # Receive data from the client
            data = conn.recv(1024)
            if not data:
                break

            # Decode the received data from bytes to string
            data_str = data.decode()

            # Convert the JSON string to a Python dictionary
            data_dict = json.loads(data_str)

            # Process the received data (insert into database, etc.)
            print("Received data:", data_dict)
            # Your data processing code here

    except Exception as e:
        print("Error handling socket data:", e)

def accept_connections():
    while True:
        # Accept incoming connection
        conn, addr = server_socket.accept()
        print("Connection from:", addr)

        # Create a new thread to handle the connection
        threading.Thread(target=handle_socket_data, args=(conn,)).start()



@app.route('/')
def index():
    return render_template('main.html')

@app.route('/receive_data', methods=['POST']) 
def receive_data():
    if request.method == 'POST':
        print('recognizes post request')
        data = request.json
        insert_data(data)
        return jsonify({'success': True})
    else:
        print('nice try kiddo')
        abort(405)

@app.route('/predict', methods=['POST'])
def predict():
    print("prediction requested...")
    predicted_activities = initt_prediction()
    return jsonify({'predicted_activity': predicted_activities})

@app.route('/plot', methods=['GET'])
def plot():
    print("plot requested...")
    return jsonify(plot_graph())

if __name__ == '__main__':
    conn = get_db_connection()
    if conn:
        create_table(conn)
        conn.close()
    app.run(host= '0.0.0.0', port=5025)





