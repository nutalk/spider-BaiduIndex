from urllib.parse import urlencode
import queue
import math
import datetime
import random
import time
import json,os

import requests

from config import PROVINCE_CODE, CITY_CODE
from utils import NotLoginError,BadRequestError
from retry import retry

headers = {
    'Host': 'index.baidu.com',
    'Connection': 'keep-alive',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
}


class BaiduIndex:
    """
        百度搜索指数
        :keywords; list
        :start_date; string '2018-10-02'
        :end_date; string '2018-10-02'
        :area; int, search by cls.province_code/cls.city_code
    """

    province_code = PROVINCE_CODE
    city_code = CITY_CODE
    _all_kind = ['all', 'pc', 'wise']
    

    def __init__(self, keywords: list, start_date: str, end_date: str,idx=None,area=0,cookie_path=None):
        COOKIES_PATH='/home/tao/文档/my_project/spider-BaiduIndex/new_spider_without_selenium/cookies_100.txt'
        self.keywords = keywords
        self._area = area
        self._params_queue = queue.Queue()
        self._init_queue(start_date, end_date, keywords)
        if cookie_path is None:
            cookie_path=COOKIES_PATH
        self.cookies_list=[]
        with open(cookie_path,'r') as f:
            for line in f:
                line=line.strip()
                self.cookies_list.append(line)
        if idx is None:
            cookies=random.sample(self.cookies_list,1)
            headers['Cookie'] = cookies[0]
        else:
            headers['Cookie'] = self.cookies_list[idx]

    def get_index(self):
        """
        获取百度指数
        返回的数据格式为:
        {
            'keyword': '武林外传',
            'type': 'wise',
            'date': '2019-04-30',
            'index': '202'
        }
        """
        while 1:
            try:
                params_data = self._params_queue.get(timeout=1)
                encrypt_datas, uniqid = self._get_encrypt_datas(
                    start_date=params_data['start_date'],
                    end_date=params_data['end_date'],
                    keywords=params_data['keywords']
                )
                key = self._get_key(uniqid)
                for encrypt_data in encrypt_datas:
                    for kind in self._all_kind:
                        encrypt_data[kind]['data'] = self._decrypt_func(
                                key, encrypt_data[kind]['data'])
                    for formated_data in self._format_data(encrypt_data):
                        yield formated_data
            except requests.Timeout:
                self._params_queue.put(params_data)
            except queue.Empty:
                break
            self._sleep_func()

    def _init_queue(self, start_date, end_date, keywords):
        """
            初始化参数队列
        """
        time_range_list = self._get_time_range_list(start_date, end_date)
        for start_date, end_date in time_range_list:
            params = {
                'keywords': keywords,
                'start_date': start_date,
                'end_date': end_date
            }
            self._params_queue.put(params)

    def _get_encrypt_datas(self, start_date, end_date, keywords):
        """
        :start_date; str, 2018-10-01
        :end_date; str, 2018-10-01
        :keyword; list, ['1', '2', '3']
        """
        request_args = {
            'word': ','.join(keywords),
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
            'area': self._area,
        }
        url = 'http://index.baidu.com/api/SearchApi/index?' + urlencode(request_args)
        html = self._http_get(url)
        datas = json.loads(html)
        if 'bad request' in html:
            time.sleep(random.randint(2,5))
            raise BadRequestError(keywords[0])
        if 'not login' in html:
            raise NotLoginError(headers['Cookie'])
        uniqid = datas['data']['uniqid']
        encrypt_datas = []
        for single_data in datas['data']['userIndexes']:
            encrypt_datas.append(single_data)
        return (encrypt_datas, uniqid)

    def _get_key(self, uniqid):
        """
        """
        url = 'http://index.baidu.com/Interface/api/ptbk?uniqid=%s' % uniqid
        html = self._http_get(url)
        datas = json.loads(html)
        key = datas['data']
        return key

    def _format_data(self, data):
        """
            格式化堆在一起的数据
        """
        keyword = str(data['word'])
        time_length = len(data['all']['data'])
        start_date = data['all']['startDate']
        cur_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        for i in range(time_length):
            for kind in self._all_kind:
                index_datas = data[kind]['data']
                index_data = index_datas[i] if len(index_datas) != 1 else index_datas[0]
                formated_data = {
                    'keyword': keyword,
                    'type': kind,
                    'date': cur_date.strftime('%Y-%m-%d'),
                    'index': index_data if index_data else '0'
                }
                yield formated_data
            cur_date += datetime.timedelta(days=1)

    def _http_get(self, url):
        """
            发送get请求, 程序中所有的get都是调这个方法
            如果想使用多cookies抓取, 和请求重试功能
            在这自己添加
        """
        
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            raise requests.Timeout
        return response.text

    def _get_time_range_list(self, startdate, enddate):
        """
            切分时间段
        """
        date_range_list = []
        startdate = datetime.datetime.strptime(startdate, '%Y-%m-%d')
        enddate = datetime.datetime.strptime(enddate, '%Y-%m-%d')
        while 1:
            tempdate = startdate + datetime.timedelta(days=300)
            if tempdate > enddate:
                date_range_list.append((startdate, enddate))
                break
            date_range_list.append((startdate, tempdate))
            startdate = tempdate + datetime.timedelta(days=1)
        return date_range_list

    def _decrypt_func(self, key, data):
        """
            数据解密方法
        """
        a = key
        i = data
        n = {}
        s = []
        for o in range(len(a)//2):
            n[a[o]] = a[len(a)//2 + o]
        for r in range(len(data)):
            s.append(n[i[r]])
        return ''.join(s).split(',')

    def _sleep_func(self):
        """
            sleep方法, 单账号抓取过快, 一段时间内请求会失败
        """
        sleep_time = random.choice(range(50, 90)) * 0.1
        time.sleep(sleep_time)

@retry(NotLoginError,tries=5,delay=3)
def get_keyword_index(word,start_date,end_date,idx=None,area=0,cookie_path=None):
    """获取百度指数
    
    Arguments:
        word {str} -- 关键词
        start_date {str} -- '2019-01-01'
        end_date {str} -- '2019-01-01'
        area {int} -- 0
        cookie_path {str} -- cookie path
    
    Returns:
        list -- list contain all datas
    """
    print('trying:',word)
    baidu_index = BaiduIndex([word],start_date,end_date,idx=idx,area=area,cookie_path=cookie_path)
    result=[]
    for item in baidu_index.get_index():
        result.append(item)
    return result
