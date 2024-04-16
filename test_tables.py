import mariadb
import secret
from tabulate import tabulate
import pandas as pd
import random

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

def print_table(cursor, table):
    cursor.execute(f"SELECT  * FROM {table}")
    print (tabulate(cursor, headers=[q[0] for q in cursor.description]))


def create_downstairs_test_table(conn):
    try:
        cursor = conn.cursor()

        cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS downstairsTBL (
                    entry_id INT AUTO_INCREMENT PRIMARY KEY,
                    device_id INT,
                    x_val FLOAT,
                    y_val FLOAT,
                    z_val FLOAT
                )
            """)
        conn.commit()
        print("Downstairs table created or exists without issues")

        #print schema
    except mariadb.Error as e:
        print(f"Error creating downstairs table: {e}")

def create_upstairs_test_table(conn):
    try:
        cursor = conn.cursor()

        cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS upstairsTBL (
                    entry_id INT AUTO_INCREMENT PRIMARY KEY,
                    device_id INT,
                    x_val FLOAT,
                    y_val FLOAT,
                    z_val FLOAT
                )
            """)
        conn.commit()
        print("Upstairs table created or exists without issues")

        #print schema
    except mariadb.Error as e:
        print(f"Error creating upstairs table: {e}")

def create_jogging_test_table(conn):
    try:
        cursor = conn.cursor()

        cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS joggingTBL (
                    entry_id INT AUTO_INCREMENT PRIMARY KEY,
                    device_id INT,
                    x_val FLOAT,
                    y_val FLOAT,
                    z_val FLOAT
                )
            """)
        conn.commit()
        print("Jogging table created or exists without issues")

        #print schema
    except mariadb.Error as e:
        print(f"Error creating jogging table: {e}")

def create_sitting_test_table(conn):
    try:
        cursor = conn.cursor()

        cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS sittingTBL (
                    entry_id INT AUTO_INCREMENT PRIMARY KEY,
                    device_id INT,
                    x_val FLOAT,
                    y_val FLOAT,
                    z_val FLOAT
                )
            """)
        conn.commit()
        print("Sitting table created or exists without issues")

        #print schema
    except mariadb.Error as e:
        print(f"Error creating sitting table: {e}")

def create_standing_test_table(conn):
    try:
        cursor = conn.cursor()

        cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS standingTBL (
                    entry_id INT AUTO_INCREMENT PRIMARY KEY,
                    device_id INT,
                    x_val FLOAT,
                    y_val FLOAT,
                    z_val FLOAT
                )
            """)
        conn.commit()
        print("Standing table created or exists without issues")

        #print schema
    except mariadb.Error as e:
        print(f"Error creating standing table: {e}")

def create_walking_test_table(conn):
    try:
        cursor = conn.cursor()

        cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS walkingTBL (
                    entry_id INT AUTO_INCREMENT PRIMARY KEY,
                    device_id INT,
                    x_val FLOAT,
                    y_val FLOAT,
                    z_val FLOAT
                )
            """)
        conn.commit()
        print("Walking table created or exists without issues")

        #print schema
    except mariadb.Error as e:
        print(f"Error creating walking table: {e}")

def insert_data_from_csv(csv_file, table_name, conn):

    csv_path = f"datasets/{csv_file}"
    df = pd.read_csv(csv_path)

    cursor = conn.cursor()

    for index, row in df.iterrows():
        x_val = row['x_val'] 
        y_val = row['y_val']  
        z_val = row['z_val']  
        device_id = random.randint(1, 10)  

        cursor.execute(
            f"""
                INSERT INTO {table_name} (device_id, x_val, y_val, z_val)
                VALUES ({device_id}, {x_val}, {y_val}, {z_val})
            """)
        
    conn.commit()




conn = get_db_connection()
if conn:
    # print_table(cursor= conn.cursor(), table='upstairsTBL')
    # print_table(cursor= conn.cursor(), table='joggingTBL')
    # print_table(cursor= conn.cursor(), table='sittingTBL')
    # print_table(cursor= conn.cursor(), table='standingTBL')
    # print_table(cursor= conn.cursor(), table='walkingTBL')
    #insert_data_from_csv('downstairs.csv', 'downstairsTBL', conn)
    print_table(cursor= conn.cursor(), table='downstairsTBL')

