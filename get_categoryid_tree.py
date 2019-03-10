import base
import pandas as pd
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Pool
import bs4
from bs4 import BeautifulSoup

process_num=64
thread_num=16

def get_child(page):
    '''
    给定某categoryId的page，返回其子categoryId组成的列表
    arg:page(str) categoryId的词展示页面的网页源码
    return:child(list) 其子categoryId
    '''
    soup=BeautifulSoup(page,'lxml')
    subject_list=soup.find('ul',{'class':'subject_list'})
    child=[]
    if not subject_list is None:
        for content in subject_list.contents:
            if(isinstance(content,bs4.element.Tag)):
                if(content.name=='li' and content.attrs['class']==['subject_item']):
                    a=content.find('a',{'class':'title'})
                    url=(a.attrs['href'])
                    child.append(int(url.split('=')[-1]))
    return child

def dfs(categoryId):
    '''
    给定categoryId，返回其下的子categoryId
    递归地调用。当该categoryId下没有子categoryId后，再返回
    arg:categoryId(int) 当前搜索的categoryId
    return:result(list) 其子孙节点和输入的categoryId本身组成的列表
    '''
    print('get categoryId:%d'%categoryId)
    url='https://terms.naver.com/list.nhn?categoryId=%d'%categoryId
    web=base.Web()
    r=web.get(url)
    child=get_child(r.text)
    pool=ThreadPool(thread_num)
    result=pool.map(dfs,child)
    pool.close()
    pool.join()
    return [categoryId]+result

def tree2list(tree):
    '''
    给定categoryId树，将其转化成为list
    采用dfs
    arg:tree(list)list类型的树
    return:result(list) 线性表
    '''

    result=[]
    if type(tree)==list:
        for child in tree:
            if type(child)!=list:
                result.append(child)
            else:
                temp=tree2list(child)
                result+=temp
    return result

if __name__=='__main__':
    report=pd.read_excel('report.xlsx')
    categoryId_list=report['categoryId'].to_list()
    pool=Pool(process_num)
    result=pool.map(dfs,categoryId_list)
    pool.close()
    pool.join()
    data=[]
    for i in range(len(categoryId_list)):
        categoryId=categoryId_list[i]
        tree=result[i]
        dfs_list=tree2list(tree)
        data+=[(categoryId,child) for child in dfs_list]
    data=pd.DataFrame(data,columns=['father','child'])
    data.to_excel('categoryId_tree.xlsx')
