'''
底层操作
'''

import requests
import config
import bs4
from bs4 import BeautifulSoup
import re
import psycopg2

class Web:
    @staticmethod
    def get(url,**kvargs):
        arg=config.requests_arg
        arg.update(kvargs)
        timeout=arg['timeout']
        max_retry=arg['max_retry']

        retry=0
        while retry<max_retry:
            try:
                r=requests.get(url,timeout=timeout)
                r.raise_for_status()
                return r
            except requests.exceptions.Timeout:
                print('web.get:timeout retry:\n%s'%url)
                retry+=1
            except Exception as e:
                raise e
        raise Exception('web.get:retry times larger than max_retry')

class Praser:
    '''
    解析器
    主要存储各种解析函数
    '''
    def __init__(self):
        self.cid_pattern=re.compile(r'cid=\d+')
        self.categoryid_pattern=re.compile(r'categoryId=\d+')

    def get_raw(self,r):
        '''
        从页面数据中，获取cid,categoryid,content
        args:
            r 返回的responese requests.responese对象
        returns:
            cid int
            categoryid int
            content str
        '''
        url=r.url
        cid=int(self.cid_pattern.search(url).group(0).split('=')[1])
        categoryid=int(self.categoryid_pattern.search(url).group(0).split('=')[1])

        soup=BeautifulSoup(r.text,'lxml')
        body=soup.find('body',attrs={'id':'termBody'})
        content=body.find('div',attrs={'id':'content'})

        return (cid,categoryid,str(content))

class DBConnect:
    '''
    数据库连接
    '''
    def __init__(self):
        self.conn=psycopg2.connect(**config.db_conn)
        self.cursor=self.conn.cursor()

    def close(self):
        return self.conn.close()

    def newcursor(self):
        return self.conn.cursor()

    def commit(self):
        return self.conn.commit()

    def getu(self):
        '''
        获取unget表的所有数据
        return:
            data 元素为所有unget数据的列表
        '''
        self.cursor.execute('SELECT * FROM UNGET;')
        data=self.cursor.fetchall()
        data=list(map(lambda x:x[0],data))
        return data

    def save_raw_content(self,docid,cid,categoryid,content):
        self.cursor.execute('SELECT SAVERAWCONTENT(%d,%d,%d,$$%s$$)'\
        %(docid,cid,categoryid,content))
        result=self.cursor.fetchall()[0]
        return result
