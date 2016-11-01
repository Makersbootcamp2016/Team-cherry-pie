# coding=utf-8


import os, glob
import requests
import json
import dateutil.parser
import datetime, time
from shutil import copyfile
from flask import Flask, request, redirect, url_for

from flask import Flask
app = Flask(__name__)

from jinja2 import Environment, PackageLoader
jinja_env = Environment(loader=PackageLoader('server','view'))

# Settings
RECORD_INTERVAL = 1             # Interval between snaphots in seconds
HISTORY_COUNT = 10              # Number of snapshot to keep

SNAPSHOT_NAME = 'snapshot.jpg'
UPLOAD_PATH = os.path.dirname(os.path.abspath(__file__))+'/static/upload/'

LONGPOLL_TIME = 30
LONGPOLL_INTERVAL = 0.1
LONGPOLL_LIMIT = int(LONGPOLL_TIME/LONGPOLL_INTERVAL)

# Check file upload
ALLOWED_EXTENSIONS = set(['jpg'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# Shared Bool SETTER
def setBool(name, boole):
        if boole:
            if not getBool(name):
                os.mknod(name+".tmp")
        elif getBool(name):
            os.remove(name+".tmp")

# Shared Bool GETTER
def getBool(name):
        return os.path.isfile(name+".tmp")

# Init
setBool('clik', False)
setBool('clak', False)
setBool('repeat', False)


@app.route("/")
def function():
    setBool('clik', True)
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


# Upload snapshot
@app.route("/shot", methods=['POST'])
def snapshot_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'image' not in request.files:
            return 'ERROR: No file..'

        file = request.files['image']
        if not file or file.filename == '' or not allowed_file(file.filename):
            return 'ERROR: Wrong file..'

        # Save Snapshot with Timestamp
        filepath = os.path.join(UPLOAD_PATH, str(int(time.time()))+"_"+SNAPSHOT_NAME)
        file.save(filepath)

        # Remove older ones
        existingfiles = []
        for f in os.listdir(UPLOAD_PATH):
            if os.path.isfile(os.path.join(UPLOAD_PATH, f)):
                existingfiles.append(f)
        existingfiles.sort()
        while len(existingfiles) > HISTORY_COUNT:
            old = existingfiles.pop(0)
            os.remove(os.path.join(UPLOAD_PATH, old))

        # New shot available
        setBool('clak', True)

        # Should we repeat ?
        if getBool('repeat'):
            time.sleep(RECORD_INTERVAL)
            setBool('clik', True)

        return 'SUCCESS'

    return 'ERROR: You\'re lost Dave..'


# Dashboard ask a shot
@app.route("/clik/<int:repeat>")
def take_shot(repeat):
    print('clik')
    setBool('clik', True)
    setBool('repeat', (repeat==1))
    return 'OK'


# RPi keep informed
@app.route("/clak")
def wait_order():
    wait_clik = 0
    while not getBool('clik') and wait_clik < LONGPOLL_LIMIT:
        time.sleep(LONGPOLL_INTERVAL)
        wait_clik += 1

    if getBool('clik'):
        setBool('clik', False)
        return 'YES'
    else:
        return 'NO'


# Dashboard keep informed
@app.route("/news")
def wait_news():

    data = {}

    wait_news = 0
    while not getBool('clak') and wait_news < LONGPOLL_LIMIT:
        time.sleep(LONGPOLL_INTERVAL)
        wait_news += 1

    # New Snaphsot available
    if getBool('clak'):
        setBool('clak', False)
        print('clak')

        # Last snapshot
        newest = max(glob.iglob(UPLOAD_PATH+'*.jpg'), key=os.path.getctime)
        path, filename = os.path.split(newest)

        snapdate = datetime.datetime.fromtimestamp(os.path.getmtime(newest)) + datetime.timedelta(hours=2)
        data['snaptime'] = snapdate.strftime("%d/%m/%Y %H:%M:%S")
        data['snapshot'] = '/static/upload/'+filename

    data['recording'] = getBool('repeat')
    return json.dumps(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=10000)
