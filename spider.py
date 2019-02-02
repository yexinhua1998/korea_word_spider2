from multiprocessing import Process,Queue
import base
import config

def spider(q):
    conn=base.DBConnect()
    praser=base.Praser()
    web=base.Web()

    print('spider_process_start')
    while True:
        docid=q.get()
        if docid==None:
            break
        try:
            url='https://terms.naver.com/entry.nhn?docId=%d'%docid
            #print('getting')
            r=web.get(url)
            #print('prasing')
            cid,categoryid,content=praser.get_raw(r)
            #print('saving')
            conn.save_raw_content(docid,cid,categoryid,content)
            #print('save raw content:done')
            conn.commit()
            print('save doc:%d'%docid)
        except Exception as e:
            print('error doc:%d'%docid)
            print(e)
            try:
                conn.save_raw_content(docid,0,0,'')
            except:
                pass

def main():
    process_num=config.spider['process_num']
    conn=base.DBConnect()
    q=Queue(config.doc_amount)
    u=conn.getu()
    conn.close()
    plist=[Process(target=spider,args=(q,)) for i in range(process_num)]
    for p in plist:
        p.start()
    for i in u:
        q.put(i)
    for i in range(process_num):
        q.put(None)
    for p in plist:
        p.join()

if __name__=='__main__':
    main()
