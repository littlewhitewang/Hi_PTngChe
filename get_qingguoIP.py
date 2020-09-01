'''
查询青果ip。不做更新

'''

#_*_encoding: utf-8_*_

import json
import logging
import threading
import time
import requests
from customProxy import get_ip


class QingGuo_ip(object):
    def __init__(self):
        self.TaskID = ''
        self.Key = 'ATB5MFFMOX100UO3'
        self.lock = threading.Lock()

    #获取ip
    def get_ip(self):

        for i in range(5):
            try:
                url = f'https://proxy.qg.net/query?Key={self.Key}'
                proxies = get_ip()
                res = requests.get(url=url, timeout=20, proxies=proxies)
                res.close()
                response = json.loads(res.content.decode('utf-8'))
                # print('获取ip：',response)
                if res.status_code == 200:
                    return response
                return {'msg': '获取ip失败！'}
            except Exception as e:
                print('获取IP失败！')
    #取10个
    def main(self):
        for i in range(10):
            try:
                ipL = []
                res1 = self.get_ip()
                for ip in res1['TaskList'][0]['Data']:
                    ipL.append(ip['host'])
                return ipL
            except Exception as e:
                print('更新青果ip失败！ Error:', e)
            time.sleep(1)

if __name__ == '__main__':
    IPL = QingGuo_ip().main()
    print(IPL)