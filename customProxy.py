# -*- coding: utf-8 -*-
import random

PROXIES = [

]


def read_proxy():
    # f = open(r"C:\Users\Administrator\Desktop\车牌信息\在场车 - 副本.txt")
    f = open(".\\ip.txt")
    # f = open(r"C:\Users\Administrator\Desktop\车牌信息\投哪的.txt")
    # f = open(r"C:\Users\Administrator\Desktop\车牌信息\多车牌2.txt")

    line = f.readline()

    while line:
        item = line.replace('"', '').replace(' ', '').replace('\t', '').replace('\n', '').upper()
        PROXIES.append(item)
        line = f.readline()
    f.close()
    # for ip in PROXIES:
    #     print(ip)


read_proxy()


class RandomProxy(object):
    def random(self):
        proxy = random.choice(PROXIES)
        return proxy


def get_ip():
    r_proxy = RandomProxy()
    new_ip = r_proxy.random()
    ip = {'http': 'http://tangheng:Xcw168TH@%s:9499' % new_ip,
          'https': 'https://tangheng:Xcw168TH@%s:9499' % new_ip
          }
    return ip


if __name__ == '__main__':
    read_proxy()

    r_proxy = RandomProxy()
    ip = r_proxy.random()
    print(ip)
