import base
import threading
from queue import Queue

class SpiderThread(threading.Thread):
    '''
    爬取词条页面的线程类
    '''
    def __init__(self,q,tid):
        threading.Thread.__init__(self)
        self.q=q
        self.conn=base.DBConnect()
        self.praser=base.Praser()
        self.tid=tid
    def run(self):
        print('SpiderThread%d start'%self.tid)
        while True:
            docid=self.q.get()
            try:
                r=base.Web.get('https://terms.naver.com/entry.nhn?docId=%d'%docid)
            except Exception as e:
                with open('spider_log.txt','a',encoding='utf-8') as f:
                    f.write(str(e))
                continue
            cid,categoryid,content=self.praser.get_raw(r)
            result=self.conn.save_raw_content(docid,cid,categoryid,content)
            if not result:
                raise Exception('SpiderThread:save raw content fail')
            self.conn.commit()

def spider(thread_amount=88):
    connect=base.DBConnect()
    u=connect.getu()
    connect.close()
    q=Queue()
    tlist=[SpiderThread(q,i+1) for i in range(thread_amount)]
    for t in tlist:
        t.start()
    for i in u:
        q.put(i)

if __name__=='__main__':
    spider()
