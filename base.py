'''
底层操作
'''

import requests
import config

class web:
    @staticmethod
    def get(url,**kvargs):
        arg=config.requests_arg
        arg.update(kvargs)
        timeout=arg['timeout']
        max_retry=arg['max_retry']

        retry=0
        while retry<max_retry:
            try:
                r=requests.get(url,timeout=timeout)
                r.raise_for_status()
                return r.text
            except requests.exceptions.Timeout:
                print('web.get:timeout retry:\n%s'%url)
                retry+=1
            except Exception as e:
                raise e
        raise Exception('web.get:retry times larger than max_retry')
