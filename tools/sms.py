import base64
import datetime
import hashlib
import json

import requests
class YunTongXin():

    base_url = 'https://app.cloopen.com:8883'

    def __init__(self, accountSid, accountToken, appId, templateId):
        self.accountSid = accountSid #账户ID
        self.accountToken = accountToken #授权令牌
        self.appId = appId
        self.templateId = templateId

    def get_request_url(self, sig):
        #/2013-12-26/Accounts/{accountSid}/SMS/{funcdes}?sig={SigParameter}
        self.url = self.base_url + '/2013-12-26/Accounts/%s/SMS/TemplateSMS?sig=%s'%(self.accountSid, sig)
        return self.url

    def get_timestamp(self):
        #时间戳
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S')#一大带两小

    def get_sig(self, timestamp):
        #生成业务url中的sig,sig包括几个部分：accountSid+token+时间戳
        s = self.accountSid+self.accountToken+timestamp
        m = hashlib.md5()
        m.update(s.encode())
        return m.hexdigest().upper()#大写

    def get_request_header(self, timestamp):
        #生成请求头Authorization
        s = self.accountSid +':' +timestamp
        auth = base64.b64encode(s.encode()).decode()
        return {'Accept': 'application/json', 'Content-Type':'application/json;charset=utf-8',
                'Authorization': auth}


    def get_request_body(self, phone, code):
        return {
            'to': phone,
            'appId': self.appId,
            'templateId': self.templateId,
            'datas': [code,'3']
        }

    def request_api(self, url, header, body):
        res = requests.post(url, headers=header, data=body) #requests，直接给这个URL发出json请求
        return res.text #拿到容联云的反馈，失败还是成功，拿到这个response



    def run(self, phone, code):
        timestamp = self.get_timestamp()
        sig = self.get_sig(timestamp)
        url = self.get_request_url(sig) #生成了业务url
        header = self.get_request_header(timestamp)
        body = self.get_request_body(phone, code)
        data = self.request_api(url, header, json.dumps(body))
        return data

# if __name__ == '__main__':
#     config = {
#         'accountSid': '2c94811c8cd4da0a018e3ca4d07a3971',
#         'accountToken': '0d91d04940684cdb947de694a04fc166',
#         'appId': '2c94811c8cd4da0a018e3ca4d2133978',
#         'templateId': '1'
#     }
#     yun = YunTongXin(**config)
#     res = yun.run('18994618087','8812')
#     print(res)
