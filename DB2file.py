import pandas as pd
import os
import psycopg2
import config
from multiprocessing import Pool

process_num=15
def get_data(categoryId):
    '''
    给定categoryId，返回其特定的数据的DataFrame
    '''
    print('geting data by categoryId %d'%categoryId)
    conn=psycopg2.connect(**config.db_conn)
    cursor=conn.cursor()
    cursor.execute('SELECT * FROM CONTENT WHERE categoryId=%d;'%categoryId)
    data=cursor.fetchall()
    print('success:got data by categoryId %d'%categoryId)
    return list2table(data)

def list2table(data):
    columns=['docid','cid','categoryId','word','cite','desc',\
    'comment_chinese','comment_japan','comment_korea','comment_english',\
    'att','txt','dic','quote','box','naml','directory','summary','other']
    return pd.DataFrame(data,columns=columns)

report=pd.read_excel('report.xlsx')
categoryId_tree=pd.read_excel('categoryId_tree.xlsx')
type1_list=list(set(report['一级分类'].to_list()))
conn=psycopg2.connect(**config.db_conn)
for type1 in type1_list:
    if not os.path.exists(type1):
        os.mkdir(type1)
    temp_report=report[report['一级分类']==type1][['二级分类','categoryId']]
    print(temp_report)
    for row in temp_report.values:
        type2,categoryId=tuple(row)
        child_categoryId=categoryId_tree[categoryId_tree['father']==categoryId]['child'].to_list()
        pool=Pool(process_num)
        result=pool.map(get_data,child_categoryId)
        pool.close()
        pool.join()
        result=pd.concat(result)
        result.index=list(range(len(result)))
        result.to_excel(type1+'/'+type2+'.xlsx')
        print('success with type2:%s'%type2)
    print('done by type1:%s'%type1)
