import pandas as pd

def get_label2_and_amount(string):
    try:
        _label2=string.split('-')[1]
    except:
        _label2=string
    result=_label2.split('（')
    print(result)
    label2,num=result[0],result[1]
    num=num.strip('个）')
    return label2,num

def get_categoryId(url):
    url=url.split('&')[1]
    categoryId=url.split('=')[1]
    return int(categoryId)

data_out=pd.DataFrame(columns=['一级分类','二级分类','官方数量','获得数量','categoryId'])

count=0
path='classfication.xlsx'
data_in=pd.read_excel(path)
label1set=list(set(data_in['一级分类'].to_list()))
for label1 in label1set:
    label2list=data_in[data_in['一级分类']==label1]['二级分类'].to_list()
    print(label2list)
    for i in range(int(len(label2list)/2)):
        label2=label2list[2*i]
        url=label2list[2*i+1]
        print(label2)
        print(url)
        label2,num=get_label2_and_amount(label2)
        categoryId=get_categoryId(url)
        s=pd.Series({
            '一级分类':label1,
            '二级分类':label2,
            '官方数量':num,
            '获得数量':-1,
            'categoryId':categoryId
        })
        s.name=count
        count+=1
        data_out=data_out.append(s)

print(data_out)
data_out.to_excel('report.xlsx')
