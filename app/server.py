#!/usr/bin/env python
# Created By: Addie Liu | liuaddie@gmail.comapp = Flask(__name__)
# https://realpython.com/python-concurrency/
# https://python-parallel-programmning-cookbook.readthedocs.io/zh_CN/latest/chapter4/02_Using_the_concurrent.futures_Python_modules.html
import os
import json
import concurrent.futures
import requests
import threading
import time
from flask import Flask, redirect, url_for, render_template, request, flash
app = Flask(__name__)
PORT = int(os.environ.get('PORT', 9090))

cams = {'http://192.168.23.141:3030/', 'http://192.168.23.184:3030/', 'http://192.168.23.211:3030/', 'http://192.168.23.149:3030/'}
# cams = {'http://192.168.23.141:3030/'}

thread_local = threading.local()

def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session

def download_site(url):
    session = get_session()
    with session.get(url) as response:
        print(f"Read {len(response.content)} from {url}")

def download_all_sites(sites):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(download_site, sites)

@app.route('/')
def index():
    return render_template("server.html", A1='http://192.168.23.141:3030/video_feed', A2='http://192.168.23.184:3030/video_feed', A3='http://192.168.23.211:3030/video_feed', A4='http://192.168.23.149:3030/video_feed')
    # return render_template("server.html", A1='{}video_feed'.format(cams[0]), A2='{}video_feed'.format(cams[1]), A3='{}video_feed'.format(cams[2]),A4='{}video_feed'.format(cams[3]))

@app.route("/video_feeds")
def video_feeds():
    """Route which renders solely the video"""
    A001 = 'http://192.168.23.109:3030/video_feed'
    return A001

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
        start_time_2 = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(evaluate_item, cam) for cam in cams]
            for future in concurrent.futures.as_completed(futures):
                print(future.result())

        # for cam in cams:
        #     cam = '{}cam_control'.format(cam)
        #     requests.post(cam, data=request.form)
            # response = requests.post(cam, data=request.form)
            # print(cam, response)
    if action == 'shoot_dl':
        postview = s.send_basic_cmd_r("actTakePicture")
        url = postview['result'][0][0]
        print(url)
        self.take += 1
        download = requests.get(url, allow_redirects=True)
        if url.find('/'):
            filename = "Take{}_{}_{}".format(self.take, d.get('id'), url.rsplit('/', 1)[1])
            print(filename)
        filepath = '_temp/{}'.format(filename)
        open(filepath, 'wb').write(download.content)

        session = ftplib.FTP('192.168.23.253','lawyankin','G9XOQr5a5Znh')
        file = open(filepath,'rb')
        folder = "/home/20210324/Take{}".format(self.take)
        # chdir(folder)
        # ftpcmd = "mkdir {}".format(folder)          # file to send
        try:
            session.mkd(folder)     # send the file
        except:
            pass
        ftpcmd = "STOR {}/{}".format(folder, filename)              # file to send
        session.storbinary(ftpcmd, file)     # send the file
        file.close()                                    # close file and FTP
        session.quit()


    if action == 'set':
        print("**Setting**")
        print(cmd)
        # print(param)
        params = [param]
        print(params)
        r = s.send_basic_cmd_r(cmd, params)
        print(r)
    return action
    return action

def count(number) :
    for i in range(0, 10000000):
        i=i+1
    return i * number

def evaluate_item(x):
    requests.post(x, data=request.form)
        # 计算总和，这里只是为了消耗时间
    # result_item = count(x)
        # 打印输入和输出结果
    # return result_item

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
