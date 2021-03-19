#!/usr/bin/env python
# Created By: Addie Liu | liuaddie@gmail.comapp = Flask(__name__)
import os
from flask import Flask, redirect, url_for, render_template, request, flash
app = Flask(__name__)
PORT = int(os.environ.get('PORT', 9090))

@app.route('/')
def index():
    return render_template("server.html")

@app.route("/video_feed")
def video_feed():
    """Route which renders solely the video"""
    return Response(
        'http://192.168.23.109:3030/video_feed', mimetype="multipart/x-mixed-replace; boundary=jpgboundary"
    )

@app.route('/cam_control', methods = ['POST'])
def cam_control():
    action = request.form['action']
    print(action)
    if action == 'focus_center':
        s1 = s.send_basic_cmd_r("setFocusMode", ["DMF"])
        s2 = s.send_basic_cmd_r("setTouchAFPosition", [50, 50]) # Center
        s3 = s.send_basic_cmd_r("cancelTouchAFPosition")
        s4 = s.send_basic_cmd_r("setFocusMode", ["MF"])

    if action == 'lock':
        s.send_basic_cmd("actHalfPressShutter")
        # print(postview)

    if action == 'shoot':
        postview = s.send_basic_cmd("actTakePicture")
        print(postview)
    return action

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
