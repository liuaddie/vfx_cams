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


import cv2
import urllib2
import numpy as np
import json


class SonyControl:
    def __init__(self):

        self.url = 'http://10.0.0.1:10000/sony/camera' ## for QX10
        # self.url = 'http://192.168.122.1:8080/sony/camera' ## for Nex-5R
        self.id = 1

    def send_rq(self, data):
        req = urllib2.Request(self.url)
        req.add_header('Content-Type', 'application/json')
        data["id"] = self.id
        self.id += 1
        response = urllib2.urlopen(req, json.dumps(data))
        r = json.load(response)
        return r

    def send_basic_cmd(self, cmd, params=[]):
        data = {"method": cmd,
                "params": params,
                "version": "1.0"}
        return self.send_rq(data)

    def liveview(self):
        stream = urllib2.urlopen(self.live)
        bytes = ''
        while True:
            bytes += stream.read(1024)
            a = bytes.find('\xff\xd8')
            b = bytes.find('\xff\xd9')
            if a != -1 and b != -1:
                jpg = bytes[a:b+2]
                bytes = bytes[b+2:]
                i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),
                                 cv2.IMREAD_COLOR)
                cv2.imshow('i', i)
                if cv2.waitKey(1) == 27:
                    exit(0)

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

if __name__ == "__main__":
    s = SonyControl()
    # s.stopRecMode()
    s.getVersions()
    # s.startRecMode()
#    s.getEvent()
    s.startLiveview()
    # s.send_basic_cmd(setShutterSpeed,["1/50"])
    # s.send_basic_cmd(setFNumber,["3.5"])
    # s.send_basic_cmd(setIsoSpeedRate,["400"])
