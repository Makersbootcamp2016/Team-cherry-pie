# coding=utf-8


import os, glob
import requests
import json
import datetime, time
from shutil import copyfile
from flask import Flask, request, redirect, url_for

from flask import Flask
app = Flask(__name__)

from jinja2 import Environment, PackageLoader
jinja_env = Environment(loader=PackageLoader('server','view'))


@app.route("/")
def function():
    data = requests.get('https://api.smartcitizen.me/v0/devices/3738')
    dataJ = data.json()

    gasV = 0
    gasU = '?'
#test
    for sensor in dataJ['data']['sensors']:
        if sensor['description']=="Temperature":
            temp = sensor['value']
            temp=round(temp,2)
            tempU = sensor['unit']

    for sensor in dataJ['data']['sensors']:
        if sensor['description']=="Humidity":
            HumV = sensor['value']
            HumV=round(HumV,2)
            HumU = sensor['unit']

    for sensor in dataJ['data']['sensors']:
        if sensor['description']=="NO2":
            gasV = sensor['value']
            gasV=round(gasV,2)
            gasU = sensor['unit']

    base = jinja_env.get_template('base.html')
    return base.render(temp_value=temp,temp_unit=tempU,hum_value=HumV,hum_unit=HumU,gas_value=gasV,gas_unit=gasU)

@app.route("/clak")
def doesrasptakeapic():
    time.sleep(10)
    return "YES"

@app.route("/shot", methods=['POST'])
def shot():
   if request.method == 'POST':
       # check if the post request has the file part
       if 'image' not in request.files:
           return 'ERROR: No file..'

       file = request.files['image']
       if not file or file.filename == '':
           return 'ERROR: Wrong file..'

       # Save Snapshot with Timestamp
       filepath = os.path.join(os.path.dirname(os.path.abspath(__file__))+'/static/upload/', "usershot.jpg")
       file.save(filepath)

       return 'SUCCESS'
   return 'ERROR: You\'re lost Dave..'



if __name__ == "__main__":
    app.run(port=10000)
