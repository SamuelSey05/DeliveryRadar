#!/usr/bin/env python3

from flask import Flask, Request, request, url_for, render_template, json

## from secrets import SECRET_KEY # TODO: Build Secrets
from videoQueue import VideoQueue
from processingController import setup_controller as proc_setup
from common import TempDir, prepDBRows, DBConnectionFailure, SIG_END
from database import getIncidents

import os
from multiprocessing import Manager, Queue
from multiprocessing.managers import SyncManager
from signal import signal, SIGINT

# Setup Processing and Video Queue with control channels
man:SyncManager = Manager()

vq_sem = man.Semaphore(0)
proc_sem = man.Semaphore(0)
vq_ctrl = man.Queue()
vq = VideoQueue(vq_ctrl, man, vq_sem, proc_sem)
proc_ctrl = man.Queue()
proc_p_handle = proc_setup(proc_ctrl, vq, proc_sem)

def sigint_handler(sig, frame):
    vq_ctrl.put(SIG_END)
    proc_ctrl.put(SIG_END)

signal(SIGINT, sigint_handler)


class R(Request):
    # Whitelist your SRCF and/or custom domains to access the site via proxy.
    trusted_hosts = ["cstdeliveryradar.soc.srcf.net", "127.0.0.1:5000"]

app = Flask(__name__, static_folder="./videoUpload/dist/assets", template_folder="./videoUpload/dist")
app.request_class = R

# Used to secure cookies.  Generate a long, random string.
# Example key generated using `os.urandom(32)`:
# app.secret_key = ("\x96\xb4\x14\x8c\x71\xec\x27\x0b\x10\xdd\x66\xa6\xf1\x00"
# 		    "\xad\xd2\x85\xa1\xe5\x85\x60\x6a\x04\x43\xf4\xf3\xad\x24")
## app.secret_key = SECRET_KEY # TODO: Secrets.py

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods = ['POST'])
def upload_file():
    
    if "file" not in request.files:
        return {"error": "No file part"}, 400
    
    file = request.files["file"]

    if file.filename == "":
        return {"error": "No selected file"}, 400

    with TempDir() as tmp:
        filename = file.filename
        file_path = os.path.join(tmp.path(), filename)
        file.save(file_path)  # save the uploaded file in the temporary directory
        if app.debug:
            print (f"Saved upload to: {file_path}")
        try:
            vq.upload(file_path, app.debug)  # pass the file path to the upload function
            return {"message": "Submission uploaded successfully"}, 200
        except Exception as e:
            return {"error": str(e)}, 500
        
@app.route("/heatmap-data", methods = ['GET'])
def heatmap_data():
    try:
        data = getIncidents()
    except DBConnectionFailure:
        data = []
    response = app.response_class(response=json.dumps(prepDBRows(data)), status=200, mimetype='application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template("index.html")



# TODO Add 404 page
# # app name 
# @app.errorhandler(404) 
# # inbuilt function which takes error as parameter 
# def not_found(e): 
# # defining function 
#   return render_template("404.html") 

