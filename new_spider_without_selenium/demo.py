from get_index import get_keyword_index
import time,random

if __name__ == "__main__":
    keywords = ['爬虫','5G']*80
    for word in keywords:
        try:
            result=get_keyword_index(word,'2019-06-01','2019-06-10')
        except Exception as err:
            print(err)
            continue
        i=0
        for item in result:
            i+=1
            if i == 2:
                print(item)
        print(word,i,sep=':')
        
