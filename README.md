Accelerometer Data Predictor!

Dataset used: https://www.cis.fordham.edu/wisdm/dataset.php

Functionality:

- The accelerometer data predictor uses the IMU to take your acceleration data (x,y, and z) and make predictions on
  what activity you are doing at that time.
- Predictions include walking, running, sitting, standing, upstairs, downstairs (controlled activities in training set)
  
Components:

backend: Python Flask Server
- frontend: html
- database: MariaDB SQL
- ml model: TensorFlow

Physical components:

- rasberry pi PicoW
- BNO055 IMU

Architecture:

- BNO055 sends post requests to Flask endpoint. Flask sends data points into the database
- On click in ui, html hits Flask endpoints
- Endpoints query the database and sends data to TensorFlow model to make a prediction as well as to a
  function that creates a graph of the data used
- TensorFlow model is downloaded in .h5 format and loaded into python with the TF, keras, and scikit-learn libraries


