import os
import time
from threading import Thread
import subprocess
import requests
import numpy
import cv2
import json
import ftplib
import re
from pysony import SonyAPI, ControlPoint

flask_app = None
try:
    import flask
    from flask import Flask, Response, render_template, request
    f = Flask(__name__, static_folder='templates', template_folder='templates')
    f.secret_key = os.urandom(42)
    f.config['DEBUG'] = False
    PORT = int(os.environ.get('PORT', 3030))

except ImportError:
    print("Cannot import `flask`, liveview on web is not available")

if f:
    # f.get_frame_handle = None
    # f.get_frame_info = None

    # f.fps = 12
    # f.width = 600
    # f.height = 400
    # f.rotate = 0

    @f.route("/")
    def index():
        return render_template("controller.html", id=d.get('id'))

    # @f.route("/cam_connect")
    # def cam_connect():
    #     while (w.connect() < 0):
    #         time.sleep(3)
    #     else:
    #         print("******** Ha Ha Ha~ ********")
    #         s = SonyAPI(QX_ADDR="http://{}:{}".format(d.get('cam_ip'), d.get('cam_port')))
    #
    #     return "connecting"

    # def gen():
    #     while True:
    #         if f.get_frame_handle is not None:
    #             frame = f.get_frame_handle()
    #             if f.get_frame_info is not None:
    #                 frame_img = cv2.resize(bts_to_img(frame), (f.width, f.height), interpolation = cv2.INTER_AREA)
    #                 frame_info = f.get_frame_info()
    #                 for x in range(len(frame_info)):
    #                     # print(frame_info[0])
    #                     category = frame_info[x]['category']
    #                     if category == 1:
    #                         status = frame_info[x]['status']
    #                         left = round(frame_info[x]['left'] * f.width / 10000)
    #                         top = round(frame_info[x]['top'] * f.height / 10000)
    #                         right = round(frame_info[x]['right'] * f.width / 10000)
    #                         bottom = round(frame_info[x]['bottom'] * f.height / 10000)
    #                         # print(left, top, right, bottom, category, status)
    #                         frame_img = cv2.rectangle(frame_img,(left,top),(right,bottom),(0,255,0),1)
    #                 match f.rotate:
    #                     case 1:
    #                         frame = image_to_bts(cv2.rotate(frame_img, cv2.ROTATE_90_CLOCKWISE))
    #                     case 2:
    #                         frame = image_to_bts(cv2.rotate(frame_img, cv2.ROTATE_180))
    #                     case 3:
    #                         frame = image_to_bts(cv2.rotate(frame_img, cv2.ROTATE_90_COUNTERCLOCKWISE))
    #                     case _:
    #                         frame = image_to_bts(frame_img)
    #
    #             yield (b'--frame\r\n'
    #                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    #         time.sleep(1/f.fps)

    # @f.route('/video_feed')
    # def video_feed():
    #     return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

    @f.route('/video_feed')
    def video_feed():
        return ""

    @f.route('/cam_control', methods=['POST'])
    def cam_control():
        rs = "Not Available"
        cam_id = request.json['cam_id']
        action = request.json['action']
        param = request.json['param']
        try:
            tt = request.json['tt']
            print(tt)
        except:
            tt = 0
        done = False
        print(cam_id, action, param)

        if action == "uploadFTP":
            print("uploadFTP: {}".format(param))

            src_folder = "_photogrammetry_src"
            filename = param
            filepath = "{}/{}/{}".format(src_folder, tt, filename)
            tt_folder = "src_folder/{}".format(src_folder, tt)
            thread_ftp = ThreadWithResult(target=upload, args=(filepath,tt_folder,filename))
            thread_ftp.start()
        else:
            try:
                rs = e()
            except:
                pass

            if rs == "IDLE":
                # handle liveview rotation
                if action == "rotate":
                    f.rotate = (f.rotate+int(param))%4
                    rs = str(f.rotate)
                elif action == "checkStatus":
                    print("checkStatus")
                else:
                    if param != "":
                        params = param.split(",")
                        # Convert type of params
                        for p in range(len(params)):
                            print("Before Convert: ", p, params[p], type(params[p]))
                            if params[p].find("\'") < 0:
                                if params[p].strip().lower() == "true" or params[p].strip().lower() == "false" :
                                    params[p] = bool(params[p])
                                else:
                                    params[p] = int(params[p])
                            else:
                                params[p] = eval(params[p].strip())
                            print("After Convert: ", p, params[p], type(params[p]))

                        fn = getattr(s, action)
                        rs = fn(param=[*params])
                    else:
                        if tt > 0 and not done:
                            while not done:
                                now = time.time()
                                # print(now)
                                if (now > tt):
                                    print(now)
                                    fn = getattr(s, action)
                                    rs = fn()
                                    done = True
                                    if action == "actTakePicture":
                                        print(rs['result'][0][0])
                                        url = rs['result'][0][0].replace("\\", "")

                                        thread_ftp = ThreadWithResult(target=upload, args=(url))
                                        thread_ftp.start()
                                        # thread_ftp.join()

                        else:
                            fn = getattr(s, action)
                            rs = fn()
                            done = True

        print(rs)
        return rs
# Upload to FTP
def upload(url):

    response = requests.get(url)
    if url.find('/'):
        filename = "{}_{}_{}".format(tt, d.get('id'), url.rsplit('/', 1)[1])
        print(filename)
    src_folder = "_photogrammetry_src"
    tt_folder = "{}/{}".format(src_folder, tt)
    if not os.path.exists(src_folder):
        os.makedirs(src_folder)
    if not os.path.exists(tt_folder):
        os.makedirs(tt_folder)

    filepath = '{}/{}'.format(tt_folder,filename)
    open(filepath, "wb").write(response.content)

    session = ftplib.FTP(d.get('ftp_addr'),d.get('id'),d.get('ftp_pw'))
    file = open(filepath,'rb')
    folder = "/{}".format(tt_folder)
    print(folder)
    try:
        session.mkd(folder)
        ftp.sendcmd('SITE CHMOD 644 ' + folder)
        print("Folder created")
    except:
        pass
    ftpcmd = "STOR {}/{}".format(folder, filename)
    session.storbinary(ftpcmd, file)
    file.close()
    session.quit()
    print("Uploaded: {}".format(filepath))

# convert image to bits for opencv
def image_to_bts(frame):
    _, bts = cv2.imencode('.webp', frame)
    bts = bts.tobytes()
    return bts

# convert bits to image for opencv
def bts_to_img(bts):
    buff = numpy.frombuffer(bts, numpy.uint8)
    buff = buff.reshape(1, -1)
    img = cv2.imdecode(buff, cv2.IMREAD_COLOR)
    return img

# handle device info
class Device:
    def __init__(self):
        with open('controller.json', 'r') as jsonfile:
            jsondata = jsonfile.read()
        self.info = json.loads(jsondata)

    def get(self, item):
        return self.info[item]

# handle device connection
class Wireless:
    def __init__(self, ssid, pw, os):
        self.ssid = ssid
        self.pw = pw
        self.os = os

    def connect(self):
        print("Waiting for Camera Signal...")
        time.sleep(3)
        if self.os == "osx":
            cam_connect = subprocess.Popen(["networksetup","-setairportnetwork","en0",self.ssid,self.pw], stdout=subprocess.PIPE)
            print(cam_connect)
            cam_connect.wait()
            cam_connect_result = -len(cam_connect.communicate()[0].decode("utf-8"))
            time.sleep(5)
            print(cam_connect_result)
        else:
            cam_connect = subprocess.Popen(["nmcli","-a","d","wifi","connect",self.ssid,"password",self.pw], stdout=subprocess.PIPE)
            cam_connect.wait()
            time.sleep(5)
            cam_connect_result = cam_connect.communicate()[0].decode("utf-8").find("successfully activated")
            print(cam_connect_result)
        return cam_connect_result

# start liveview from pysony
# def liveview():
#     url = s.liveview()
#     lst = s.LiveviewStreamThread(url)
#     lst.start()
#     print('[i] LiveviewStreamThread started.')
#     return lst.get_latest_view, lst.get_frameinfo

class ThreadWithResult(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None):
        def function():
            self.result = target(*args, **kwargs)
        super().__init__(group=group, target=function, name=name, daemon=daemon)

def e():
    e = s.getEvent('false')
    status = e["result"][1]["cameraStatus"]

    return status

def connect():
    e_chk = 0
    while True:
        try:
            time.sleep(20)
            e_chk += 1
            print("*"*23)
            print("** e: {} {} ".format(e(), e_chk))
            print("*"*23)
        except:
            print("e: None")
            cam_connect()


def cam_connect():
    global s
    global api

    # try:
    #     s
    # except NameError:
    #     ss = False
    # else:
    #     ss = True

    while w.connect() < 0:
        time.sleep(3)
    else:
        print("******** Ha Ha Ha~ ********")
        s = SonyAPI(QX_ADDR="http://{}:{}".format(d.get('cam_ip'), d.get('cam_port')))
        api = s.getAvailableApiList()
        print("*"*23)
        print(api)
        print("*"*23)

        if 'startRecMode' in (api['result'])[0]:
            print("startRecMode: ", s.startRecMode())
            time.sleep(5)

        api = s.getAvailableApiList()

        print("*"*23)
        print(api)
        print("*"*23)
        print("e: {}".format(e()))
        print("*"*23)
        # print("getAvailableLiveviewSize: ", s.getAvailableLiveviewSize())
        # time.sleep(3)
        #
        # print("setLiveviewFrameInfo: ", s.setLiveviewFrameInfo(param=[{"frameInfo": True}]))
        # time.sleep(3)

        print("{} Connnected.".format(d.get('id')))


def run_f():
    # handler, info = liveview()
    if f:
        # f.get_frame_handle = handler
        # f.get_frame_info = info
        f.run(host='0.0.0.0', port=PORT, debug=False)

if __name__ == "__main__":
    c = ControlPoint()
    d = Device()
    w = Wireless(d.get('cam_ssid'), d.get('cam_pw'), d.get('ctrl_os'))
    print("******** Controller Info ********")
    print(d.get('id'), d.get('cam_ssid'), d.get('cam_pw'))
    print("******** Start Controller ********")
    # thread = Thread(target=cam_connect)
    # thread.daemon = True
    # thread.start()
    thread_f = ThreadWithResult(target=run_f)
    thread_connect = ThreadWithResult(target=connect)
    thread_f.start()
    thread_connect.start()
    # thread_f.join()
    # thread_connect.join()
    # s = thread_connect.result
