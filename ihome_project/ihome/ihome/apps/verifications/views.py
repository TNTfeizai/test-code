import random, json, re
from django import http
from django.views import View
from django_redis import get_redis_connection
from django.conf import settings


from celery_tasks.sms.tasks import send_sms_code
from ihome.libs.captcha.captcha import captcha

# Create your views here.

# 创建日志输出器


logger = settings.LOGGER


class ImageCodeView(View):
    """图形验证码"""

    def get(self, request):
        """

        :param request: 请求对象
        :param cur: 唯一标识图形验证码所属于的用户
        :return: image/jpg
        """
        # 实现主体逻辑，生成图片验证码，保存图片验证码，返回响应图片验证码
        # 获取标识符
        cur = request.GET.get('cur')
        # 1. 生成图片验证码
        text, image = captcha.generate_captcha()
        # 2.保存图片验证码15663122006
        redis_conn = get_redis_connection("image_code")
        # redis_conn.setex("key", "expires", "value")
        redis_conn.setex("image_%s" % cur, 300, text)

        # 响应图片验证码
        return http.HttpResponse(image, content_type="image/jpg")


class SMSCodeView(View):
    """短信验证码"""

    def post(self, request):
        """
        :param request: 请求对象
        :param mobile: 手机号
        :return: JSON
        """
        # 接受参数
        json_dict = json.loads(request.body.decode())
        mobile = json_dict.get('mobile')
        image_code_client = json_dict.get('text')
        cur = json_dict.get('id')

        # 校验参数
        if not all([image_code_client, cur]):
            return http.JsonResponse({'code': 4002, 'errmsg': '缺少必传参数'})
            # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({'errno': 4103, 'errmsg': '请输入正确的手机号'})
        # 创建连接到redis的对象
        redis_conn = get_redis_connection("image_code")

        # 发送短信之前判断用户是否频繁发送短信 取出标记
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return http.JsonResponse({'code': 4103, 'errmsg': '发送短信过于频繁'})
        # 提取图形验证码
        image_code_server = redis_conn.get('image_%s' % cur)
        if image_code_server is None:
            # 图形验证码不存在或过期
            return http.JsonResponse({'code': 4002, 'errmsg': '图形验证码失效'})
        # 删除图形验证码，避免恶意测试图形验证码
        redis_conn.delete('image_%s' % cur)
        # 对比图形验证码
        image_code_server = image_code_server.decode()  # bytes转字符串
        if image_code_client.lower() != image_code_server.lower():  # 转小写之后比较
            return http.JsonResponse({'code': 4103, 'errmsg': '输入图形验证码有误'})

        # 生成短信验证码.生成6位数的验证码
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)  # 手动输出日志记录短信验证码

        # 创建redis管道
        redis_conn = get_redis_connection("sms_code")
        pl = redis_conn.pipeline()
        # 300为有效期
        pl.setex('sms_%s' % mobile, 300, sms_code)
        # 60s内是否重复发送的标记
        pl.setex('send_flag_%s' % mobile, 60, 1)
        # 执行
        pl.execute()

        # 使用celery发送短信验证码
        send_sms_code.delay(mobile, sms_code)
        # 响应结果
        return http.JsonResponse({'errno': 0, 'errmsg': '发送短信成功'})
