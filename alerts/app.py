import json
import smtplib
import os
import win32com.client
from flask import Flask, render_template, redirect, request, url_for, make_response, jsonify
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
color = "green"


@app.route('/')
def index():
    content = make_response(render_template('index.html'))
    return content


@app.route('/_ajaxAutoRefresh', methods= ['GET'])
def stuff():
    return jsonify(color=color)


@app.route('/api/v1/device/register',methods=['POST'])
def register():
    request.get_json(force=True)

    parser = reqparse.RequestParser()
    parser.add_argument('id', required=True)
    args = parser.parse_args()

    id = args['id']

    print("registering device: ", id)

    returnData = "Device registered"

    return returnData, 201


@app.route('/api/v1/device/<id>/changeColor',methods=['PUT'])
def changeColor(id):
    global color
    request.get_json(force=True)

    parser = reqparse.RequestParser()
    parser.add_argument('color', required=True)
    args = parser.parse_args()

    color = (args['color'])

    print("requesting device: ", id)

    returnData = "Command accepted"

    return returnData, 201
    
@app.route('/api/v1/device/<id>/notificationoutlook',methods=['POST'],endpoint='func2')
def notificationOutlook(id):
    request.get_json(force=True)

    parser = reqparse.RequestParser()
    parser.add_argument('message', required=True)
    args = parser.parse_args()

    message = (args['message'])

    print("requesting device: ", id)
 
    

    outlook = win32com.client.Dispatch('outlook.application')

    mail = outlook.CreateItem(0)

    mail.To = 'satwika.kotha@ltts.com'
    mail.Subject = 'Test Email'
    #mail.HTMLBody = '<h3>This is HTML Body</h3>'
    mail.Body = message
    #mail.Attachments.Add('c:\\sample.xlsx')
    #mail.Attachments.Add('c:\\sample2.xlsx')
    #mail.CC = 'somebody@company.com'

    mail.Send()

    print("Mail sent")


if __name__ == "__main__":
	app.run(    debug=True, host='0.0.0.0', port=int(os.getenv('PORT', '5000')), threaded=True)
