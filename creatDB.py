import sqlite3

con = sqlite3.connect('track_db.db')
cursorObj = con.cursor()
cursorObj.execute('''CREATE TABLE track_list
               (article_url    TEXT(100)    NOT NULL PRIMARY KEY);''')
cursorObj.execute('''CREATE TABLE track_record
               (ID INT  NOT NULL PRIMARY KEY,
                article_url    TEXT(100)  NOT NULL,
                article_title    TEXT(100)  NOT NULL,
                Like    INT       DEFAULT '0',
                Dislike    INT    DEFAULT '0',
                Neutral    INT    DEFAULT '0',
                update_dt datetime NOT NULL);''')                
print ("create suc")
con.commit()
con.close()