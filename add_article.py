# -*- coding: utf-8 -*-
from time import sleep
import requests
import datetime
import sqlite3
import datetime
import time
import json
import schedule
import sys
import os
import config_file as cfg_file


def make_print_to_file(path='./'):
    '''
    path， it is a path for save your log about fuction print
    example:
    use  make_print_to_file()   and the   all the information of funtion print , will be write in to a log file
    :return:
    '''
 
    class Logger(object):
        def __init__(self, filename="Default.log", path="./"):
            self.terminal = sys.stdout
            self.log = open(os.path.join(path, filename), "a", encoding='utf8',)
 
        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)
 
        def flush(self):
            pass
 
 
    fileName = 'add_article.py'+datetime.datetime.now().strftime('day'+'%Y_%m_%d')
    sys.stdout = Logger(fileName + '.log', path=path)

    print(fileName.center(60,'*'))


def track(url):
    con = sqlite3.connect('track_db.db')
    cursorObj = con.cursor()
    print ("DB連接成功...")
    cursorObj.execute('SELECT * FROM track_list ')
    try:
        sql = f"INSERT INTO track_list (article_url) VALUES ('{url}')"
        #print(sql)
        cursorObj.execute(sql)
        con.commit()
        con.close()
        return "文章新增成功"
    except:
        return "文章新增失敗"
    

def call_server(today_st_int,today_ed_int):
    url_list=[]
    key_list = ['戴帽子','賊頭','有牌的流氓','波麗士','條子','警察','警官','阿sir','刑事伯','警員','警署','分局','警員','鴿子','派出所']
    my_headers = {'cookie': 'over18=1;'}
    for key in key_list:
        URL = f"http://140.120.13.248:31111/api/GetByContent?content={key}&start={today_st_int}&end={today_ed_int}&size=200&from=0"
        response = requests.get(URL, headers = my_headers)
        context = json.loads(response.text)
        #print(context)
        for i in context["hits"]:
            if(i["_source"]["type"]=="article"):
                print("新增",i["_source"]["article_title"])
                url_list.append(i["_source"]["article_url"])
    #去掉重複URL
    unique_set = set(url_list)
    url_list = list(unique_set)            
    #print(url_list)
    return url_list

def set_schedule():
    #先抓時間區間轉成時間戳
    today_ed= datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    today_st= (datetime.datetime.now()+datetime.timedelta(hours=-2)).strftime('%Y-%m-%d %H:%M:%S')
    today_st_int = int(time.mktime(time.strptime(today_st, "%Y-%m-%d %H:%M:%S")))
    today_ed_int = int(time.mktime(time.strptime(today_ed, "%Y-%m-%d %H:%M:%S")))
    print(today_ed)
    url_list = call_server(today_st_int,today_ed_int)
    for url in url_list:
        print(url,track(url))
    print("作業完畢...兩小時後再次執行")
        

if __name__ == '__main__':
    make_print_to_file(path='log')
    print("執行中")
    set_schedule() #先執行一次
    schedule.every(2).hours.do(set_schedule)    #每隔一小時執行一次任務
    while(True):
        schedule.run_pending()    #run_pending：執行所有可以執行的任務
        sleep(1)    #睡眠1秒
    
        


