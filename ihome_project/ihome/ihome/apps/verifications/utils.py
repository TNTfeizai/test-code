# 定义任务
import json
import urllib.request
import ssl
from urllib.parse import quote
import string


# 使用装饰器装饰异步任务,保证celery识别任务
def send_auth_id(name, idCard):
    host = 'https://idcert.market.alicloudapi.com'
    path = '/idcard'
    method = 'GET'
    appcode = '504ecf9cd9d244b5a799985174114507'
    querys = 'idCard=' + idCard + '&' + 'name=' + name
    bodys = {}
    url = host + path + '?' + querys
    newurl = quote(url, safe=string.printable)
    request = urllib.request.Request(newurl)
    request.add_header('Authorization', 'APPCODE ' + appcode)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    response = urllib.request.urlopen(request, context=ctx)
    content = response.read()
    contents = content.decode('UTF-8')
    result_str = json.loads(contents)
    print(result_str)
    if result_str['status'] == '01':
        return 1
    else:
        return 0
