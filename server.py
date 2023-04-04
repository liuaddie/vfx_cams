import os
import time
import subprocess
import requests
import json
import re

flask_app = None
try:
    import flask
    from flask import Flask, Response, render_template, request
    f = Flask(__name__, static_folder='templates', template_folder='templates')
    PORT = int(os.environ.get('PORT', 3030))

except ImportError:
    print("Cannot import `flask`.")

if f:
    f.config['DEBUG'] = False

    @f.route("/")
    def index():
        return render_template("server.html")

    @f.route('/cam_control', methods=['POST'])
    def cam_control():
        cam_id = request.json['cam_id']
        action = request.json['action']
        param = request.json['param']
        print(cam_id, action, param)
        rs = "done"
        print(rs)
        return rs

    @f.route('/video_feed')
    def video_feed():
        rs = ""
        return rs

if __name__ == "__main__":
    if f:
        f.run(host='0.0.0.0', port=PORT, debug=False)
