import concurrent.futures
import time
import requests
headers = {'User-Agent': 'Mozilla/5.0'}
payload = {'action':'shoot_dl', 'cmd':'', 'param':''}
# https://stackoverflow.com/questions/20759981/python-trying-to-post-form-using-requests
number_list = ['http://192.168.23.141:3030/', 'http://192.168.23.184:3030/', 'http://192.168.23.211:3030/']

def evaluate_item(x):
        # 计算总和，这里只是为了消耗时间
        result_item = count(x)
        # 打印输入和输出结果
        return result_item

def count(cam):
    cam = '{}cam_control'.format(cam)
    session = requests.Session()
    session.post(cam,headers=headers,data=payload)
    # requests.post(cam, data=request.form)
    # for i in range(0, 10000000):
    #     i=i+1
    # return i * number

if __name__ == "__main__":
        # # 顺序执行
        # start_time = time.time()
        # for item in number_list:
        #         print(evaluate_item(item))
        # print("Sequential execution in " + str(time.time() - start_time), "seconds")
        # # 线程池执行
        # start_time_1 = time.time()
        # with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        #         futures = [executor.submit(evaluate_item, item) for item in number_list]
        #         for future in concurrent.futures.as_completed(futures):
        #                 print(future.result())
        # print ("Thread pool execution in " + str(time.time() - start_time_1), "seconds")
        # 进程池
        start_time_2 = time.time()
        with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(evaluate_item, item) for item in number_list]
                for future in concurrent.futures.as_completed(futures):
                        print(future.result())
        print ("Process pool execution in " + str(time.time() - start_time_2), "seconds")
