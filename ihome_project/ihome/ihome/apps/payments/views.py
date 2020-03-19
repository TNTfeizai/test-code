import os

from alipay import AliPay
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django import http
from django.http import JsonResponse

from ihome.utils.response_code import RETCODE
from ihome.utils.views import LoginRequiredJSONMixin
# Create your views here.
from orders.models import Order
from .models import Payment
from . import contents


class PaymentStatusView(View):
    """保存订单支付结果"""

    def get(self, request):
        # 获取前端传入的请求参数
        query_dict = request.GET
        data = query_dict.dict()
        # 获取并从请求参数中剔除signature 签名
        signature = data.pop('sign')

        # 创建支付宝支付对象
        alipay = AliPay(
            appid=contents.ALIPAY_APPID,
            app_notify_url=None,
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),
            sign_type="RSA2",
            debug=contents.ALIPAY_DEBUG
        )

        # 校验这个重定向是否是alipay重定向过来的
        success = alipay.verify(data, signature)
        if success:
            # 读取order_id
            order_id = data.get('out_trade_no')
            # 读取支付宝流水号
            trade_id = data.get('trade_no')
            # 保存Payment模型类数据
            Payment.objects.create(
                order_id=order_id,
                trade_id=trade_id
            )

            # 修改订单状态为待评价
            Order.objects.filter(order_id=order_id, status=Order.ORDER_STATUS['WAIT_PAYMENT']).update(
                status=Order.ORDER_STATUS["WAIT_COMMENT"]
            )

            # 响应支付宝订单id trade_id
            # context = {
            #     'trade_id': trade_id
            # }
            # 响应支付宝订单id trade_id
            data = {
                "trade_id": trade_id
            }
            return JsonResponse({"errno": RETCODE.OK, "errmsg": "支付成功", "data": data})
            # return render(request, 'pay_success.html', context)
        else:
            # 若状态码为5006 则表示支付失败
            return JsonResponse({"errno": RETCODE.PARAMERR, "errmsg": "支付成功"})
            # 订单支付失败,重定向到我的订单
            # return redirect(reverse('orders:info'))
            # return http.HttpResponseForbidden('非法请求')


class PaymentView(LoginRequiredJSONMixin, View):
    """订单支付功能"""

    def get(self, request, order_id):
        # 查询要支付的订单
        user = request.user
        # 校验参数
        try:
            # 用户订单号为表里的主键, 并且是当前登录用户, 并且订单状态是待支付
            order = Order.objects.get(order_id=order_id, user=user, status=Order.ORDER_STATUS["WAIT_PAYMENT"])
        except Order.DoesNotExist:
            # 若订单信息错误 状态码为5006
            return JsonResponse({"errno": RETCODE.PARAMERR, "errmsg": "订单信息错误"})
            # return http.HttpResponseForbidden('订单信息错误')

        # 创建支付宝支付对象
        alipay = AliPay(
            appid=contents.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url, 我们是ali返回页面不采用这个
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),
            sign_type="RSA2",
            debug=contents.ALIPAY_DEBUG
        )

        # 生成登录支付宝连接
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,  # 路径参数传递过来的也是字符串类型
            total_amount=str(order.amount),  # 用户支付总金额,转为str类型再传入
            subject="爱家%s" % order_id,  # 用户展示的订单标题
            return_url=contents.ALIPAY_RETURN_URL,  # 回调地址
        )

        # 响应登录支付宝连接
        # 真实环境电脑网站支付网关：https://openapi.alipay.com/gateway.do? + order_string
        # 沙箱环境电脑网站支付网关：https://openapi.alipaydev.com/gateway.do? + order_string
        alipay_url = contents.ALIPAY_URL + "?" + order_string
        return JsonResponse({"errno": RETCODE.OK, "errmsg": "OK", 'alipay_url': alipay_url})