#!/usr/bin/env python3

from flask import Flask, Request, request, url_for, render_template, json

## from secrets import SECRET_KEY # TODO: Build Secrets
from videoQueue import upload
from common import TempDir, prepDBRows, DBConnectionFailure
from database import getIncidents

import os

class R(Request):
    # Whitelist your SRCF and/or custom domains to access the site via proxy.
    trusted_hosts = ["cstdeliveryradar.soc.srcf.net", "127.0.0.1:5000"]

app = Flask(__name__, static_folder="./video-upload/dist/assets", template_folder="./video-upload/dist")
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
        try:
            upload(file_path)  # pass the file path to the upload function
            return {"message": "File uploaded successfully"}, 200
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
