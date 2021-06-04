from uploads3 import *
from simple_camera import take_picture
import time

from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/mask')
def run_recognition():
    s3upload = s3Upload()

    # take picture and name it capture.png
    s3upload.upload_picture()
    
    # mask recognition
    recog = s3upload.detect_labels()
    state = s3upload.check_mask(recog)
    print("STATE is", state)
    # updating db
    s3upload.update_db(state)
    print(recog)
    return state

@app.route('/stats')
def getStats():
    print(request.args.get("date"))
    date = str(request.args.get("date"))
    s3upload = s3Upload()
    stats = s3upload.get_today_stats(date)
    return stats

