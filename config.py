db_conn={
    'host':'127.0.0.1',
    'database':'korea_word',
    'user':'postgres',
    'password':'Ye25554160'
}

doc_amount=5735142

#default args of requests.get
requests_arg={
    'max_retry':10,
    'timeout':10
}

content_saver_arg={
    'commit_amount':100
}

spider_arg={
    'crawler_p_amount':4,
    'crawler_thread_amount':64,
    'praser_amount':4,
    'saver_thread_amount':20
}
