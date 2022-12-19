import os
import time
import subprocess
import requests
import numpy
import cv2
import json
from pysony import SonyAPI, ControlPoint

flask_app = None
try:
    import flask
    from flask import Flask
    f = Flask(__name__)
except ImportError:
    print("Cannot import `flask`, liveview on web is not available")

if f:
    f.get_frame_handle = None
    f.get_frame_info = None
    f.config['DEBUG'] = False

    @f.route("/")
    def index():
        return flask.render_template_string("""
            <html>
              <head>
                <title>SONY Camera LiveView Streaming</title>
                <script type=text/javascript src="{{url_for('static', filename='jquery-3.6.0.min.js') }}"></script>
                <script>
                    function request_cam_control(action, cmd, param)
                    {
                      var focus_pt = $('#setting').find('input[name="focus_pt"]').val()
                      alert('focus'+focus_pt)
                      var req = new XMLHttpRequest()
                      req.open('POST', '/cam_control')
                      req.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
                      var postVars = 'action='+action+'&cmd='+cmd+'&param='+focus_pt
                      req.send(postVars)
                      return false
                    }
                </script>
              </head>
              <body>
                <h1>SONY LiveView Streaming</h1>
                <img src="{{ url_for('video_feed') }}">
                <p>
                  <form action="" method="POST" id="setting">
                  <input type="text" id="focus_pt" name="focus_pt" placeholder="50,50">
                  <input type="button" value="Focus" onclick="return request_cam_control('focus','','')">
                  </form>
                </p>
              </body>
            </html>
                    """)

    def gen():
        width = 640
        height = 424
        frame_rate = 6
        while True:
            if f.get_frame_handle is not None:
                frame = f.get_frame_handle()
                if f.get_frame_info is not None:
                    frame_img = bts_to_img(frame)
                    frame_info = f.get_frame_info()
                    for x in range(len(frame_info)):
                        # print(frame_info[0])
                        category = frame_info[x]['category']
                        if category == 1:
                            status = frame_info[x]['status']
                            left = round(frame_info[x]['left'] * width / 10000)
                            top = round(frame_info[x]['top'] * height / 10000)
                            right = round(frame_info[x]['right'] * width / 10000)
                            bottom = round(frame_info[x]['bottom'] * height / 10000)
                            # print(left, top, right, bottom, category, status)
                            frame_img = cv2.rectangle(frame_img,(left,top),(right,bottom),(0,255,0),1)
                    frame = image_to_bts(frame_img)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(1/frame_rate)

    @f.route('/video_feed')
    def video_feed():
        return flask.Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

    @f.route('/cam_control', methods = ['POST'])
    def cam_control():
        action = flask.request.form['action']
        cmd = flask.request.form['cmd']
        par = flask.request.form['param']
        pa1 = int(par.split(",")[0])
        pa2 = int(par.split(",")[1])
        print(action, cmd, par)
        print("setTouchAFPosition", s.setTouchAFPosition(param=[pa1, pa2]))
        return action

def image_to_bts(frame):
    _, bts = cv2.imencode('.webp', frame)
    bts = bts.tobytes()
    return bts

def bts_to_img(bts):
    buff = numpy.frombuffer(bts, numpy.uint8)
    buff = buff.reshape(1, -1)
    img = cv2.imdecode(buff, cv2.IMREAD_COLOR)
    return img

class Device:
    def __init__(self):
        with open('controller.json', 'r') as jsonfile:
            jsondata = jsonfile.read()
        self.info = json.loads(jsondata)

    def get(self, item):
        return self.info[item]

    def connect(self):
        cam_connection_try = 0
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

def liveview():
    url = s.liveview()
    lst = s.LiveviewStreamThread(url)
    lst.start()
    print('[i] LiveviewStreamThread started.')
    return lst.get_latest_view, lst.get_frameinfo

if __name__ == "__main__":
    d = Device()
    c = ControlPoint()
    print("******** Start Controller ********")
    print(d.get('id'), d.get('cam_ssid'), d.get('cam_pw'))

    while not len(c.discover(3)):
        d.connect()
        time.sleep(3)
    else:
        print("******** Ha Ha Ha~ ********")
        s = SonyAPI(QX_ADDR=c.discover(10)[0])

    api = s.getAvailableApiList()
    print(api)
    print("*"*23)

    if 'startRecMode' in (api['result'])[0]:
        print("startRecMode: ", s.startRecMode())
        time.sleep(10)

    api = s.getAvailableApiList()
    print("*"*23)
    print(api)
    print("*"*23)

    print("setLiveviewFrameInfo: ", s.setLiveviewFrameInfo(param=[{"frameInfo": True}]))
    time.sleep(3)
    print("getAvailableLiveviewSize: ", s.getAvailableLiveviewSize()) # M = 640x424

    handler, info = liveview()
    if f:
        f.get_frame_handle = handler
        f.get_frame_info = info
        f.run()


    # print(s.getAvailablePostviewImageSize())
    # postview = s.actTakePicture()['result'][0][0].replace("\\", "")
    # print(postview)
    # if postview.find('/'):
    #     filename = "Take_{}".format(postview.rsplit('/', 1)[1])
    #     print(filename)
    # task_folder = "_temp"
    # if not os.path.exists(task_folder):
    #     os.makedirs(task_folder)
    # filepath = "{}/{}".format(task_folder, filename)
    # download = requests.get(postview, allow_redirects=True)
    # open(filepath, 'wb').write(download.content)
