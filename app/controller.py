import os
import time
import subprocess
import requests
import cv2
import json
from pysony import SonyAPI, ControlPoint

class Device:
    def __init__(self):
        with open('controller.json', 'r') as jsonfile:
            jsondata = jsonfile.read()
        self.info = json.loads(jsondata)

    def get(self, item):
        return self.info[item]

    def connect(self):
        cam_connection_try = 0
        print(self.get('id'), self.get('cam_ssid'), self.get('cam_pw'))
        print("Waiting for Camera Signal...")
        time.sleep(3)
        if self.get('ctrl_os') == "osx":
            cam_connect = subprocess.Popen(["networksetup","-setairportnetwork","en0",self.get('cam_ssid'),self.get('cam_pw')], stdout=subprocess.PIPE)
            print(cam_connect)
            cam_connect.wait()
            cam_connect_result = cam_connect.communicate()[0].decode("utf-8")
            print(cam_connect_result)
        else:
            cam_connect = subprocess.Popen(["nmcli","-a","d","wifi","connect",self.get('cam_ssid'),"password",self.get('cam_pw')], stdout=subprocess.PIPE)
            cam_connect.wait()
            time.sleep(10)
            cam_connect_result = cam_connect.communicate()[0].decode("utf-8").find("successfully activated")
            print(cam_connect_result)

if __name__ == "__main__":
    d = Device()
    c = ControlPoint()
    while not len(c.discover(3)):
        d.connect()
        time.sleep(3)
    else:
        print("******** Ha Ha Ha~ ********")
        s = SonyAPI(QX_ADDR=c.discover(1)[0])

    api = s.getAvailableApiList()
    print(api)
    if 'startRecMode' in (api['result'])[0]:
        print(s.startRecMode())
        time.sleep(10)
        api = s.getAvailableApiList()
        print(api)
    print(s.getAvailablePostviewImageSize())
    postview = s.actTakePicture()['result'][0][0].replace("\\", "")
    print(postview)
    if postview.find('/'):
        filename = "Take_{}".format(postview.rsplit('/', 1)[1])
        print(filename)
    task_folder = "_temp"
    if not os.path.exists(task_folder):
        os.makedirs(task_folder)
    filepath = "{}/{}".format(task_folder, filename)
    download = requests.get(postview, allow_redirects=True)
    open(filepath, 'wb').write(download.content)
