# !/usr/bin/env python
# coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from .contents import accessKeyId, accessSecret, cn_hangzhou


def request_sms():
    # client = AcsClient('<accessKeyId>', '<accessSecret>', 'cn-hangzhou')
    client = AcsClient(accessKeyId, accessSecret, cn_hangzhou)

    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https')  # https | http
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')

    request.add_query_param('RegionId', "cn-hangzhou")
    # return request
    # request.add_query_param('PhoneNumbers', "17786495723")
    request.add_query_param('SignName', "ihome")
    request.add_query_param('TemplateCode', "SMS_176936142")
    return client, request
    # request.add_query_param('TemplateParam', "{\"code\": \"225445\"}")

    # response = client.do_action(request)

    # python2:  print(response)
    # print(str(response, encoding='utf-8'))
