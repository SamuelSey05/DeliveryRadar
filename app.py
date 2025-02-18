#!/usr/bin/env python3

from flask import Flask, Request, request, url_for, render_template

## from secrets import SECRET_KEY # TODO: Build Secrets


class R(Request):
    # Whitelist your SRCF and/or custom domains to access the site via proxy.
    trusted_hosts = ["cstdeliveryradar.soc.srcf.net"]


app = Flask(__name__, static_folder="./leaflet-heatmap-comp/dist/assets", template_folder="./leaflet-heatmap-comp/dist")
app.request_class = R

# Used to secure cookies.  Generate a long, random string.
# Example key generated using `os.urandom(32)`:
# app.secret_key = ("\x96\xb4\x14\x8c\x71\xec\x27\x0b\x10\xdd\x66\xa6\xf1\x00"
# 		    "\xad\xd2\x85\xa1\xe5\x85\x60\x6a\x04\x43\xf4\xf3\xad\x24")
## app.secret_key = SECRET_KEY # TODO: Secrets.py

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template("index.html")

