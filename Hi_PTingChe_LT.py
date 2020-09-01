'''
Hi_P停车公众号：
时间： 8-24

入口： 公众号，临停入口

8-28 第一批32个ip被封。

现用新一批前2 个。
8-31: ip限制，更换2个
目前已用IP：
106.53.124.164
106.55.0.226
106.55.0.127
106.55.1.130

全部ip已已用。先用青果ip 10 通道

'''

import datetime
import json
import logging
import threading
from multiprocessing.pool import ThreadPool
import requests
from fake_useragent import fake, UserAgent
from customProxy import get_ip
import re
import time
import random
# 设置日志等级和格式
from gevent.threadpool import ThreadPoolExecutor
from lxml import etree

from get_qingguoIP import QingGuo_ip

file = open('Hi_PTingChe.log', encoding='utf-8', mode='w')
logging.basicConfig(level=logging.ERROR,  # 控制台打印的日志级别
                    # filename='Hi_PTingChe.log',
                    # filemode='w',  ##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志a是追加模式，默认如果不写的话，就是追加模式
                    stream=file,
                    # 日志格式
                    format=
                    '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                    )
ua = UserAgent()


class Hi_PTingChe_Spider(object):
    def __init__(self):
        self.Session = requests.Session()
        self.Session.keep_alive = False
        self.n = 0
        self.iplist = []

    # 发送请求
    def get_mes(self, car_no):
        url = 'https://toc.sunsea.net/payment/orderWithCoupons'
        # 失败后重试
        for i in range(5):
            try:
                data = {
                    'plateNumber': car_no,
                    'coupons': ''
                }
                headers = {
                    'User-Agent': ua.random,
                    'consumerId': '',

                }
                # proxies = get_ip()
                # proxies = {'https': 'http://tangheng:Xcw168TH@47.92.227.143:9499'}
                proxies = {'https': 'https://%s' % random.choice(self.iplist)}
                res = self.Session.get(url=url, params=data, proxies=proxies, headers=headers, timeout=10)#
                res.close()
                response = res.content.decode('utf-8')
                self.n += 1
                print(self.n, res.status_code, f'--{datetime.datetime.now()}--', proxies, response)
                if res.status_code == 200:
                    return json.loads(response)
                elif res.status_code == 509:
                    time.sleep(1)
                    return self.get_mes(car_no)
            except Exception as e:
                logging.warning('%s 其他错误！Error: %s', car_no, e)
            # logging.warning('车牌%s：进行第%s次重试', car_no, i + 1)
            if i == 4:
                logging.error('车辆%s查询失败！', car_no)

    # 解析返回数据
    def parse(self, car_no, res):
        try:
           if res['data']['parkName']:
               return res['data']
        except Exception as e:
            logging.error('%s - Parse Error: %s', car_no, str(res))

    # 获取车牌
    def get_car_no(self, number):
        while True:
            url = 'http://106.54.123.234:19999/platNumber/getDataPackage/Hi_PTingChe/%d' % number
            try:
                res = self.Session.get(url=url, timeout=2)
                res.close()
                # print(res.text)  # {"code":0,"msg":"(0)成功","content":["粤VLT000","粤WMU837"]}
                result = json.loads(res.text)
                car_no_list = result['content']
                # logging.info("获取车牌成功！%s", car_no_list)
                return car_no_list
            except Exception as e:
                logging.error('获取车牌列表失败！Error:%s', e)

    # 发送车辆信息
    def send_mes(self, mes):
        t = time.mktime(time.strptime(mes['inDt'], "%Y%m%d%H%M%S"))  # 年月日对象转时间戳
        # t = int(time.time()) # 时间戳对象
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
        data = {
            "uniqueMark": 'Hi_PTingChe' + '_' + str(mes['carNum']) + '_' + str(int(t)),  # 停车场平台名称首字母缩写_车牌_入场时间秒戳
            "parkingId": mes['parkId'],  # 停车场唯一编码(18000100200524)
            "parkingName": mes['parkName'],  # 停车场名字
            "platform": 'Hi_PTingChe',  # 平台拼英缩写'
            "plateNumber": mes['carNum'],  # 车牌
            "platformAlias": "Hi_P停车",  # 平台名称别名（给不懂技术人员看）  CTP车钱包公众号
            "detailAddress": '',  # 详细位置
            "position": '',  # 经纬度   (经度,纬度)
            "formatAriseTime": dt,  # 格式化后时间（2020-04-13 09:58:51）
            "ariseTimeLong": int(t * 1000),  # 入场时间戳（毫秒）
            "ariseImg": '',  # 入场图片url
            "otherInfo": ""  # 附带信息（月卡，停车位置详细说明等）
        }
        params = {
            # 'json': json.dumps(data),
            'json': str(data),
            "type": "small",
        }
        self.send_to_spiser(params)
        # print(params)
        # return None
        for i in [30, 60, 180, 360, 720, 900]:
            try:
                basurl = 'http://106.54.123.234:19999'
                url = basurl + '/unified/submitData'
                res = self.Session.get(url=url, params=params, timeout=10)
                res.close()
                if res.status_code == 200:
                    print('Hi_P停车--', datetime.datetime.now().replace(microsecond=0), res.text, params)
                    return None
            except Exception as e:
                logging.error('信息上传失败：%s', e)
            logging.error('%s-信息上传失败,正在重试！', data['plateNumber'])
            time.sleep(i)

    # 控制调用函数
    def start(self, car_no):
        response = self.get_mes(car_no)
        if response:
            mes_data = self.parse(car_no, response)
            if mes_data:
                self.send_mes(mes_data)

    # 发送数据到监控系统
    def send_to_spiser(self, mes):
        for i in range(2):
            try:
                data = {'mes': str(mes)}
                url = 'http://106.53.220.9:5000/insert_mes'
                res = self.Session.get(url=url, params=data)
                # print(res.url)
                res.close()
                print(res.text)
                if json.loads(res.text)['code'] == 000 or json.loads(res.text)['code'] == "000":
                    return None
            except Exception as e:
                print('向监控系统提交数据失败！Errot: %s' % e)

    def get_newip(self):
        getip = QingGuo_ip()
        while True:
            try:
                self.iplist = getip.main()
                print(self.iplist)
                time.sleep(10 * 1)
            except Exception as e:
                print(e)

    # 主函数ps：设置多线程或多进程等
    def main(self):
        time1 = time.time()
        n = 1
        # self.start('粤E701DU')
        thread = threading.Thread(target=self.get_newip)
        thread.start()
        time.sleep(3)
        while True:
            print('Hi_P停车--', '%s---Running! %s' % (datetime.datetime.now(), time.time() - time1))
            car_number = 5000
            car_no_list = self.get_car_no(car_number)
            # print(car_no_list)
            with ThreadPoolExecutor(5) as exector:  # 使用with来管理ThreadPoolExecutor
                # map方法和内置的map方法类似，不过exector的map方法会并发调用，返回一个由返回的值构成的生成器
                exector.map(self.start, car_no_list)
            if n % 2 == 0:
                time2 = time.time()
                print('Hi_P停车--', '%s--One thouhend need time %s' % (
                    time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), (time2 - time1)))
                data = {
                    'json': {'platformAlias': 'Hi_P停车', 'time': str(datetime.timedelta(seconds=time2 - time1))},
                    'type': 'time'
                }
                self.send_to_spiser(data)
                time1 = time2
            n += 1


if __name__ == '__main__':
    Hi_PTingChe_Spider().main()
