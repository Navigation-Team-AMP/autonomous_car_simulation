#parsing command line arguments
import argparse
#decoding camera images
import base64
#for frametimestamp saving
from datetime import datetime
#reading and writing files
import os
#high level file operations
import shutil
#matrix math
import numpy as np
#real-time server
import socketio
#concurrent networking 
import eventlet
#web server gateway interface
import eventlet.wsgi
#image manipulation
from PIL import Image
#web framework
from flask import Flask
#input output
from io import BytesIO
# Load model
from model import Model

#initialize our server
sio = socketio.Server()
#our flask (web) app
app = Flask(__name__)

model = Model()
model.loadModel()

#registering event handler for the server
@sio.on('telemetry')
def telemetry(sid, data):
    if data:
        # The current steering angle of the car
        steering_angle = float(data["steering_angle"])
        # The current throttle of the car, how hard to push peddle
        throttle = float(data["throttle"])
        # The current speed of the car
        speed = float(data["speed"])
        # Compute steering angle of the car    
        image = Image.open(BytesIO(base64.b64decode(data["image"])))



        '''
        steering_angle = model.predict(image, preloaded=True)
        # Compute speed
        speed_target = 25 - abs(steering_angle) / 0.4 * 10
        # throttle = 0.2 - abs(steering_angle) / 0.4 * 0.15
        throttle = (speed_target - speed) * 0.1
        print("network prediction -> (steering angle: {:.3f}, throttle: {:.3f})".format(steering_angle, throttle))
        '''


        # get model prediction
        waypoints = model.predict(image, preloaded=True); # x,y,z,x,y,z,x,y,z...
        


        '''
        NOTE: Potential one-off errors here!
        '''


        NUM_VALS_IN_WAYPNT = 3;

        waypoints_string = "";
        #parse waypoints to a string
        for i in range(0,len(waypoints/NUM_VALS_IN_WAYPNT)): # "x,y,z"
            waypoints_string = waypoints_string + ",";

            for a in range(0,NUM_VALS_IN_WAYPNT):
                waypoints_string = waypoints_string + str(waypoints[NUM_VALS_IN_WAYPNT*i+a]) + " "; # replace the space with a comma to do x,y,z,x,y,z,x,y,z

            
        # waypoints_string should equal ",x y z, x y z, x y z"  note the comma at the beginning which we take out in the send_control call
        

        send_control(steering_angle, throttle, waypoints_string[1:]);

@sio.on('connect')
def connect(sid, environ):
    print("connect ", sid)
    send_control(0, 0)


def send_control(steering_angle, throttle):
    sio.emit(
        "steer",
        data={
            'steering_angle': steering_angle.__str__(),
            'throttle': throttle.__str__()
        },
        skip_sid=True)


if __name__ == '__main__':
    
    # wrap Flask application with engineio's middleware
    app = socketio.Middleware(sio, app)

    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app)
