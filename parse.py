import base
import psycopg2
import config
from multiprocessing import Process,Queue


def raw_content_praser(q1,q2,p_id):
    print('process %d start'%p_id)
    conn=psycopg2.connect(**config.db_conn)
    cursor=conn.cursor()
    parser=base.Parser()
    while True:
        docid=q1.get()
        if(docid is None):
            break
        cursor.execute('SELECT * FROM RAWCONTENT WHERE docid=%d'%docid)
        row=cursor.fetchall()[0]
        docid,cid,categoryId,rawcontent=row
        if(rawcontent==''):
            q2.put(docid)
            continue
        #print('docid=%d'%docid)
        data=parser.parse_raw_content(rawcontent)
        cite,word,desc,cw,jw,kw,ew,content=data
        command='''
        SELECT SAVECONTENT(%d,%d,%d,
        $DATA$%s$DATA$,$DATA$%s$DATA$,
        $DATA$%s$DATA$,$DATA$%s$DATA$,
        $DATA$%s$DATA$,$DATA$%s$DATA$,
        $DATA$%s$DATA$,$DATA$%s$DATA$,
        $DATA$%s$DATA$,$DATA$%s$DATA$,
        $DATA$%s$DATA$,$DATA$%s$DATA$,
        $DATA$%s$DATA$,$DATA$%s$DATA$,
        $DATA$%s$DATA$,$DATA$%s$DATA$
        );
        '''%(docid,cid,categoryId,word,cite,desc,cw,jw,kw,ew,
        content['att'],content['txt'],content['dic'],content['quote'],
        content['box'],content['naml'],content['directory'],content['summary'],
        content ['other'])
        cursor.execute(command)
        result=cursor.fetchall()[0][0]
        if(result):
            q2.put(docid)
        pass
    conn.commit()

def parse():
    conn=psycopg2.connect(**config.db_conn)
    cursor=conn.cursor()
    cursor.execute('SELECT docid FROM RAWCONTENT;')
    data=cursor.fetchall()
    data=list(map(lambda x:x[0],data))
    q1=Queue()
    q2=Queue()
    n=config.parse['process_num']
    p_list=[Process(target=raw_content_praser,args=(q1,q2,i)) for i in range(n)]
    for p in p_list:
        p.start()
    print('put data into q1')
    for item in data:
        q1.put(item)
    for i in range(n):
        q1.put(None)
    print('put data success')
    size=len(data)
    cap=size/1000
    count=0
    while True:
        docid=q2.get()
        count+=1
        print('parse doc %d\t\t\t(%d/%d=%f%%)'%(docid,count,size,(count*100)/size))
        if(count==size):
            break
    for p in p_list:
        p.join()
    pass

if __name__=='__main__':
    parse()
