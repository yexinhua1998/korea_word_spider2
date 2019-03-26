import base
from multiprocessing import Pool as ProcessPool
from multiprocessing.dummy import Pool as ThreadPool
import bs4
from bs4 import BeautifulSoup
import re

THREAD_NUM=10

def get_num(page):
    '''
    给定list页面的string
    返回该页面对应的词条数目
    arg:page(str)页面的html源码，字符串
    return:num(int)页面的词条数目
    '''
    soup=BeautifulSoup(page)
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
    soup=BeautifulSoup(page)
    content_list=soup.find('ul',{'class':'content_list'})
    for li in content_list.contents:
        if type(li)==bs4.element.Tag:
            title=li.find('strong',{'class':'title'})
            a=title.find('a')
            url_list.append('https://terms.naver.com'+a.attrs['href'])
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
    soup=BeautifulSoup(page)
    paginate=soup.find('div',{'id':'paginate'})
    page_id_list=[]
    for tag in paginate.contents:
        if type(tag)==bs4.element.Tag:
            if(tag.name=='a'):
                page_id_list.append(int(tag.string))
    return page_id_list

def get(url):
    global web
    return web.get(url).text

def get_docid_from_categoryId(categoryId):
    '''
    给定categoryId，返回其对应的所有docId
    '''
    global web
    web=base.Web()
    url='https://terms.naver.com/list.nhn?categoryId=%d'%categoryId
    r=web.get(url)
    r.raise_for_status()
    num=get_num(r.text)
    visited_page=[1]
    docid_list=get_docid_from_page(r.text)
    page_id_list=get_page_id(r.text)
    url=url+'&page=%d'
    while True:
        pool=ThreadPool(THREAD_NUM)
        result=pool.map(get,[url%page_id for page_id in page_id_list])
        for page_id in page_id_list:
            if not page_id in visited_page:
                visited_page.append(page_id)
        page_id_list=[]
        pool.close()
        pool.join()
        result=list(result)
        for page in result:
            _page_id_list=get_page_id(page)
            for page_id in _page_id_list:
                if (not page_id in visited_page) and (not page_id in page_id_list):
                    page_id_list.append(page_id)
            _docid_list=get_docid_from_page(page)
            if _docid_list[0] in docid_list:
                continue
            docid_list+=_docid_list
        if(page_id_list==[]):
            break
    return docid_list
