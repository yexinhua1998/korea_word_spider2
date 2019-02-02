import base
import threading
from queue import Queue as TQ
from base import PQ
from multiprocessing import Process,Manager,Lock,Semaphore
import config


class SpiderThread(threading.Thread):
    '''
    爬取词条页面的线程类
    '''
    def __init__(self,q_in,q_out,tid):
        threading.Thread.__init__(self)
        self.q_in=q_in
        self.q_out=q_out
        self.tid=tid

    def run(self):
        print('SpiderThread%d start'%self.tid)
        while True:
            docid=self.q_in.get()
            url='https://terms.naver.com/entry.nhn?docId=%d'%docid
            try:
                r=base.Web.get(url)
                #print('get doc %d success'%docid)
            except Exception as e:
                #with open('spider_log.txt','a',encoding='utf-8') as f:
                #    f.write(str(e))
                #print('error:url=%s'%url)
                r=None
            self.q_out.put((docid,r))
        pass

def subcrawl(q_in,crawl2prase,thread_amount):
    '''
    爬取的子进程
    '''
    q1=TQ()
    q2=TQ()
    tlist=[SpiderThread(q1,q2,i+1) for i in range(thread_amount)]
    for t in tlist:
        t.start()
    while True:
        data=q_in.get()
        print('get data:%d'%data)
        if data is None:
            break
        q1.put(data)
    print('None is getted')

    while True:
        data=q2.get()
        crawl2prase.put(data)
        print('transfer doc %d to praser'%data[0])

    for t in tlist:
        t.join()
    pass


def crawl(crawl2prase,thread_amount=64,p_amount=4):
    '''
    爬取函数
    '''
    connect=base.DBConnect()
    u=connect.getu()
    connect.close()
    q_in=PQ()
    plist=[Process(target=subcrawl,args=(q_in,crawl2prase,thread_amount))
    for i in range(p_amount)]
    for p in plist:
        p.start()
    print('putting u to q_in')
    q_in.put_many(u)
    print('all u is put 2 subcrawl')
    for i in range(p_amount):
        q_in.put(None)#给出结尾
    print('None is put tu subcrawl')

    for p in plist:
        p.join()
    pass

def prase_responese(q_in,q_out):
    praser=base.Praser()
    while True:
        docid,r=q_in.get()

        if r==None:
            cid,categoryid,content=0,0,''
        else:
            cid,categoryid,content=praser.get_raw(r)

        q_out.put((docid,cid,categoryid,content))
        print('prase doc %d'%docid)
    pass

class ContentSaver(threading.Thread):
    '''
    保存content的线程
    '''
    def __init__(self,q,tid):
        threading.Thread.__init__(self)
        self.q=q
        self.tid=tid
        self.conn=base.DBConnect()

    def run(self):
        print('ContentSaver%d: start'%self.tid)
        n=config.content_saver_arg['commit_amount']
        #counter=0
        while True:
            data=self.q.get()
            result=self.conn.save_raw_content(*data)
            print('save doc %d'%data[0])
            if not result:
                raise Exception('ContentSaver:save content fail.')
            #counter+=1
            #if counter%n==0:
            self.conn.commit()
        pass

def save_content(q_in,thread_amount=64):
    '''
    将爬取到的页面保存到数据库
    '''
    q2thread=TQ()
    tlist=[ContentSaver(q2thread,i+1) for i in range(thread_amount)]
    for t in tlist:
        t.start()

    while True:
        data=q_in.get()
        q2thread.put(data)
    for t in tlist:
        t.join()
    pass

def spider(**kvargs):
    arg=config.spider_arg
    arg.update(kvargs)

    crawl2prase=base.PQ()
    prase2save=base.PQ()

    crawlp=Process(target=crawl,
    args=(crawl2prase,arg['crawler_thread_amount'],arg['crawler_p_amount']))
    crawlp.start()

    praser_list=[Process(target=prase_responese,
    args=(crawl2prase,prase2save))
    for i in range(arg['praser_amount'])]
    for p in praser_list:
        p.start()

    savep=Process(target=save_content,
    args=(prase2save,arg['saver_thread_amount']))
    savep.start()

    crawlp.join()
    for p in praser_list:
        p.join()
    savep.join()


if __name__=='__main__':
    spider()
