'''
底层操作
'''

import requests
import config
import bs4
from bs4 import BeautifulSoup
import re
import psycopg2
from multiprocessing import Lock,Semaphore,Manager,Process

from _base.parse.get_content import get_content
from _base.parse.wordsplit import split as wordsplit
from _base.parse.common import tag2string

requests.adapters.DEFAULT_RETRIES=config.web['low_level_retry']

class Web:
    '''
    web连接类
    '''
    def __init__(self):
        '''
        为了提升性能，使用一个session，不keep-alive的连接方式
        '''
        self.s=requests.session()
        self.s.keep_alive=False

    def get(self,url,**kvargs):
        arg=config.web
        arg.update(kvargs)
        timeout=arg['timeout']
        max_retry=arg['max_retry']

        retry=0
        while retry<max_retry:
            try:
                r=self.s.get(url,timeout=timeout)
                r.raise_for_status()
                return r
            except requests.exceptions.Timeout:
                retry+=1
                print('web.get:timeout retry:%d times\n%s'%(retry,url))
            except requests.exceptions.HTTPError:
                if r.status_code==404:
                    raise Exception('404')
                retry+=1
            except requests.exceptions.ConnectionError:
                retry+=1
            except Exception as e:
                print('web.get')
                print(e)
                raise e
        raise Exception('web.get:retry times larger than max_retry')

class Parser:
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

    def parse_raw_content(self,raw_content):
        '''
        将raw content解析为可以进入数据库的数据的方法
        args:raw_content (str) 未解析的数据
        return: cite,word,cw,jw,kw,ew,content
        cite:引用字段
        word:词字段
        desc:desc字段
        cw,jw,kw,ew:chinese word;japanese word;korean word;english word
        content (key1,key2,...,keyn)
        '''

        soup=BeautifulSoup(raw_content,'lxml')
        title=soup.find('div',{'class':'headword_title'})
        cite=tag2string(title.find('p',{'class':'cite'}))
        word=tag2string(title.find('h2',{'class':'headword'}))
        desc=tag2string(title.find('p',{'class':'desc'}))
        cw,jw,kw,ew=wordsplit(title.find('p',{'class':'word'}))
        content=get_content(soup.find('div',{'id':'size_ct'}))
        return cite.strip('\n'),word,desc,cw,jw,kw,ew,content
        pass

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
        #print('executing command')
        self.cursor.execute('SELECT SAVERAWCONTENT(%d,%d,%d,$DATA$%s$DATA$);'\
        %(docid,cid,categoryid,content))
        #print('fetching result')
        result=self.cursor.fetchall()[0]
        return result

    def save_category_doc(self,categoryid,docid):
        self.cursor.execute('SELECT SAVE_CATEGORY_DOC(%d,%d);'%(categoryid,docid))
        result=self.cursor.fetchall()[0]
        return result

manager=Manager()

class PQ:
    '''
    进程之间的通信队列类
    '''
    def __init__(self):
        self.lock=Lock()
        self.signal=Semaphore(0)
        #self.manager=Manager()
        #self.q=self.manager.list()
        self.q=manager.list()

    def put(self,data):
        self.lock.acquire()
        self.q.append(data)
        self.signal.release()
        self.lock.release()

    def get(self):
        self.signal.acquire()
        self.lock.acquire()
        data=self.q.pop(0)
        self.lock.release()
        return data

    def put_many(self,data):
        '''
        将一个列表直接放进去，避免频繁操作
        '''
        self.lock.acquire()
        print('put_list:get the lock')
        size=len(data)
        self.q+=data
        print('put_list:the queue add the list success')
        for i in range(len(data)):
            self.signal.release()
        print('re-init the signal success')
        self.lock.release()
        print('put list success')

    def get_many(self,data,num=1000):
        '''
        获取size数量的data，返回一个列表
        如果列表剩下不足size个，则全部返回
        '''
        self.lock.acquire()
        size=len(self.q)
        if(size>num):
            temp=self.q[:num]
            self.q=self.q[num:]
            getted_num=num
        else:
            getted_num=size
            temp=self.q[:]
            self.q=manager.list()
        for i in range(getted_num):
            self.signal.acquire()
        self.lock.release()
        return temp
