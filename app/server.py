#!/usr/bin/env python
#
# Implement part of the Sony Camera Remote API in a scriptable way.
#
# Copyright (C) 2015 Julien Desfossez
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.

# Original By: https://github.com/jdesfossez/sony-remote/blob/master/sony.py

#
# Modified By: Addie Liu | liuaddie@gmail.com
#
# Install OpenCV on MAC
# https://lizonghang.github.io/2016/07/16/Mac%E4%B8%8A%E5%AE%89%E8%A3%85python-opencv/
# http://www.mobileway.net/2015/02/14/install-opencv-for-python-on-mac-os-x/
#

# https://pypi.org/project/flask-opencv-streamer/
import os
from cryptography.fernet import Fernet
import time
from datetime import datetime
from functools import wraps
from threading import Thread
from cryptography.fernet import Fernet
from flask import Flask, Response, render_template, request

import cv2
import urllib.request
import numpy as np
import json
import requests

class LoginManager:
    """A class to handle auth storage, using encryption"""

    def __init__(self, path_to_login_file, keyname):
        self.path = path_to_login_file
        self.keyname = keyname
        self.key = self.load_key()
        self.fernet = Fernet(self.key)
        self.logins = self.load_logins()

    def __getstate__(self):
        """An override for loading this object's state from pickle"""
        ret = {"path": self.path, "keyname": self.keyname}
        return ret

    def __setstate__(self, dict_in):
        """An override for pickling this object's state"""
        self.path = dict_in["path"]
        self.keyname = dict_in["keyname"]
        self.key = self.load_key()
        self.fernet = Fernet(self.key)
        self.logins = self.load_logins()

    def load_logins(self):
        """Loads logins from a file, returning them as a dict"""
        logins = {}
        if os.path.exists(self.path):
            with open(self.path, "r") as file:
                lines = file.readlines()
                for line in lines:
                    decrypted_line = self.fernet.decrypt(bytes(line.encode()))
                    decrypted_line = decrypted_line.decode()
                    username, password = (
                        decrypted_line.replace(" ", "")
                        .replace("\n", "")
                        .replace("\t", "")
                        .split(",")
                    )
                    logins[username] = password
        return logins

    def write_logins(self):
        """Writes the logins to an encryptedfile"""
        if os.path.exists(self.path):
            os.remove(self.path)
        with open(self.path, "w") as file:
            for username in self.logins:
                file.write(self.encrypt_line(username) + "\n")

    def add_login(self, username, password):
        """Adds a new username and password, writing changes afterward"""
        if username in list(self.logins.keys()):
            print("Login pair not added; login {} already exists".format(username))
        else:
            self.logins[username] = password
            self.write_logins()

    def remove_login(self, username):
        """Removes a username and password, writing changes afterward"""
        if not username in list(self.logins.keys()):
            print("Login not found - no deletion was made")
        else:
            del self.logins[username]
            self.write_logins()

    def encrypt_line(self, username):
        """Encrypts a username/password line for the txt file and converts to str"""
        ret = "{}, {}".format(username, self.logins[username]).encode()
        ret = bytes(ret)
        ret = self.fernet.encrypt(ret)
        return str(ret.decode("utf-8"))

    def load_key(self):
        """Loads the key from a hidden location"""
        token = ""
        if os.path.exists(self.keyname):
            with open(self.keyname, "r") as file:
                lines = file.readlines()
                for line in lines:
                    token = line.replace("\n", "")
                    break
        else:
            token = Fernet.generate_key()
            with open(self.keyname, "w+") as file:
                file.write(token.decode("utf-8"))
        if isinstance(token, bytes):
            return bytes(token)
        return bytes(token.encode())

class Streamer:
    """A clean wrapper class for a Flask OpenCV Video Streamer"""

    def __init__(
        self,
        port,
        requires_auth,
        stream_res=(1280, 720),
        frame_rate=30,
        login_file="logins",
        login_key=".login",
    ):
        self.flask_name = "{}_{}".format(__name__, port)
        self.login_file = login_file
        self.login_key = login_key
        self.flask = Flask(self.flask_name)
        self.frame_to_stream = None
        self.guest_password = None
        self.password_create_time = None
        self.thread = None
        self.is_streaming = False
        self.port = port
        self.req_auth = requires_auth
        self.stream_res = stream_res
        self.frame_rate = frame_rate
        if requires_auth:
            self.generate_guest_password()
            self.login_manager = LoginManager(login_file, login_key)

    def __getstate__(self):
        """An override for loading this object's state from pickle"""
        ret = {
            "flask_name": self.flask_name,
            "port": self.port,
            "req_auth": self.req_auth,
            "stream_res": self.stream_res,
            "login_file": self.login_file,
            "login_key": self.login_key,
        }
        return ret

    def __setstate__(self, dict_in):
        """An override for pickling this object's state"""
        self.flask_name = dict_in["flask_name"]
        self.flask = Flask(self.flask_name)
        self.frame_to_stream = None
        self.guest_password = None
        self.password_create_time = None
        self.thread = None
        self.is_streaming = False
        self.port = dict_in["port"]
        self.req_auth = dict_in["req_auth"]
        self.stream_res = dict_in["stream_res"]
        if self.req_auth:
            self.generate_guest_password()
            self.login_manager = LoginManager(
                dict_in["login_file"], dict_in["login_key"]
            )

    def start_streaming(self):
        """Starts the video stream hosting process"""
        gen_function = self.gen

        @self.flask.route("/video_feed")
        @self.requires_auth
        def video_feed():
            """Route which renders solely the video"""
            return Response(
                gen_function(), mimetype="multipart/x-mixed-replace; boundary=jpgboundary"
            )

        @self.flask.route("/")
        @self.requires_auth
        def index():
            """Route which renders the video within an HTML template"""
            return render_template("index.html")

        @self.flask.route('/cam_control', methods = ['POST'])
        def cam_control():
            action = request.form['action']
            print(action)
            if action == 'focus_center':
                # Some Notes
                # [Maximum value, minimum value, step value]
                # In this case, it means that from 2500K to 9900K with 100K increments in between.
                #
                #
                s1 = s.send_basic_cmd_r("setFocusMode", ["DMF"])
                s2 = s.send_basic_cmd_r("setTouchAFPosition", [50, 50]) # Center
                s3 = s.send_basic_cmd_r("cancelTouchAFPosition")
                s4 = s.send_basic_cmd_r("setFocusMode", ["MF"])


                # s1 = s.send_basic_cmd_r("setFocusMode", ["DMF"])
                # print(s1)
                # if s1['result'][0] == 0:
                #     print("DMF")
                #     s2 = s.send_basic_cmd_r("setTouchAFPosition", [50, 50]) # Center
                #     if s2['result'][0] == 0:
                #         print("TouchAF Center")
                #         s3 = s.send_basic_cmd_r("cancelTouchAFPosition")
                #         if s3['result'][0] == 0:
                #             print("TouchAF Stop")
                #             s4 = s.send_basic_cmd_r("setFocusMode", ["MF"])
                            # if s4['result'][0] == 0:
                                # print("MF")

                # print("s1="+s1)    # s.send_basic_cmd("cancelTouchAFPosition")

                # json_data=open('json_data')
                # data = s1.json()
                # # s1_dump = json.dumps(s1)
                # s1_load = json.loads(s1_dump)
                # print(s1_load['result'][0])
                # json_data.close()
                # s3 = s.send_basic_cmd("setFocusMode", ["MF"])
                # print(s3)
                # print(postview)
            if action == 'lock':
                s.send_basic_cmd("actHalfPressShutter")
                # print(postview)
            if action == 'shoot':
                postview = s.send_basic_cmd("actTakePicture")
                print(postview)
            return action
            # return jsonify(username=username)

        @self.flask.route("/guest")
        @self.requires_auth
        def guest():
            """Route which shows a logged in user the current guest password and how long it'll work"""
            if self.req_auth:
                return "<center>The current guest password is:<br>{}<br>Password will expire {}</center>".format(
                    self.guest_password,
                    str(datetime.fromtimestamp(self.password_create_time + 86400)),
                )
            else:
                return "Auth not required, this page is not needed"

        @self.flask.route("/change password")
        def change_password():
            """Route which allows an authenticated user to chagne their password"""
            if self.req_auth:
                return render_template("form.html")
            else:
                return "Auth not required, this page is not needed"

        @self.flask.route("/change password result", methods=["POST", "GET"])
        def result():
            """Route which responds to a change_password input"""
            if request.method == "POST":
                result = request.form

                # Confirmation password didn't match
                if result["pw"] != result["pw_conf"]:
                    return render_template(
                        "fail.html", reason="New passwords did not match"
                    )
                # No username exists
                if result["username"] not in list(self.login_manager.logins.keys()):
                    return render_template("fail.html", reason="Username doesn't exist")
                # Old password wrong
                if result["old_pw"] != self.login_manager.logins[result["username"]]:
                    return render_template(
                        "fail.html", reason="Old password was incorrect"
                    )

                self.login_manager.remove_login(result["username"])
                self.login_manager.add_login(result["username"], result["pw"])
                return render_template("pass.html")

        self.thread = Thread(
            daemon=True,
            target=self.flask.run,
            kwargs={
                "host": "0.0.0.0",
                "port": self.port,
                "debug": False,
                "threaded": True,
            },
        )
        self.thread.start()
        self.is_streaming = True

    def update_frame(self, frame):
        """Updates the frame for streaming"""
        self.frame_to_stream = self.get_frame(frame)

    def get_frame(self, frame):
        """Encodes the OpenCV image to a 1280x720 image"""
        _, jpeg = cv2.imencode(
            ".jpg",
            cv2.resize(frame, self.stream_res),
            params=(cv2.IMWRITE_JPEG_QUALITY, 70),
        )
        return jpeg.tobytes()

    def gen(self):
        """A generator for the image."""
        header = "--jpgboundary\r\nContent-Type: image/jpeg\r\n"
        prefix = ""
        while True:
            # frame = self.frame_to_stream
            msg = (
                prefix
                + header
                + "Content-Length: {}\r\n\r\n".format(len(self.frame_to_stream))
            )

            yield (msg.encode("utf-8") + self.frame_to_stream)
            prefix = "\r\n"
            time.sleep(1 / self.frame_rate)

    def check_auth(self, username, password):
        """Dummy thing to check password"""
        # Generate a password if there is no password OR the one given is older than 24hrs
        if (
            self.guest_password is None
            or (time.time() - self.password_create_time) > 86400
        ) and self.req_auth:
            self.generate_guest_password()
        # Refresh the login manager's logins from the disk, in case a new login has been generated
        self.login_manager.logins = self.login_manager.load_logins()
        # Check the login manager for a match first
        if username in list(self.login_manager.logins.keys()):
            return password == self.login_manager.logins[username]

        # Otherwise check if it's the guest acct
        return username == "guest" and password == self.guest_password

    def authenticate(self):
        """Sends a 401 response that enables basic auth"""
        return Response(
            "Authentication Failed. Please reload to log in with proper credentials",
            401,
            {"WWW-Authenticate": 'Basic realm="Login Required"'},
        )

    def requires_auth(self, func):
        """A custom decorator for Flask streams"""

        @wraps(func)
        def decorated(*args, **kwargs):
            if self.req_auth:
                auth = request.authorization
                if not auth or not self.check_auth(auth.username, auth.password):
                    return self.authenticate()
                return func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        return decorated

    def generate_guest_password(self):
        """Generates and prints a random password on creation"""
        print("Generating Flask password")
        self.guest_password = str(Fernet.generate_key().decode())
        self.password_create_time = time.time()
        print(
            "Password for stream on Port: {} is\n    {}".format(
                self.port, self.guest_password
            )
        )

class SonyControl:
    def __init__(self):

        # self.url = 'http://10.0.0.1:10000/sony/camera' ## for QX10
        self.url = 'http://192.168.122.1:8080/sony/camera' ## for Nex-5R
        self.id = 1

    def send_rq(self, data):
        # req = urllib.request.Request(self.url)
        # req.add_header('Content-Type', 'application/json')
        data["id"] = self.id
        self.id += 1
        # print(json.dumps(data))
        response = requests.post(self.url, data=json.dumps(data))
        # print(response.json())
        r = response.json()
        # print(r)
        return r

    def send_basic_cmd(self, cmd, params=[]):
        data = {"method": cmd,
                "params": params,
                "version": "1.0"}
        return self.send_rq(data)

    def send_basic_cmd_r(self, cmd, params=[]):
        data = {"method": cmd,
                "params": params,
                "version": "1.0"}
        rq_data = self.send_rq(data)
        rq_data_dumps = json.dumps(rq_data)
        rq_data_loads = json.loads(rq_data_dumps)
        return rq_data_loads

    def liveview(self):
        stream = urllib.request.urlopen(self.live)
        print(stream)
        bytes = b''
        while True:
            bytes += stream.read(1024)
            # print(bytes)
            a = bytes.find(b'\xff\xd8')
            b = bytes.find(b'\xff\xd9')
            if a != -1 and b != -1:
                jpg = bytes[a:b+2]
                bytes = bytes[b+2:]
                # print(jpg)
                # print(bytes)
                i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                streamer.update_frame(i)
                if not streamer.is_streaming:
                    streamer.start_streaming()

                # cv2.imshow('i', i)
                # if cv2.waitKey(1) == 27:
                #     exit(0)

    def getVersions(self):
        r = self.send_basic_cmd("getVersions")
        print("Version %s" % r["result"][0][0])

    def startRecMode(self):
        r = self.send_basic_cmd("startRecMode")
        if r["result"][0] == 0:
            print("Rec mode started")

    def stopRecMode(self):
        r = self.send_basic_cmd("stopRecMode")
        if r["result"][0] == 0:
            print("Rec mode stopped")

    def getEvent(self):
        r = self.send_basic_cmd("getEvent", params=[True])
        for i in r["result"]:
            print(i)
            if i == "isoSpeedRateCandidates":
                print("LA")
        print("isoSpeedRateCandidates : %s" % (r["result"][0]))

    def startLiveview(self):
        r = self.send_basic_cmd("startLiveview")
        self.live = r["result"][0]
        self.liveview()

    def initialize(self):
        self.send_basic_cmd("setFocusMode", ["MF"])

if __name__ == "__main__":
    port = 3030
    require_login = False
    streamer = Streamer(port, require_login)

    # Open video device 0
    # video_capture = cv2.VideoCapture(0)
    s = SonyControl()
    # s.stopRecMode()
    # s.getVersions()
    s.startRecMode()
    # s.send_basic_cmd("cancelTouchAFPosition")
    # s.initialize()
    s.send_basic_cmd("setFocusMode", ["MF"])
    s.send_basic_cmd("setShutterSpeed",["1/50"])
    s.send_basic_cmd("setFNumber",["3.5"])
    s.send_basic_cmd("setIsoSpeedRate",["3200"])
    s.startLiveview()
