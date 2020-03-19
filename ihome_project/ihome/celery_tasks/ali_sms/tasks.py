from celery_tasks.main import celery_app
from .alisms import request_sms


# 使用装饰器装饰异步任务,保证celery识别任务
@celery_app.task(name='ali_sms')
def ali_sms(mobile, sms_code):
    mobile = str(mobile)
    sms_code = int(sms_code)
    code = "{\"code\": \"%s\"}" % sms_code
    client, request = request_sms()
    request.add_query_param('PhoneNumbers', mobile)
    request.add_query_param('TemplateParam', code)
    response = client.do_action(request)
    print(str(response, encoding='utf-8'))
