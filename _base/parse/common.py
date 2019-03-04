'''
解析用的公共函数
'''
import bs4

def tag2string(tag):
    '''
    将bs4.Tag对象转换成string
    arg:bs4.Tag对象
    return:string str
    '''
    if(tag.string==None):
        result=''
        for item in tag.contents:
            if(isinstance(item,bs4.element.NavigableString)):
                result+=item
            elif(isinstance(item,bs4.element.Tag)):
                result+=tag2string(item)
        return result
    else:
        return tag.string
