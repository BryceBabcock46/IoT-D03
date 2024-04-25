import numpy as np
import pandas as pd
import mariadb
import secret
from keras.models import load_model
from sklearn.preprocessing import StandardScaler


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

model = load_model("acceleration_model.h5")

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


if __name__ == "__main__":
    conn = get_db_connection()
    query = 'SELECT x_val, y_val, z_val FROM walkingTBL'
    data = pd.read_sql(query, conn)

    predictions = predict_activity(data)
    print(data)

    print("here's some predictions")
    for activity in predictions:
        print(activity)
