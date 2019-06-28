from get_index import BaiduIndex
import time,random
if __name__ == "__main__":
    keywords = ['爬虫']
    for i in range(10):
        baidu_index = BaiduIndex(keywords, '2018-01-01', '2019-05-02',idx=i,cookie_path='/home/tao/文档/my_project/spider-BaiduIndex/new_spider_without_selenium/cookis.txt')
        for index in baidu_index.get_index():
            print(i,index,sep=":")
            time.sleep(random.randint(10,20)/10)
            break
