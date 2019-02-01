import base
import threading
from queue import Queue as TQ
from multiprocessing import Queue as PQ
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
                print('get doc %d success'%docid)
            except Exception as e:
                #with open('spider_log.txt','a',encoding='utf-8') as f:
                #    f.write(str(e))
                print('error:url=%s'%url)
                r=None
            self.q_out.put((docid,r))
        pass

def crawl(list_out,lock,signal,thread_amount=64):
    '''
    爬取函数
    '''
    connect=base.DBConnect()
    u=connect.getu()
    connect.close()
    q_in=TQ()
    q_out=TQ()
    tlist=[SpiderThread(q_in,q_out,i+1) for i in range(thread_amount)]
    for t in tlist:
        t.start()
    for i in u:
        q_in.put(i)

    while True:
        data=q_out.get()
        lock.acquire()
        list_out.append(data)
        signal.release()
        lock.release()
        print('transfer doc %d to praser'%data[0])

    for t in tlist:
        t.join()
    pass

def prase_responese(list_in,list_out,lock_in,lock_out,s_in,s_out):
    praser=base.Praser()
    while True:
        s_in.acquire()
        lock_in.acquire()
        docid,r=list_in.pop(0)
        lock_in.release()

        if r==None:
            cid,categoryid,content=0,0,''
        else:
            cid,categoryid,content=praser.get_raw(r)

        lock_out.acquire()
        list_out.append((docid,cid,categoryid,content))
        s_out.release()
        lock_out.release()
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

def save_content(list_in,lock,signal,thread_amount=64):
    '''
    将爬取到的页面保存到数据库
    '''
    q_in=TQ()
    tlist=[ContentSaver(q_in,i+1) for i in range(thread_amount)]
    for t in tlist:
        t.start()

    while True:
        signal.acquire()
        lock.acquire()
        data=list_in.pop(0)
        lock.release()
        q_in.put(data)
    for t in tlist:
        t.join()
    pass

def spider(**kvargs):
    arg=config.spider_arg
    arg.update(kvargs)

    manager=Manager()
    crawl2prase=manager.list()
    prase2save=manager.list()
    #列表取出和放入的互斥信号量
    lock1=Lock()
    lock2=Lock()
    #指示列表内容数量的信号量
    s1=Semaphore(0)
    s2=Semaphore(0)

    crawlp=Process(target=crawl,args=(crawl2prase,lock1,s1,arg['crawler_thread_amount']))
    crawlp.start()

    praser_list=[Process(target=prase_responese,
    args=(crawl2prase,prase2save,lock1,lock2,s1,s2))
    for i in range(arg['praser_amount'])]
    for p in praser_list:
        p.start()

    savep=Process(target=save_content,
    args=(prase2save,lock2,s2,arg['saver_thread_amount']))
    savep.start()

    crawlp.join()
    for p in praser_list:
        p.join()
    savep.join()


if __name__=='__main__':
    spider()
