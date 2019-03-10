import bs4
from . import common

def have_chinese(text):
	#判断text内是否含有中文
	'''
	普通中文范围 以及 CJK 统一表意符号(CJK Unified Ideographs)
	2E80-2EFF：CJK 部首补充 (CJK Radicals Supplement)
	2F00-2FDF：康熙字典部首 (Kangxi Radicals)
	3000-303F：CJK 符号和标点 (CJK Symbols and Punctuation)
	31C0-31EF：CJK 笔画 (CJK Strokes)
	3200-32FF：封闭式 CJK 文字和月份 (Enclosed CJK Letters and Months)
	3300-33FF：CJK 兼容 (CJK Compatibility)
	3400-4DBF：CJK 统一表意符号扩展 A (CJK Unified Ideographs Extension A)
	4DC0-4DFF：易经六十四卦符号 (Yijing Hexagrams Symbols)
	4E00-9FBF：CJK 统一表意符号 (CJK Unified Ideographs)
	F900-FAFF：CJK 兼容象形文字 (CJK Compatibility Ideographs)
	FE30-FE4F：CJK 兼容形式 (CJK Compatibility Forms)
	'''
	for char in text:
		if (char>='\u4e00' and char<='\u9fbf') or \
		(char >='\u2e80' and char <='\u2fdf') or \
		(char >='\u3000' and char <='\u303f') or \
		(char >='\u31c0' and char<='\u31ef') or \
		(char >='\u3200' and char<='\u9fbf') or \
		(char >= '\uf900' and char <= '\ufaff') or \
		(char >='\ufe30' and char <='\ufe4f'):
			return True
	return False

def have_japanese(text):
	'''
	判断是否含有日语字符
	arg:text 被判断字符串
	return:is_have_japanese 是否含有日本字符 布尔值
	'''
	for char in text:
		if (char>='\u3040' and char <='\u30ff') or \
		(char>='\u3100' and char <='\u312f') or \
		(char>='\u3200' and char <='\u32ff'):#这个字符比较奇怪，会被当成日文字符
			return True
	return False

def have_korean(text):
	'''
	判断是否含有韩语字符
	arg:text 被判断字符串
	return:is_have_korean 是否含有韩语字符 布尔值
	'''
	for char in text:
		if char>='\uac00' and char <='\ud7a3':
			return True
	return False

def word2list(word):
    '''
    给定一个bs4.BeautifulSoup对象，其内容为section_wrap中的headword_title中的word
    将其解析为一个由字符串组成的列表
    arg:word被解析的对象
    return:word_list list 里面为字符串
    '''
    result=[]
    for item in word.contents:
        if(isinstance(item,bs4.element.Tag)):
            if(item.name=='a'):
                continue
            temp=common.tag2string(item)
            if(temp!=''):
                result.append(temp)
    return result

def split(word):
    '''
    给定一个bs4.BeautifulSoup对象，其内容为section_wrap中的headword_title中的word
    将其解析为不同语言的字符串，字符串内容为对应语言的word的列表
    arg:word 被解析的对象
    return:kw,jw,cw,ew 韩 日 中 英
    '''
    kw,jw,cw,ew=[],[],[],[]
    word_list=word2list(word)
    for word_string in word_list:
        if(have_japanese(word_string)):
            jw.append(word_string)
        elif(have_korean(word_string)):
            kw.append(word_string)
        elif(have_chinese(word_string)):
            cw.append(word_string)
        else:
            ew.append(word_string)
    return ','.join(cw),','.join(jw),','.join(kw),','.join(ew)
