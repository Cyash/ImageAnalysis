# coding: utf-8
from flask import Flask, request, jsonify, render_template
import base64
import json
import requests
import googleapikeys

#TODO: Improvements
#1. accept only certain types of images like png, jpg
#2. see if we can use AWS Simple Queing Service to queue requests


app = Flask(__name__)

GOOGLE_CLOUD_VISION_API_URL = 'https://vision.googleapis.com/v1/images:annotate?key='

def goog_cloud_vison (image_content, classificationType):
    api_url = GOOGLE_CLOUD_VISION_API_URL+googleapikeys.CLOUD_VISION
    req_body = json.dumps({
        'requests': [{
            'image': {
                'content': image_content
            },
            'features': [{
                'type': classificationType,
                'maxResults': 10,
            }]
        }]
    })

    res = requests.post(api_url, data=req_body)
    return res.json()

RATINGS = ['LIKELY', 'VERY_LIKELY']

def likely_sentiment(face):
    if face['joyLikelihood'] in RATINGS:
        return 'JOY'
    if face['sorrowLikelihood'] in RATINGS:
        return 'SORROW'
    if face['angerLikelihood'] in RATINGS:
        return 'ANGER'
    if face['surpriseLikelihood'] in RATINGS:
        return 'SURPRISE'


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return "please upload the file"
        if 'classify' not in request.form:
            return "select a type of classification"
        file = request.files['file']
        classificationType = request.form['classify']
        if file.filename == '':
             return 'No selected file'

        #help thread
        #stackoverflow.com/questions/38702937/error-must-be-convertible-to-a-buffer-not-inmemoryuploadedfile
        image_content = base64.b64encode(file.read())

        response = goog_cloud_vison(image_content, classificationType)

        if classificationType == 'FACE_DETECTION':
            sentiment = {}
            faceAnnotations = response['responses'][0]['faceAnnotations']
            sentiment['sentiment'] = likely_sentiment(faceAnnotations[0])
            return json.dumps(sentiment)

        if classificationType == 'LABEL_DETECTION':
            labelDescrption = []
            finalLabels = {}
            labels = response['responses'][0]['labelAnnotations']
            for label in labels:
                labelDescrption.append(label['description'])
                finalLabels['labels'] = labelDescrption

            return json.dumps(finalLabels)

        if classificationType == 'LANDMARK_DETECTION':
            landmarksDescription = []
            finallandmarkDescription = {}
            landmarks = response['responses'][0]['landmarkAnnotations']

            for landmark in landmarks:
                landmarksDescription.append(landmark['description'])
                finallandmarkDescription['landmark'] = landmarksDescription

            return json.dumps(finallandmarkDescription)

        if classificationType == 'TEXT_DETECTION':
            textInPic = []
            finalTextExtrabcted = {}

            textBlock = response['responses'][0]['textAnnotations']
            for text in textBlock:
                textInPic.append(text['description'])
                finalTextExtrabcted['text'] = textInPic[0]
            return json.dumps(finalTextExtrabcted)

        #if the calssification type is none other than those 4 types just render json response
        return jsonify(response)

    return render_template('index.html')


if __name__=='__main__':
    app.run()
