import base
from multiprocessing import Pool as ProcessPool
from multiprocessing.dummy import Pool as ThreadPool
import bs4
from bs4 import BeautifulSoup
import re
import pandas as pd
import os

THREAD_NUM=10
PROCESS_NUM=30

def get_num(page):
    '''
    给定list页面的string
    返回该页面对应的词条数目
    arg:page(str)页面的html源码，字符串
    return:num(int)页面的词条数目
    '''
    soup=BeautifulSoup(page,'lxml')
    path_area=soup.find('div',{'class':'path_area'})
    count=path_area.find('em',{'class':'count'})
    string=count.string[:-1].replace(',','')
    return int(string)

def get_url_list(page):
    '''
    给定一个list页面
    返回该页面对应的所有词条的url
    arg:page(str)页面的html源码
    return:url_list(list(str))所有词条的url
    '''
    url_list=[]
    soup=BeautifulSoup(page,'lxml')
    content_list=soup.find('div',{'id':'content'})
    a_list=content_list('a')
    for a in a_list:
        if type(a)==bs4.element.Tag:
            if 'href' in a.attrs.keys():
                url=a.attrs['href']
                if url[:6]=='/entry':
                    url_list.append('https://terms.naver.com'+url)
    return url_list

def get_docid_from_page(page):
    '''
    给定一个列表网页的html源码
    返回其下面的所有docid
    arg:page(str) 列表网页的html源码
    return:docid_list(list(int))网页下对应的docid的列表
    '''
    pattern=re.compile(r'\d+')
    result=[]
    url_list=get_url_list(page)
    for url in url_list:
        result.append(int(pattern.search(url).group(0)))
    return result

def get_page_id(page):
    '''
    给定一个page的html源码
    返回其下面有的pageid
    '''
    soup=BeautifulSoup(page,'lxml')
    paginate=soup.find('div',{'id':'paginate'})
    if paginate is None:
        return []
    page_id_list=[]
    for tag in paginate.contents:
        if type(tag)==bs4.element.Tag:
            if(tag.name=='a'):
                page_id_list.append(int(tag.string))
    return page_id_list

def get(arg):
    web,url=arg
    return web.get(url).text

def get_docid_from_list(arg):
    '''
    给定list页面的url,获取url对应的所有docid
    arg:url(str)
    return:docid_list(list(int))
    '''
    url,num=arg
    web=base.Web()
    if num==-1:
        r=web.get(url)
        num=get_num(r.text)
    page_amount=num/15
    if page_amount!=int(page_amount):
        page_amount=int(page_amount)+1
    else:
        page_amount=int(page_amount)
    pool=ThreadPool(THREAD_NUM)
    result=pool.map(get,[(web,url+('&page=%d'%(i+1))) for i in range(page_amount)])
    pool.close()
    pool.join()
    docid_list=[docid for page in result for docid in get_docid_from_page(page)]
    return docid_list

def get_index_url_list(page):
    '''
    给定一个list页面的head_page(html源码,str)
    返回其按照字母索引的所有url组成的列表
    '''
    url_list=[]
    soup=BeautifulSoup(page,'lxml')
    content=soup.find('div',{'id':'content'})
    order_item_list=content('li',{'class':'order_item'})
    for order_item in order_item_list:
        if type(order_item)==bs4.element.Tag:
            if not 'selected' in order_item.attrs['class']:
                a=order_item.find('a')
                url_list.append('https://terms.naver.com'+a.attrs['href'])
    return url_list

def get_docid_from_categoryId(categoryId):
    '''
    给定categoryId，返回其对应的所有docId
    '''
    web=base.Web()
    url='https://terms.naver.com/list.nhn?categoryId=%d'%categoryId
    r=web.get(url)
    head_page=r.text
    num=get_num(head_page)
    print('num=%d'%num)
    if num<=20000:
        print('method1:')
        _result=get_docid_from_list((url,num))
    else:
        print('method2:')
        url='https://terms.naver.com/list.nhn?categoryId=%d&so=st3.asc'%categoryId
        r=web.get(url)
        head_page=r.text
        index_url_list=get_index_url_list(head_page)
        result=map(get_docid_from_list,[(url,-1) for url in index_url_list])
        result=list(result)
        _result=[docid for docid_list in result for docid in docid_list]
    return list(set(_result))

def save_docid_with_categoryid(arg):
    '''
    给定父类以及类的categoryid
    以(father,docid)的形式
    保存categoryid对应的所有docid到数据库
    arg:
        father(int):categoryid的父类别的categoryid
        categoryid(int):categoryid
    return:
        None
    '''
    father,categoryid,counter=arg
    path='./category_doc/%d.txt'%categoryid
    print('geting docid.categoryid=%d'%categoryid)
    if os.path.exists(path):
        print('get category %d from file'%categoryid)
        with open(path,'r') as f:
            docid_list=f.read()
        docid_list=eval(docid_list)
    else:
        print('get category %d from web'%categoryid)
        docid_list=get_docid_from_categoryId(categoryid)
        with open(path,'w') as f:
            f.write(str(docid_list))
    print('get docid success.categoryid=%d'%categoryid)
    conn=base.DBConnect()
    for docid in docid_list:
        conn.save_category_doc(father,docid)
    conn.commit()
    conn.close()
    print('save success.categoryid=%d'%categoryid)
    counter[0]+=1
    print('categoryid=%d done:\t%.2f'%(categoryid,(counter[0]/float(counter[-1]))))
    return None


def get_category_doc(tree):
    '''
    给定以[(father1,categoryid1),(father2,categoryid2)......(father_n,categoryid_n)]
    构成的树,其中father_i为categoryid_i的父类的categoryid。
    爬取所有对应的docid，并保存到数据
    arg:
        tree(list(tuple))，类别树
    return:
        None
    '''
    counter=base.manager.list([0,0])
    counter[-1]=len(tree)
    pool=ProcessPool(PROCESS_NUM)
    pool.map(save_docid_with_categoryid,[row+(counter,) for row in tree])
    pool.close()
    pool.join()
    print('all done.')

if __name__=='__main__':
    path='categoryId_tree.xlsx'
    data=pd.read_excel(path)
    use_cols=['father','child']
    data=data[use_cols]
    tree=[tuple(row) for row in data.values]
    get_category_doc(tree)
