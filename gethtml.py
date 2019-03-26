import psycopg2
import config

command='''
SELECT * FROM RAWCONTENT
WHERE docid=%d;
'''
docid=957927
connect=psycopg2.connect(**config.db_conn)
cursor=connect.cursor()
cursor.execute(command%docid)
data=cursor.fetchall()
for docid,cid,categoryId,content in data:
    with open('test_html/%d.html'%docid,'w') as f:
        f.write(content)
print('done')
