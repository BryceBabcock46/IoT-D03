import numpy as np
import pandas as pd
from scipy import stats
from tensorflow import keras
from keras.models import load_model

print('*'*20)
model = load_model('accel_model.h5')
print('*'*20)

def predict_activity(data):
    input_data = preprocess_data(data)
    predictions = model.predict(input_data)

    #TESTING PREDICTIONS WITH CONTROL DATA
    # temp_data = pd.read_csv('./datasets/standing.csv')
    # test_data = preprocess_data(temp_data)
    # test_data = np.expand_dims(test_data, axis=1)
    # predictions = model.predict(test_data)
    # desired_shape = (temp_data.shape[0], 80, 3, 1)
    # reshaped_data = temp_data.values.reshape(desired_shape)
    # predictions = model.predict(reshaped_data)

    predicted_label = np.argmax(predictions, axis=1)
    activity_labels = ['Walking', 'Jogging', 'Upstairs', 'Downstairs', 'Sitting', 'Standing']
    decoded_label = activity_labels[predicted_label[0]]

    return decoded_label


def preprocess_data(data):
    df = pd.DataFrame(data)
    print("columns:...")
    print(df.columns)
    scaled_X = df[['x_val', 'y_val', 'z_val']]
    frame_size = 80
    hop_size = 40
    X, _ = get_frames(scaled_X, frame_size, hop_size)
    X = X.reshape(-1, frame_size, 3, 1)
    return X

def get_frames(df, frame_size, hop_size):
    frames = []
    for i in range(0, len(df) - frame_size, hop_size):
        frame = df[i: i + frame_size]
        frames.append(frame)
    return np.asarray(frames), None