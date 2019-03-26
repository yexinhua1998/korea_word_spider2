import pandas as pd
from multiprocessing import Pool

def get_len(row):
    type1,type2,right_amount,catched_amount,categoryId=tuple(row)
    data=pd.read_excel(type1+'/'+type2+'.xlsx')
    return len(data)

raw_report=pd.read_excel('report.xlsx')
del raw_report[raw_report.columns[0]]
new_report=raw_report.copy()
pool=Pool(20)
result=pool.map(get_len,raw_report.values)
new_report['获得数量']=pd.Series(result,index=new_report.index)
new_report['完成率']=(new_report['获得数量']/new_report['官方数量'])*100
new_report.to_excel('new_report.xlsx')
