import bs4
from bs4 import BeautifulSoup

def get_ele_string(ele,is_except_a=False):
	'''
	递归地获取html元素中的文字
	arg:ele html元素
	arg:is_except_a 是否忽略a元素 如果是则不管a元素
	'''
	string=''
	if ele is None:
		return string
	for item in ele.contents:
		if isinstance(item,bs4.element.Comment):
			continue
		if isinstance(item,bs4.element.NavigableString):
			if string=='\n':
				continue
			string+=item
		elif isinstance(item,bs4.element.Tag):
			if item.name=='script':
				continue
			if is_except_a and item.name=='a':
				continue
			string+=get_ele_string(item)
	return string.replace('\n',' ').replace('\t',' ')


def get_att(element):
	'''
	从html元素 element中获取att信息
	arg:element bs4.element.Tag对象 att信息对应的element
	return att 字典类型
	'''
	att={}
	tbody=element.find('tbody')
	if tbody is None :
		return att
	for tr in tbody.contents:
		if not isinstance(tr,bs4.element.Tag):
			continue
		th=tr.find('th')
		key=get_ele_string(th)

		td=tr.find('td')
		value=get_ele_string(td)

		att[key]=value
	return att




def get_subinfo(dd,dic):
	'''
	从对应的dd元素中，获取subinfo，并写入到dic内
	arg:dd bs4.element.Tag 对应的html元素
	return: None
	'''
	for item in dd.contents:
		if item=='\n':
			continue
		if isinstance(item,bs4.element.Tag):
			if not 'class' in item.attrs.keys():
				value=item.string
			elif item.attrs['class'][0]=='label' and item.name=='em':
				key=item.string
		else:
			value=item
	dic[key]=value
	pass

def get_word_and_cite(dt,dic):
	'''
	从对应的dt元素中，获取word和cite，并写入到dic中
	arg:dt bs4.element.Tag 对应的html元素
	return None
	'''
	for item in dt.contents:
		if isinstance(item,bs4.element.Tag):
			if item.name=='strong' and item.attrs['class'][0]=='word':
				dic['word']=item.string
			elif item.name=='span' and item.attrs['class'][0]=='cite':
				dic['cite']=item.string
	pass


def get_dic(element):
	'''
	从html元素中 获取dic信息
	arg:element bs4.element.Tag dic信息对应的element
	return dic 字典类型
	'''
	dic={}

	dl=element.find('dl')
	for item in dl.contents:
		if item=='\n':
			continue
		if not isinstance(item,bs4.element.Tag):
			continue
		if item.name=='dt':
			get_word_and_cite(item,dic)
		elif 'class' in item.attrs.keys():
			if item.name=='dd' and item.attrs['class'][0]=='sub_info':
				get_subinfo(item,dic)
		else:
			#获取主内容
			dic['main']=get_ele_string(item)
	return dic



def data_out(data):
	'''
	将data列表转化成输出的string
	arg: data data列表
	return: result 输出的字符串
	'''
	result=''
	for dic in data:
		for key,value in dic.items():
			result+='%s::%s,,'%(key,value)
		result=result[:-2]#把最后的逗号去掉
		result+=';;'
	return result

def get_comment(soup):
	'''
	从词条页面中，取出注释，并进行分割
	arg:soup bs4中BeautifulSoup对象，整个网页
	return:word 词条名
	return:comment 注释字符串
	'''
	headword_title=soup.find('div',{'class':'headword_title'})
	headword=headword_title.find('h2',{'class':'headword'})
	cite=headword_title.find('p',{'class':'cite'})
	dest=headword_title.find('p',{'class':'desc'})
	cite=get_ele_string(cite)
	dest=get_ele_string(dest)
	word=get_ele_string(headword)
	comment_ele=headword_title.find('p',{'class':'word'})
	comment=get_ele_string(comment_ele,is_except_a=True)#此处由于有语音的a元素，故需要排除
	return word.strip('\t \n'),cite.strip('\t \n'),dest.strip('\t \n'),comment.strip('\t \n')

def dict2content(dic):
	'''
	将某个字典转换成可以装入main的形式
	即key1\tvalue1\nkey2\tvalue2\n的形式
	arg:dic 转换的源字典
	return:text 转换后的字符串
	'''
	text=''
	for key,value in dic.items():
		text+=key+'\t'+value+'\n'
	return text

def get_content(size_ct):
	'''
	给定一个bs4.BeautifulSoup对象html元素 size_ct
	获取词条的主要内容，并以字典形式返回
	arg:size_ct bs4.BeautifulSoup对象 对应于页面中的size_ct html元素
	return:main 字典类型 key为对应的字段，value为对应的字符串
	'''
	main={}
	key_list=['att','txt','dic','quote','box','naml','directory','summary','other']
	for key in key_list:
		main[key]=''
	raw_main=main.copy()

	if size_ct is None:
		return main

	for item in size_ct.contents:
		#把无效的子元素去除掉
		if not isinstance(item,bs4.element.Tag):
			continue
		elif item.name=='script' or item.name=='h3':
			#script为js代码，h3为小标题
			continue

		try:
			if 'class' in item.attrs.keys():
				if item.name=='div' and item.attrs['class'][0]=='att_type':
					#为att类型
					main['att']+=dict2content(get_att(item))
				elif item.name=='p' and item.attrs['class'][0]=='txt':
					#txt类型
					txt=get_ele_string(item)
					###here###
					if item.previous_sibling.previous_sibling.name=='h3':
						#将小标题加入到content里面
						main['txt']+=get_ele_string(item.previous_sibling.previous_sibling)+'\t'
					###here###
					main['txt']+=txt+'\n'
				elif item.name=='div' and item.attrs['class'][0]=='terms_dic_area':
					#dic类型
					dic=get_dic(item)
					main['dic']+=dict2content(dic)
				elif item.name=='div' and item.attrs['class'][0]=='na_block_quote':
					#quote类型
					main['quote']+=get_ele_string(item)+'\n'
				elif item.name=='div' and item.attrs['class'][0]=='box_content':
					#box类型
					main['box']+=get_ele_string(item)+'\n'
				elif item.name=='div' and item.attrs['class'][0]=='naml_area':
					#naml类型
					main['naml']+=get_ele_string(item)+'\n'
				elif item.name=='div' and item.attrs['class'][0]=='tmp_agenda' and item.attrs['class'][1]=='newline':
					#directory类型
					main['directory']+=get_ele_string(item)+'\n'
				elif item.name=='dl' and item.attrs['class'][0]=='summary_area':
					#summary类型
					main['summary']+=get_ele_string(item)+'\n'
			else:
				#遇到未遇见过的类型，放入other字段
				txt=get_ele_string(item)
				if txt!='':
					#当文字为空时，一般为存放图片的标签
					main['other']+=txt+'\n'
		except Exception as e:
			#不明原因错误，则抛出错误，同时直接给other字段
			print('get_word_main_content error')
			print(e)
			txt=get_ele_string(item)
			if txt!='':
				#当文字为空时，一般为存放图片的标签
				main['other']+=txt+'\n'

	if main==raw_main:
		#有时候会有旧版本的网页，会出现无法解析的情况，此时main和原来的main的值是一样的
		main['txt']+=get_ele_string(size_ct)+'\n'

	return main
