import numpy as np
import pandas as pd
from keras.models import load_model
from sklearn.preprocessing import StandardScaler
import mariadb
import secret
import json
from flask import jsonify
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64

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
    

model = load_model('acceleration_model.h5')
 
def get_frames(df, frame_size, hop_size):
    frames = []
    for i in range(0, len(df) - frame_size, hop_size):
        x = df['x_val'].values[i: i + frame_size]
        y = df['y_val'].values[i: i + frame_size]
        z = df['z_val'].values[i: i + frame_size]
        frames.append([x, y, z])
    return np.asarray(frames)

def predict_activity(data):
    Fs = 20
    frame_size = Fs * 4
    hop_size = Fs * 2

    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data)

    X = get_frames(pd.DataFrame(data=scaled_data, columns=['x_val','y_val','z_val']), frame_size, hop_size)

    predictions = model.predict(X)
    predicted_labels = np.argmax(predictions, axis=1)

    activity_labels = {0: 'Walking', 1: 'Jogging', 2: 'Upstairs', 3: 'Downstairs', 4: 'Sitting', 5: 'Standing'}
    decoded_labels = [activity_labels[label] for label in predicted_labels]

    return decoded_labels

def plot_graph():
    conn = get_db_connection()
    query = 'SELECT x_val, y_val, z_val FROM (SELECT * FROM accelTable ORDER BY entry_id DESC LIMIT 100) AS latest_data ORDER BY entry_id ASC'
    data = pd.read_sql(query, conn)

    fig, axs = plt.subplots(3, 1, figsize=(10, 12))  
    for i, axis in enumerate(['x_val', 'y_val', 'z_val']):
        plot_activity(data, axis, axs[i])  
        axs[i].set_title(f'{axis.upper()}')
        axs[i].set_xlabel('Entry')
        axs[i].set_ylabel('Acceleration')

    plt.tight_layout()

    buffer = BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)

    # Convert the plot to base64
    data_uri = base64.b64encode(buffer.read()).decode('utf-8')

    plt.close(fig)

    return {
        'plots': [
            'data:image/png;base64,' + data_uri,
            'data:image/png;base64,' + data_uri,
            'data:image/png;base64,' + data_uri
        ]
    }


def plot_activity(data, axis, ax):
    ax.plot(data[axis], label=axis.upper())

    ax.legend()
    #plt.savefig('activity_plot.png')



def initt_prediction():
    conn = get_db_connection()
    query = 'SELECT x_val, y_val, z_val FROM (SELECT * FROM accelTable ORDER BY entry_id DESC LIMIT 100) AS latest_data ORDER BY entry_id ASC'
    data = pd.read_sql(query, conn)
    predictions = predict_activity(data)
    return predictions







































# def predict_activity(data):

#     input_data = preprocess_data(data)
#     predictions = model.predict(input_data)
#     predicted_label = np.argmax(predictions, axis=1)
#     activity_labels = ['Walking', 'Jogging', 'Upstairs', 'Downstairs', 'Sitting', 'Standing']
#     decoded_label = activity_labels[predicted_label[0]]
#     print("The model predicts client is "+ decoded_label)
#     return decoded_label


# def preprocess_data(data):
#     df = pd.DataFrame(data)
#     print("columns:...")
#     print(df.columns)
#     scaled_X = df[['x_val', 'y_val', 'z_val']]
#     frame_size = 80
#     hop_size = 40
#     X, _ = get_frames(scaled_X, frame_size, hop_size)
#     X = X.reshape(-1, frame_size, 3, 1)
#     return X

# def get_frames(df, frame_size, hop_size):
#     frames = []
#     for i in range(0, len(df) - frame_size, hop_size):
#         frame = df[i: i + frame_size]
#         frames.append(frame)
#     return np.asarray(frames), None