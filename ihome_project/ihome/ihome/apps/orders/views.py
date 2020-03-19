import json, time

import json

import datetime
from django import http
from django.conf import settings
from django.views import View

from homes.models import House
from ihome.utils.complete_url import Url
from ihome.utils.constants import SEND_SMS_TEMPLATE_ID

from ihome.utils.views import LoginRequiredJSONMixin

from ihome.utils.response_code import RETCODE
from ihome.utils.views import LoginRequiredJSONMixin

from orders.models import Order
from django import http
import json
from django.shortcuts import render

# Create your views here.
from django.views import View

from users.models import User
from .models import Order

logger = settings.LOGGER


class GetOrderView(LoginRequiredJSONMixin,View ):
    def get(self, request):
        # 接收参数
        role = request.GET.get('role')
        if not all([role]):
            return http.JsonResponse({"errno": RETCODE.NECESSARYPARAMERR, "errmsg": "缺少参数"})
            # 查询出所有房东对应的房屋信息
        try:
            user = User.objects.get(id=request.user.id)
            # user = User.objects.get(id=1)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({"errno": RETCODE.DBERR, "errmsg": "查找用户失败"})
        # 构建容器
        orders = []
        # 判断如果是房东，展示所有他对应的房屋，展示对应的订单信息
        if role == 'landlord':
            # 查出房东对应的所有房屋
            houses = user.houses.all()
            # 遍历所有的房子，找出所有的对应订单，并且返回数据
            for house in houses:
                landlord_orders = house.order_set.all()
                # 通过所以的房子遍历出所有房子对应的订单
                for landlord_order in landlord_orders:
                    if Order.ORDER_STATUS_ENUM[landlord_order.status] == "WAIT_COMMENT":
                        status = "COMPLETE"
                        landlord_order.status = Order.ORDER_STATUS["COMPLETE"]
                        landlord_order.save()
                    else:
                        status = Order.ORDER_STATUS_ENUM[landlord_order.status]
                    order = {
                        "amount": landlord_order.amount,
                        "comment": landlord_order.comment,
                        "ctime": landlord_order.create_time,
                        "days": landlord_order.days,
                        "end_date": landlord_order.end_date,
                        "img_url": Url(house.index_image_url),
                        "order_id": landlord_order.order_id,
                        "start_date": landlord_order.begin_date,
                        "status": status,
                        "title": house.title,
                    }
                    orders.append(order)
            data = {'orders': orders}
            return http.JsonResponse({"errno": "0", "errmsg": "OK", "data": data})
        # 如果是房客,显示他所有订单
        elif role == 'custom':
            # 通过用户外键查询到所有的订单
            custom_orders = user.orders.all()
            # user.orders_set.all()===user.orders.all()
            # 遍历订单
            for custom_order in custom_orders:
                if Order.ORDER_STATUS_ENUM[custom_order.status] == "COMPLETE":
                    status = "WAIT_COMMENT"
                    custom_order.status = Order.ORDER_STATUS["WAIT_COMMENT"]
                    custom_order.save()
                else:
                    status = Order.ORDER_STATUS_ENUM[custom_order.status]
                    # 通过订单找出房子
                house = custom_order.house
                order = {
                    "amount": custom_order.amount,
                    "comment": custom_order.comment,
                    "ctime": custom_order.create_time,
                    "days": custom_order.days,
                    "end_date": custom_order.end_date,
                    "img_url": Url(house.index_image_url),
                    "order_id": custom_order.order_id,
                    "start_date": custom_order.begin_date,
                    "status": status,
                    "title": house.title
                }
                orders.append(order)
            data = {'orders': orders}
            return http.JsonResponse({"errno": "0", "errmsg": "OK", "data": data})

    def post(self, request):
        # 接收参数
        json_dict = json.loads(request.body.decode())
        house_id = json_dict.get('house_id')
        start_date = json_dict.get('start_date')
        end_date = json_dict.get('end_date')
        # 校验参数
        if not all([house_id, start_date, end_date]):
            return http.JsonResponse({"errno": RETCODE.NECESSARYPARAMERR, "errmsg": "缺少参数"})

        # 将字符串转换为datetime类型
        fmt = "%Y-%m-%d"

        # 将字符串先转化为实践对象,时间对象一般分为九个年月日时分秒等
        start_date_str = time.strptime(start_date, fmt)
        end_date_str = time.strptime(end_date, fmt)

        # 将年月日通过切片提取处来，并用三个参数接收
        start_year, start_month, start_day = start_date_str[:3]
        end_year, end_month, end_day = end_date_str[:3]

        # 将提取出来的年月日参数转化为datetime.datetime类型
        start_day_time = datetime.datetime(start_year, start_month, start_day)
        end_day_time = datetime.datetime(end_year, end_month, end_day)

        # 将datetime类型进行天数差计算
        days = (end_day_time - start_day_time).days
        # 将提取出来的年月日参数转化为datetime.date类型，比较大小
        start_date_datetime = datetime.date(start_year, start_month, start_day)
        end_date_datetime = datetime.date(end_year, end_month, end_day)
        # # 生成订单号
        # order_id = time.timezone.localtime().strftime('%Y%m%d%H%M%S') + ('%09d' % user_id)
        while True:
            # 通过房屋id查询到房屋对象
            house = House.objects.get(id=house_id)
            # 获取原始订单数量
            origin_order_count = house.order_count
            # 通过房屋对象查询出房屋所有的订单
            user_orders = house.order_set.all()
            # 如果有人下单
            if user_orders:
                # 便利所有的订单，看这个起始时间是否存在有订单已经订购的情况，有则返回房屋已被订购
                for user_order in user_orders:
                    # 获取该房屋所有订单的起始时间和结束时间
                    order_start_time = user_order.begin_date
                    order_end_time = user_order.end_date
                    # 判断用户下单时间是否在别人租房时间内
                    if start_date_datetime.__le__(order_end_time) and end_date_datetime.__ge__(
                            order_start_time):
                        return http.JsonResponse({"errno": RETCODE.STOCKERR, "errmsg": "该时间段以被租购"})
            # house_price = "房屋单价"
            house_price = house.pricen
            # amount = "订单总金额"
            amount = house_price * days
            # status = "订单状态"
            # comment = "订单的评论信息或者拒单原因"
            # 保存数据
            user_id = request.user.id
            # user_id = 2
            now = datetime.datetime.now()
            order_id = '%s%09d' % (now.strftime("%Y%m%d%H%M%S"), user_id)
            # 乐观锁
            new_order_count = origin_order_count + SEND_SMS_TEMPLATE_ID
            # time.sleep(7)
            result = House.objects.filter(id=house_id, order_count=origin_order_count).update(
                order_count=new_order_count)
            if result == 0:
                continue
            # 如果没人下单则跳出循环，进行订单保存
            break
        # 保存数据
        try:
            # 保存下单用户的id,房屋id,开始时间，结束时间
            order = Order.objects.create(order_id=order_id, user_id=user_id, begin_date=start_date, end_date=end_date,
                                         house_id=house_id,
                                         days=days, house_price=house_price, amount=amount,
                                         status=Order.ORDER_STATUS["WAIT_ACCEPT"])
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({"errno": RETCODE.DBERR, "errmsg": "生成订单失败"})
        data = {
            'order_id': order.order_id
        }
        return http.JsonResponse({"errno": RETCODE.OK, "errmsg": "下单成功", "data": data})


class OrderClerkView(LoginRequiredJSONMixin, View):
    def put(self, request, order_id):
        # 接收参数
        try:
            order = Order.objects.get(order_id=order_id)
        except:
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '数据错误'})
        action = json.loads(request.body.decode()).get('action')
        reason = json.loads(request.body.decode()).get('reason')
        # 校验参数
        if not all([action]):
            return http.JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少必传参数'})
        # 业务逻辑
        if action == 'accept':
            # Order.objects.get(id=order_id).updata(status=3)
            order.status = Order.ORDER_STATUS['WAIT_COMMENT']
            order.save()
            #
        elif action == 'reject':
            try:
                # Order.objects.filter(id=order_id).updata(comment=reason, status=6)
                order.comment = reason
                order.status = Order.ORDER_STATUS['REJECTED']
                order.save()
            except:
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '数据错误'})
        return http.JsonResponse({'errno': '0', 'errmsg': '操作成功'})


class OrderCommentView(LoginRequiredJSONMixin, View):
    """评论订单"""

    def put(self, request, order_id):
        # 接收参数
        try:
            Order.objects.get(order_id=order_id)
        except:
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '数据错误'})
        comment = json.loads(request.body.decode()).get('comment')
        # 校验参数
        if not all([comment]):
            return http.JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少参数'})
        # 业务逻辑
        try:
            # Order.objects.get(id=order_id).updata(comment=comment, status=4)
            order = Order.objects.get(order_id=order_id)
            order.comment = comment
            order.status = Order.ORDER_STATUS['COMPLETE']
            order.save()
        except:
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '数据错误'})
        return http.JsonResponse({'errno': '0', 'errmsg': '评论成功'})
