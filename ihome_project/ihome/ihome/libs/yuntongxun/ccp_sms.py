# -*- coding:utf-8 -*-

# import ssl
# ssl._create_default_https_context =ssl._create_stdlib_context # 解决Mac开发环境下，网络错误的问题

from .CCPRestSDK import REST
import ssl

# 说明：主账号，登陆云通讯网站后，可在"控制台-应用"中看到开发者主账号ACCOUNT SID
_accountSid = '8aaf07086d05d00c016d39fcf3411d5f'

# 说明：主账号Token，登陆云通讯网站后，可在控制台-应用中看到开发者主账号AUTH TOKEN
_accountToken = '3390ee39f38244e6ae5d329256a61eeb'

# 请使用管理控制台首页的APPID或自己创建应用的APPID
_appId = '8aaf07086d05d00c016d3d4dac121f51'

# 说明：请求地址，生产环境配置成app.cloopen.com

ssl._create_default_https_context = ssl._create_unverified_context
_serverIP = 'https://app.cloopen.com'

# 说明：请求端口 ，生产环境为8883
_serverPort = "8883"

# 说明：REST API版本号保持不变
_softVersion = '2013-12-26'

# 云通讯官方提供的发送短信代码实例
# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# @param $tempId 模板Id
# def sendTemplateSMS(to, datas, tempId):
#     # 初始化REST SDK
#     rest = REST(_serverIP, _serverPort, _softVersion)
#     rest.setAccount(_accountSid, _accountToken)
#     rest.setAppId(_appId)
#
#     result = rest.sendTemplateSMS(to, datas, tempId)
#     print(result)


class CCP(object):
    """发送短信验证码的单例类"""

    def __new__(cls, *args, **kwargs):
        """
        定义单例的初始化方法
        :return: 单例
        """
        # 判断单例是否存在:_instance属性中存储的就是单例
        if not hasattr(cls, '_instance'):
            cls._instance = super(CCP, cls).__new__(cls)
            cls._instance.rest = REST(_serverIP, _serverPort, _softVersion)
            cls._instance.rest.setAccount(_accountSid, _accountToken)
            cls._instance.rest.setAppId(_appId)

        return cls._instance

    def sendTemplateSMS(self, to, datas, tempId):
        result = self.rest.sendTemplateSMS(to, datas, tempId)
        print(result)
        if result.get('statusCode') == '000000':
            return 0
        else:
            return -1


if __name__ == '__main__':
    # 注意： 测试的短信模板编号为1
    # sendTemplateSMS('17600992168', ['123456', 5], 1)

    # 单例类发送短信验证码
    CCP().sendTemplateSMS('17600992168', ['123456', 5], 1)
