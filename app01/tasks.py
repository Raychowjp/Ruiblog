from Ruiblog.celery import app
from tools.sms import YunTongXin
@app.task
def send_sms_c(phone,code):
    config = {
        'accountSid': '2c94811c8cd4da0a018e3ca4d07a3971',
        'accountToken': '0d91d04940684cdb947de694a04fc166',
        'appId': '2c94811c8cd4da0a018e3ca4d2133978',
        'templateId': '1'
    }
    yun = YunTongXin(**config)
    res = yun.run(phone, code)
    print(res)


