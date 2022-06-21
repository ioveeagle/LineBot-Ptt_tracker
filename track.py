# -*- coding: utf-8 -*-
from ctypes import util
from time import sleep
import requests 
# 導入 BeautifulSoup 模組(module)：解析HTML 語法工具
import bs4
import datetime
import sqlite3
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
 
 
    fileName = 'track.py'+datetime.datetime.now().strftime('day'+'%Y_%m_%d')
    sys.stdout = Logger(fileName + '.log', path=path)

    print(fileName.center(60,'*'))

def track(url):
    # 文章連結
    URL = url
    # 設定Header與Cookie
    my_headers = {'cookie': 'over18=1;'}
    # 發送get 請求 到 ptt 八卦版
    response = requests.get(URL, headers = my_headers)

    #  把網頁程式碼(HTML) 丟入 bs4模組分析
    soup = bs4.BeautifulSoup(response.text,"html.parser")
    #print(soup)
    header = soup.find_all('span','article-meta-value')
    # 標題
    title = header[2].text

    Like = 0
    Dislike = 0
    Neutral = 0

    ## 查找所有html 元素 抓出內容
    main_container = soup.find(id='main-container')
    rows = main_container.find_all('div',class_ = 'push')
    for row in rows:
        sign = row.find('span').get_text().replace(' ','')
        #print('>>>',sign)
        if(sign=='推'): Like+=1
        elif(sign=='噓'): Dislike+=1
        elif(sign=='→'): Neutral+=1

    con = sqlite3.connect('track_db.db')
    cursorObj = con.cursor()
    cursorObj.execute('SELECT * FROM track_record')
    #print(rt)
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sql = f"INSERT INTO track_record (ID,article_url,article_title,Like,Dislike,Neutral,update_dt) VALUES ('{len(cursorObj.fetchall())+1}','{url}','{title}','{Like}','{Dislike}','{Neutral}','{now}')"
    #print(sql)
    cursorObj.execute(sql)
    con.commit()
    con.close()

def on_hot(url):
    time_ed= datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    time_st= (datetime.datetime.now()+datetime.timedelta(hours=-3)).strftime('%Y-%m-%d %H:%M:%S')
    con = sqlite3.connect('track_db.db')
    cursorObj = con.cursor()
    sql = f"SELECT * FROM track_record WHERE article_url = '{url}' AND ( update_dt BETWEEN '{time_st}' AND '{time_ed}' ) ORDER BY ID DESC"
    #print(sql)
    cursorObj.execute(sql)
    select_list = cursorObj.fetchall()
    #print(select_list)
    if len(select_list) >1:
    
        latest = select_list[0]
        oldest = select_list[-1]

        Like_Variety = latest[3] - oldest[3]
        Dislike_Variety = latest[4] - oldest[4]
        Neutral_Variety = latest[5] - oldest[5]

        con.commit()
        con.close()
        if hot_algo(Like_Variety,Dislike_Variety,Neutral_Variety) != "none":
            return hot_algo(Like_Variety,Dislike_Variety,Neutral_Variety),latest[2]
        else:
            de_artivle(url)
            print("文章無人回應 刪除")
            return "cold",latest[2]
    else:
        print("資料量: ",len(select_list))
        if hot_algo(select_list[0][3],select_list[0][4],select_list[0][5]) != "none":
            return hot_algo(select_list[0][3],select_list[0][4],select_list[0][5]),latest[2]
        else:
            print("文章目前無人回應")
            return "none",latest[2]

def hot_algo(Like_Variety,Dislike_Variety,Neutral_Variety):
    if(Like_Variety+Dislike_Variety+Neutral_Variety>=8):
        return "熱烈討論"
    else:
        return "none"

# def rm_article(url):
#     con = sqlite3.connect('track_db.db')
#     cursorObj = con.cursor()
#     sql = f"DELETE FROM track_list WHERE article_url = '{url}'"
#     #print(sql)
#     cursorObj.execute(sql)
#     con.commit()
#     con.close()
    

def set_schedule():
    push_list=[]
    con = sqlite3.connect('track_db.db')
    cursorObj = con.cursor()
    print ("DB連接成功")
    cursorObj.execute('SELECT * FROM track_list')
    track_list = cursorObj.fetchall()
    
    for row in track_list:
        print("-"*50)
        try:
            track((row[0]))
            print("推噓數更新完畢...分析文章熱門程度")
            result,title = on_hot(row[0])
            if result == 'cold':
                print("不熱門了")
            elif result == 'none':
                print("只有一筆留言")
            else:
                rt = {
                    "文章標題":title,
                    "文章網址":row[0],
                    "state":result
                }
                push_list.append(rt)
                
            print("分析完成")
        except: 
            print("ERROR  ",row[0])
        
        # else:
        #     rm_article(row[0])
    
    print("-"*50)
    print("推播列表",push_list)
    #line_notify(push_list)
    #line_notify1(push_list)
    #line_notify2(push_list)
    print("作業完畢...兩小時後再次執行")
    con.commit()
    con.close()

def de_artivle(url):
    con = sqlite3.connect('track_db.db')
    cursorObj = con.cursor()
    sql = f"DELETE FROM track_list WHERE article_url = '{url}'"
    #print(sql)
    cursorObj.execute(sql)
    print("取消追蹤",url)
    con.commit()
    con.close()

# def line_notify(push_list): #Kyu用
#     headers = {
#             "Authorization": "Bearer " + "rxNWqyeauITvxtqi1lip9V9Ku36GuoLqozCVPO423Qj",
#             "Content-Type": "application/x-www-form-urlencoded"
#     }
#     if len(push_list) > 0:  
#         for push in push_list:
#             context ="\n"
#             for i in push:
#                 context += f"{i}: {push[i]}\n"
#             params = {"message": context}
#     else:
#         params = {"message": "目前無熱門討論文章"}
#     print(params)
#     r = requests.post("https://notify-api.line.me/api/notify",headers=headers, params=params)
#     print(r.status_code)  #200

def line_notify1(push_list): #with老師
    headers = {
            "Authorization": "Bearer " + "IBEqUd6OrDNS96RTWTAvvlNVpzV5hCRUNwuIEul1EQl",
            "Content-Type": "application/x-www-form-urlencoded"
    }
    if len(push_list) > 0:  
        for push in push_list:
            context ="\n"
            for i in push:
                context += f"{i}: {push[i]}\n"
            params = {"message": context}
    else:
        params = {"message": "目前無熱門討論文章"}
    print(params)
    r = requests.post("https://notify-api.line.me/api/notify",headers=headers, params=params)
    print(r.status_code)  #200

def line_notify2(push_list): #with警署
    headers = {
            "Authorization": "Bearer " + "TaHafyuzXC1wbUneUMHiJHusW55Mxd6AjmJ92aJzrCN",
            "Content-Type": "application/x-www-form-urlencoded"
    }
    if len(push_list) > 0:  
        for push in push_list:
            context ="\n"
            for i in push:
                context += f"{i}: {push[i]}\n"
            params = {"message": context}
    else:
        params = {"message": "目前無熱門討論文章"}
    print(params)
    r = requests.post("https://notify-api.line.me/api/notify",headers=headers, params=params)
    print(r.status_code)  #200


if __name__ == '__main__':
    make_print_to_file(path='log')
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("執行中")
    set_schedule() #先執行一次
    schedule.every(2).hours.do(set_schedule)    #每隔一小時執行一次任務
    while(True):
        schedule.run_pending()    #run_pending：執行所有可以執行的任務
        sleep(1)    #睡眠1秒