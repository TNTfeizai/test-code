
import json, re, random

from django.contrib.auth import login, authenticate, logout
from django.views import View
from django import http
from django_redis import get_redis_connection
from fdfs_client.client import Fdfs_client

from pymysql import DatabaseError

from homes.models import House

import json, re
from django import http
from django.conf import settings


from celery_tasks.sms.constants import IMAGE_CODE_REDIS_EXPIRES
from celery_tasks.ali_sms.tasks import ali_sms
from homes.models import House
from fdfs_client.client import Fdfs_client
from pymysql import DatabaseError

from ihome.utils.complete_url import Url
from ihome.utils.response_code import RETCODE
from ihome.utils.views import LoginRequiredJSONMixin

from users.contents import check_password_number, redis_password_expires, not_show_number


import json

from verifications.utils import send_auth_id


# Create your views here.
from django import http
from django.views import View

from . models import User

logger = settings.LOGGER

# Create your views here.


class ResetPasswordView(View):
    """重置密码"""

    def post(self, request):
        json_dict = json.loads(request.body.decode())
        mobile = json_dict.get('mobile')
        password = json_dict.get('password')
        sms_code_client = json_dict.get('phonecode')

        # 判断参数是否齐全
        if not all([mobile, password, sms_code_client]):
            return http.JsonResponse({'errno': 4103	, 'errmsg': '缺少必传参数'})
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({'errno': 4103, 'errmsg': '请输入正确的手机号'})
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.JsonResponse({'errno': 4103, 'errmsg': '请输入8-20位密码'})

        # 判断短信验证码是否输入正确
        redis_conn = get_redis_connection('sms_code')
        # 取出保存在redis中的短信验证码
        sms_code_server = redis_conn.get('retrieve_sms_%s' % mobile)
        # 取不到就表示失效了
        if sms_code_server is None:
            return http.JsonResponse({'errno':4002, 'errmsg': '短信验证码失效'})
        # 取出的数据要进行解码,bytes转字符串
        if sms_code_client != sms_code_server.decode():
            return http.JsonResponse({'errno':4002,'errmsg': '输入验证码有误'})
        # 校验完成保存数据
        try:
            # user = User.objects.create_user(username=mobile, password=password, mobile=mobile)
            user = User.objects.filter(mobile=mobile).first()

            user.set_password(password)
            user.save()
        except DatabaseError:
            return http.JsonResponse({'errno': 4001, 'errmsg': '重置密码失败'})
        #
        # # 登入用户，　实现状态保持
        # login(request, user)
        # 响应注册结果
        return http.JsonResponse({'errno': 0, 'errmsg': '重置密码成功'})


class RetrievePasswordView(View):
    """找回密码----发送短信验证码"""

    def post(self, request):
        """发送短信验证码"""
        json_dict = json.loads(request.body.decode())
        mobile = json_dict.get('mobile')
        # 创建连接到redis的对象
        redis_conn = get_redis_connection("image_code")
        # 发送短信之前判断用户是否频繁发送短信 取出标记
        retrieve_send_flag = redis_conn.get('retrieve_send_flag_%s' % mobile)
        if retrieve_send_flag:
            return http.JsonResponse({'errno': 4103, 'errmsg': '发送短信过于频繁'})
        sms_code = '%06d' % random.randint(0, 999999)

        logger.info(sms_code)  # 手动输出日志记录短信验证码

        # 创建redis管道
        redis_conn = get_redis_connection("sms_code")
        pl = redis_conn.pipeline()
        # 300为有效期
        pl.setex('retrieve_sms_%s' % mobile, 300, sms_code)
        # 60s内是否重复发送的标记
        pl.setex('retrieve_send_flag_%s' % mobile, 60, 1)
        # 执行
        pl.execute()
        # 使用celery发送短信验证码
        ali_sms.delay(mobile, sms_code)
        # 响应结果
        return http.JsonResponse({'errno': 0, 'errmsg': '发送短信成功'})


class RegisterView(View):
    """用户注册"""

    def post(self, request):
        """
        实现用户注册
        :param request:注册对象
        :return: 注册结果
        """
        # 接受参数
        json_dict = json.loads(request.body.decode())
        mobile = json_dict.get('mobile')
        password = json_dict.get('password')
        sms_code_client = json_dict.get('phonecode')
        # 判断参数是否齐全
        if not all([mobile, password, sms_code_client]):
            return http.JsonResponse({'errno': 4002, 'errmsg': '缺少必传参数'})
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({'errno': 4103, 'errmsg': '请输入正确的手机号'})
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.JsonResponse({'errno': 4002, 'errmsg': '请输入8-20位密码'})
        # 判断短信验证码是否输入正确
        redis_conn = get_redis_connection('sms_code')
        # 取出保存在redis中的短信验证码
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        # 取不到就表示失效了
        if sms_code_server is None:
            return http.JsonResponse({'errmsg': '短信验证码失效'})
        # 取出的数据要进行解码,bytes转字符串
        if sms_code_client != sms_code_server.decode():
            return http.JsonResponse({'errmsg': '输入验证码有误'})
        # 校验完成保存数据
        try:
            user = User.objects.create_user(username=mobile, password=password, mobile=mobile)
        except DatabaseError:
            return http.JsonResponse({'errmsg': '注册失败'})

        # 登入用户，　实现状态保持
        login(request, user)
        # 响应注册结果
        return http.JsonResponse({'errno': 0, 'errmsg': '注册成功'})


class LoginView(View):

    def get(self, request):
        """判断是否登录"""
        user = request.user
        if not user.is_authenticated:
            return http.JsonResponse({'errno': 4101, 'errmsg': '未登录'})
        return http.JsonResponse(
            {'errno': "0", 'errmsg': '已登录', 'data': {'name': request.user.username, 'user_id': request.user.id}})

    def post(self, request):

        # 接受参数
        json_dict = json.loads(request.body.decode())
        mobile = json_dict.get('mobile')
        password = json_dict.get('password')

        # 判断参数是否齐全
        if not all([mobile, password]):
            return http.JsonResponse({'errno': 4002, 'errmsg': '缺少必传参数'})
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({'errno': 4103, 'errmsg': '请输入正确的手机号'})
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.JsonResponse({'errno': 4002, 'errmsg': '请输入8-20位密码'})

        # 解决用户名登录问题
        user = User.objects.filter(mobile=mobile).first()
        if not user:
            return http.JsonResponse({'errno': 4103, 'errmsg': '用户名或密码错误'})

        # 创建链接对象
        redis_conn = get_redis_connection("image_code")
        # 当前用户在阶段尝试密码次数
        check_flag = redis_conn.get("check_flag_%s" % mobile)
        if not check_flag:
            redis_conn.setex("check_flag_%s" % mobile, redis_password_expires, 1)
        time_remaining = redis_conn.ttl("check_flag_%s" % mobile)
        time_minute = time_remaining // 60
        time_second = time_remaining % 60
        if check_flag:
            check_flag = int(check_flag.decode())
            # 如果尝试次数大于我规定的次数, 返回响应
            if check_flag >= check_password_number:
                # 获取当前阶段剩余时间 错误周期
                return http.JsonResponse({'errno': 4101, 'errmsg': '尝试次数过多, 请于%s分%s秒后再试' % (
                    time_minute, time_second)})
            # 如果尝试次数小于于我规定的次数, 用户尝试增加1次
            redis_conn.incrby("check_flag_%s" % mobile, 1)
        # 判断密码是否正确
        flag = user.check_password(password)
        # 若密码错误
        if not flag:
            if check_flag:
                # 如果尝试次数大于规定的次数, 则显示倒计时
                if check_flag > not_show_number:
                    return http.JsonResponse({'errno': 4103, 'errmsg': '用户名或密码错误, %s分%s秒内你还剩%s次机会' % (
                        time_minute, time_second, check_password_number - check_flag)})
                else:
                    return http.JsonResponse({'errno': 4103, 'errmsg': '用户名或密码错误'})
            else:
                return http.JsonResponse({'errno': 4103, 'errmsg': '用户名或密码错误'})

        login(request, user)
        return http.JsonResponse({'errno': 0, 'errmsg': '登录成功'})

    def delete(self, request):
        user = request.user
        if not user.is_authenticated:
            return http.JsonResponse({'errno': 4101, 'errmsg': '未登录'})
        logout(request)
        return http.JsonResponse({'errno': 0, 'errmsg': '已登出'})


class IndexView(View):
    """首页推荐"""

    def get(self, request):
        # 查询所有的房屋首页图片
        home_images = House.objects.order_by('-id')
        # 定义容器
        data = []
        for home_image in home_images:
            # 查询出房屋首页图片并排序
            info = {
                "house_id": home_image.id,
                "img_url": Url(home_image.index_image_url),
                "title": home_image.title
            }
            data.append(info)

        # 返回响应
        return http.JsonResponse({
            "data": data,
            "errmsg": "OK",
            "errno": "0"
        })


class ChangeUsernameView(LoginRequiredJSONMixin, View):
    def put(self, request):
        # 接收参数
        json_str = request.body.decode()
        data = json.loads(json_str)
        username = data.get('name')
        # 校验参数
        if not all([username]):
            return http.JsonResponse({"errno": RETCODE.NECESSARYPARAMERR, "errmsg": "缺少参数"})
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.JsonResponse({"errno": RETCODE.USERERR, "errmsg": "用户名格式不正确"})
        # 修改数据库用户名数据
        try:
            user = User.objects.get(id=request.user.id)
            user.username = username
            user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({"errno": RETCODE.DBERR, "errmsg": "修改失败"})
        return http.JsonResponse({"errno": RETCODE.OK, "errmsg": "修改成功"})


class AuthUserView(LoginRequiredJSONMixin, View):
    def get(self, request):
        user = request.user
        real_name = user.real_name
        id_card = user.id_card

        return http.JsonResponse({
            "errno": RETCODE.OK,
            "errmsg": "认证信息保存成功",
            "real_name": real_name,
            "id_card": id_card
        })

    def post(self, request):
        # 接收参数
        user = request.user
        json_str = request.body.decode()
        data = json.loads(json_str)
        real_name = data.get('real_name')
        id_card = data.get('id_card')
        # 连接redis数据库
        redis_conn = get_redis_connection('sms_code')
        # pl = redis_conn.pipeline()
        # 判断用户是否点击三次，如果超过就不能在点击，因为要钱，防止恶意用户
        send_flag = redis_conn.get('card_%s' % user.id)
        # print(send_flag)
        if not send_flag:
            send_flag = redis_conn.setex('card_%s' % user.id, IMAGE_CODE_REDIS_EXPIRES * 12, 1)
        elif int(send_flag.decode()) > 3:
            return http.JsonResponse({"errmsg": "验证过于频繁，请一小时后重试"})
        else:
            send_flag = redis_conn.incrby('card_%s' % user.id, 1)
        # 校验参数
        if not all([real_name, id_card]):
            return http.JsonResponse({'errno': RETCODE.NECESSARYPARAMERR, "errmsg": "缺少参数"})
        if not re.match(r'^[\w]{2,4}$', real_name):
            return http.JsonResponse({'errno': RETCODE.USERERR, "errmsg": "请输入正确姓名"})
        if not re.match(r'^[1-9][0-9]{16}[0-9x]$', id_card):
            return http.JsonResponse({'errno': RETCODE.DBERR, "errmsg": "请输入正确身份证"})


        User.objects.filter(id=user.id).update(real_name=real_name, id_card=id_card)

        # return http.JsonResponse({
        #     "errno": RETCODE.OK,
        #     "errmsg": "认证信息保存成功",
        #     "real_name": real_name,
        #     "id_card": id_card
        # })

        # 调用celery验证身份证信息
        result = send_auth_id(real_name, id_card)
        if result == 1:
            User.objects.filter(id=user.id).update(real_name=real_name, id_card=id_card)
            return http.JsonResponse({
                "errno": RETCODE.OK,
                "errmsg": "实名认证通过",
                "real_name": real_name,
                "id_card": id_card
            })
        elif result == 0:
            return http.JsonResponse({"errno": RETCODE.DBERR, "errmsg": "验证不通过,请输入真实信息", })



class UserCenter(LoginRequiredJSONMixin, View):
    """个人中心"""

    def get(self, request):
        # 转字符串
        avatar = Url(str(request.user.avatar))

        return http.JsonResponse({
            'errno': '0',
            'errmsg': 'ok',
            'data': {
                "avatar": avatar,
                "mobile": request.user.mobile,
                "name": request.user.username,
                "user_id": request.user.id,
                "create_time": request.user.date_joined,
            }
        })


class UserCenterImage(View):
    """个人头像上传"""

    def post(self, request):
        # try:
        #     avatar = request.body
        # except:
        #     return http.JsonResponse({'code': 4002, 'errmsg': '数据不存在'})
        user = request.user
        # 3创建FastDFS链接对象
        client = Fdfs_client(settings.FASTDFS_PATH)
        # 获取前端传递的image文件
        image = request.FILES.get('avatar')
        # 上传图片到fastDFS
        print(image)
        res = client.upload_appender_by_buffer(image.read())
        # 判断是否上传成功
        if res['Status'] != 'Upload successed.':
            return http.JsonResponse({'code': 4302, 'errmsg': '文件读写错误'})
        # 获取上传后的路径
        image_url = res['Remote file_id']

        # 保存图片
        User.objects.filter(id=user.id).update(avatar=image_url)
        # User.objects.create(avatar=avatar, url=image_url)

        data = {
            'avatar_url': Url(image_url)
        }
        return http.JsonResponse({'code': 0, 'errmsg': '头像上传成功', 'data': data})
