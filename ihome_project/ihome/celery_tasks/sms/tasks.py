# 定义任务
from celery_tasks.sms.yuntongxun.ccp_sms import CCP
from . import constants
from celery_tasks.main import celery_app


# 使用装饰器装饰异步任务,保证celery识别任务
@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    """发送短信验证码的异步任务"""
    send_ret = CCP().sendTemplateSMS(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60],
                                     constants.SEND_SMS_TEMPLATE_ID)
    return send_ret






