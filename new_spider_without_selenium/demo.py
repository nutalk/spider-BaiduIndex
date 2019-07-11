from get_index import get_keyword_index
import time,random

if __name__ == "__main__":
    keywords = ['工业','5G']*30
    for idx,word in enumerate(keywords):
        try:
            result=get_keyword_index(word,'2019-06-01','2019-06-10',idx=idx)
        except Exception as err:
            print(err)
            continue
        i=0
        for item in result:
            i+=1
            if i == 2:
                print(item)
                break
        
