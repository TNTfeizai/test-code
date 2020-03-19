import json
import datetime
from django import http
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.db import transaction
from django.core.cache import cache

from ihome.utils.views import LoginRequiredJSONMixin
from orders.models import Order
from .models import Area, Facility, House, HouseImage
from .contents import not_login_user_id
from fdfs_client.client import Fdfs_client
from ihome.utils.response_code import RETCODE

from homes.models import HouseImage, House
from ihome.utils.views import LoginRequiredJSONMixin
from orders.models import Order
from ihome.utils.complete_url import Url

logger = settings.LOGGER


# Create your views here.

class AreasView(View):
    """城区列表"""

    def get(self, request):
        """获取城区列表"""
        # 读取缓存数据
        data = cache.get("data")
        if not data:
            data = []
            areas = Area.objects.all()
            for area in areas:
                data.append({
                    "aid": area.id,
                    "aname": area.name
                })
            # 存储地区缓存数据
            cache.set("data", data, 3600)

        return JsonResponse({"errmsg": "获取成功", "errno": RETCODE.OK,
                             "data": data})


class HousesView(View):
    """房源"""

    def get(self, request, p=1):
        """房屋数据搜索"""
        aid = request.GET.get('aid')
        sd = request.GET.get('sd')
        ed = request.GET.get('ed')

        # 排序规则
        sort = request.GET.get('sk', 'new')
        if sort == 'booking':
            sort_field = 'order_count'
        elif sort == 'price-inc':
            sort_field = 'price'
        elif sort == 'price-des':
            sort_field = '-price'
        else:
            sort_field = '-create_time'

        # 当用户点击搜索时, 默认没有这些值
        if aid == sd == ed == "":
            query_houses = House.objects.order_by(sort_field)
            date = datetime.date.today().strftime('%Y-%m-%d')
            sd = date
            ed = date
        # 当用户只选择了区域, 却没有选择入住时间
        elif sd == ed == "":
            query_houses = House.objects.filter(area_id=aid).order_by(sort_field)
            date = datetime.date.today().strftime('%Y-%m-%d')
            sd = date
            ed = date
        # 当用户选择了时间, 却没有选择区域
        elif aid == "":
            query_houses = House.objects.order_by(sort_field)
        else:
            query_houses = House.objects.filter(area_id=aid).order_by(sort_field)

        houses = []
        for house in query_houses:
            if Order.objects.filter(house_id=house.id, begin_date__lt=sd, end_date__gte=ed):
                continue
            else:
                houses.append({
                    'address': house.address,
                    'area-name': house.area.name,
                    'ctime': house.create_time,
                    'house_id': house.id,
                    'img_url': Url(house.index_image_url),
                    'order_count': house.order_count,
                    'price': house.price,
                    'room_count': house.room_count,
                    'title': house.title,
                    'user_avatar': Url(str(house.user.avatar))
                })

        # 2.1创建分页对象，指定列表、页大小
        paginator = Paginator(houses, 5)
        # 2.2获取指定页码的数据
        page_skus = paginator.page(p)
        # 2.3获取总页数
        total_page = paginator.num_pages

        data = {
            'houses': houses,
            'total_page': total_page
        }

        return http.JsonResponse({'errno': "0", 'errmsg': 'ok', 'data': data})

    def post(self, request):
        """发布房源   保存"""
        # 获取登录对象
        user = request.user
        if user.is_authenticated:
            # 接收参数
            json_dict = json.loads(request.body.decode())
            title = json_dict.get("title")
            price = json_dict.get("price")
            area_id = json_dict.get("area_id")
            address = json_dict.get("address")
            room_count = json_dict.get("room_count")
            acreage = json_dict.get("acreage")
            unit = json_dict.get("unit")
            capacity = json_dict.get("capacity")
            beds = json_dict.get("beds")
            deposit = json_dict.get("deposit")
            min_days = json_dict.get("min_days")
            max_days = json_dict.get("max_days")
            facility = json_dict.get("facility")

            # 校验参数
            if not all(
                    [title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days,
                     max_days,
                     facility]):
                return JsonResponse({"errmsg": "参数不全", "errno": RETCODE.PARAMERR})

            try:
                price = int(price)
                room_count = int(room_count)
                acreage = int(acreage)
                capacity = int(capacity)
                deposit = int(deposit)
                min_days = int(min_days)
                max_days = int(max_days)
                # facility = eval(facility)
            except:
                return JsonResponse({"errmsg": "参数类型错误", "errno": RETCODE.PARAMERR})

            try:
                Area.objects.get(id=area_id)
                # area = Area.objects.get(id=area_id)
            except Area.DoesNotExist:
                return JsonResponse({"errmsg": "城区不存在", "errno": RETCODE.NODATAERR})

            try:
                # 查询设施列表对象结果集
                facilities = Facility.objects.filter(id__in=facility)
            except Facility.DoesNotExist:
                return JsonResponse({"errmsg": "设施不存在", "errno": RETCODE.NODATAERR})

            facility_id_list = [i.id for i in facilities]

            # 开启事务
            with transaction.atomic():
                # 创建保存点
                save_id = transaction.savepoint()
                try:
                    # 保存房屋信息
                    house = House.objects.create(
                        user=user,
                        area_id=area_id,
                        title=title,
                        price=price,
                        address=address,
                        room_count=room_count,
                        acreage=acreage,
                        unit=unit,
                        capacity=capacity,
                        beds=beds,
                        deposit=deposit,
                        min_days=min_days,
                        max_days=max_days,
                    )

                    # 多对多保存, 用刚保存的实例对象.字段名.add(对应的字段名)
                    house.facility.add(*facility_id_list)
                    # for facility_id in facility_id_list:
                    #     house.facility.add(facility_id)
                except Exception as e:
                    settings.LOGGER.error(e)
                    transaction.savepoint_rollback(save_id)
                    return JsonResponse({"errno": RETCODE.DBERR, "errmsg": "保存房屋信息失败"})
                else:
                    # 提交事务
                    transaction.savepoint_commit(save_id)
            house_id = house.id
            return JsonResponse({"errno": RETCODE.OK, "errmsg": "发布成功", "data": {"house_id": house_id}})
        else:
            return JsonResponse({'errno': RETCODE.SESSIONERR, 'errmsg': '用户未登录'})


class HousesDetailView(View):
    """房屋详情页"""

    def get(self, request, house_id):
        """获取详情页数据"""
        try:
            house_project = House.objects.get(id=house_id)
        except House.DoesNotExist:
            return JsonResponse({"errmsg": "房屋不存在", "errno": RETCODE.NODATAERR})
        # 获取登录对象
        login_user = request.user
        if login_user.is_authenticated:
            # 当前登录用户的用户id
            user_id = login_user.id
        else:
            user_id = not_login_user_id

        # 获取订单集合
        order_dict = Order.objects.filter(house=house_project)
        # 用户评论列表
        comments = []
        for order in order_dict:
            comments.append({
                "comment": order.comment,  # 用户评论
                "ctime": order.create_time,  # 订单创建时间
                "user_name": order.user.username  # 评论用户的用户名
            })

        facilities = []  # 设施列表
        facility_ids = House.objects.filter(id=house_id).first().facility.all()
        for facility_id in facility_ids:
            facility_id = facility_id
            facilities.append(facility_id.id)

        # 房屋图片路径
        house_image_dict = HouseImage.objects.filter(house=house_project)
        img_urls = []
        for house_image in house_image_dict:
            img_urls.append(Url(house_image.url))
        data = {
                   "house": {
                       "acreage": house_project.acreage,  # 房屋面积
                       "address": house_project.address,  # 房屋地址
                       "beds": house_project.beds,  # 房屋床铺的配置
                       "capacity": house_project.capacity,  # 房屋容纳的人数
                       "comments": comments,  # 用户评论列表
                       "deposit": house_project.deposit,  # 房屋押金
                       "facilities": facilities,  # 设施列表
                       "hid": house_project.id,  # 房屋id
                       "img_urls": img_urls,  # 房屋图片的路径
                       "max_days": house_project.max_days,  # 最多入住天数，0表示不限制
                       "min_days": house_project.min_days,  # 最少入住日期
                       "price": house_project.price,  # 单价
                       "room_count": house_project.room_count,  # 房间数目
                       "title": house_project.title,  # 房屋标题
                       "unit": house_project.unit,  # 房屋单元， 如几室几厅
                       "user_avatar": Url(str(house_project.user.avatar)),  # 房主头像
                       "user_id": house_project.user.id,  # 房主id
                       "user_name": house_project.user.real_name,  # 房主真实姓名
                   },
                   "user_id": user_id
               }
        return JsonResponse({"data": data, "errmsg": "OK", "errno": RETCODE.OK})


class UploadImageView(LoginRequiredJSONMixin, View):
    """上传房源图片视图"""

    def post(self, request, house_id):
        try:
            house = House.objects.get(id=house_id)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'errno': RETCODE.NODATAERR, 'errmsg': '数据不存在'})

        # 3创建FastDFS链接对象
        client = Fdfs_client(settings.FASTDFS_PATH)
        # 获取前端传递的image文件
        image = request.FILES.get('house_image')
        # 上传图片到fastDFS
        res = client.upload_by_buffer(image.read())
        # 判断是否上传成功
        if res['Status'] != 'Upload successed.':
            return http.JsonResponse({'errno': 4302, 'errmsg': '文件上传失败'})
        # 获取上传后的路径
        image_url = res['Remote file_id']

        # 开启事务
        with transaction.atomic():
            # 创建保存点
            save_id = transaction.savepoint()

            try:
                # 保存默认图片
                if not house.index_image_url:
                    house.index_image_url = image_url
                    house.save()
                # 保存图片
                HouseImage.objects.create(house_id=house_id, url=image_url)
            except Exception as e:
                logger.error(e)
                transaction.savepoint_rollback(save_id)
                return JsonResponse({"errno": RETCODE.DBERR, "errmsg": "保存房屋图片失败"})
            else:
                # 提交事务
                transaction.savepoint_commit(save_id)

        data = {
            'url': Url(image_url)
        }

        return http.JsonResponse({'errno': RETCODE.OK, 'errmsg': '图片上传成功', 'data': data})


class HouseListView(LoginRequiredJSONMixin, View):
    """我的房屋列表视图"""

    def get(self, request):
        user = request.user
        query_houses = House.objects.filter(user=user)
        houses = []
        for house in query_houses:
            houses.append({
                'address': house.address,
                'area_name': house.area.name,
                'ctime': house.create_time,
                'house_id': house.id,
                'img_url': Url(house.index_image_url),
                'order_count': house.order_count,
                'price': house.price,
                'room_count': house.room_count,
                'title': house.title,
                'user_avatar': Url(str(house.user.avatar))
            })

        return http.JsonResponse({'errno': RETCODE.OK, 'errmsg': 'ok', 'data': {'houses': houses}})


class HouseIndex(View):
    """首页房屋推荐"""

    def get(self, request):
        query_houses = House.objects.all()[0:5]

        data = []

        for house in query_houses:
            data.append({
                'house_id': house.id,
                'img_url': Url(house.index_image_url),
                'title': house.title
            })

        return http.JsonResponse({'errno': 0, 'errmsg': 'ok', 'data': data})
