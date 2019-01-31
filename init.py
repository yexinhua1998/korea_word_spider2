import psycopg2
import config

if __name__=='__main__':
    connect=psycopg2.connect(**config.db_conn)
    cursor=connect.cursor()
    print('connect success!')

    with open('create_table.sql','r',encoding='utf-8') as f:
        cursor.execute(f.read())
    print('create table success')

    with open('create_index.sql','r',encoding='utf-8') as f:
        cursor.execute(f.read())
    print('create index success')

    with open('create_function.sql','r',encoding='utf-8') as f:
        cursor.execute(f.read())
    print('create function success')

    cursor.execute('SELECT initunget(%d);'%(config.doc_amount))
    print('Initialize unget success')

    connect.commit()
