
# coding=utf-8
from flask import Flask
app = Flask(__name__)


from jinja2 import Environment, PackageLoader
jinja_env = Environment(loader=PackageLoader('server','Views'))


import requests

data = requests.get('https://api.smartcitizen.me/v0/devices/3740')
dataJ = data.json()
#
# for sensor in dataJ['data']['sensor']:
#     if sensor ['id'] ==4:
#         temperature = sensor['value']

# rep = requests.post('http://imagebin.ca/upload.php',
#                     files={
#                     'file':open('/Users/corinofontana/Desktop/Test.png', 'rb')
#                     }
#                     )
# print(rep)
# print(rep.text)
#
# lien = rep.text;
#
# x=lien.split('url:')#split URL
# a,b=x
# print(b)#b=url image

# @app.route("/")# text ecran
# def Picture():
#     return b


@app.route("/")
def hello():

    data = requests.get("https://api.smartcitizen.me/v0/devices/3740")
    dataJ = data.json()
    #print(dataJ['data']['sensors'][3]['value'],dataJ['data']['sensors'][3]['unit'])
    tempj = dataJ['data']['sensors'][3]['value']
    tempj=str(tempj)


    base = jinja_env.get_template('Base.html')
    return base.render(temp_value=tempj)#inserer image=b pour voir l'image upload


if __name__ == "__main__":
    app.run(port=1333)
