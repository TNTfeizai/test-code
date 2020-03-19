
from django.conf.urls import url

from . import views

urlpatterns = [
    # 城区列表
    url(r'^api/v1.0/areas/$', views.AreasView.as_view()),
    # 发布房源
    url(r'^api/v1.0/houses/$', views.HousesView.as_view()),
    # 房屋详情页面
    url(r'^api/v1.0/houses/(?P<house_id>\d+)/$', views.HousesDetailView.as_view()),
    # 上传房屋图片
    url(r'^api/v1.0/houses/(?P<house_id>\d+)/images/$', views.UploadImageView.as_view()),
    # 房屋列表
    url(r'^api/v1.0/user/houses/$',views.HouseListView.as_view()),
    # 首页房屋推荐
    url(r'^api/v1.0/houses/index/$',views.HouseIndex.as_view()),
    # 房屋数据搜索
    # url(r'^api/v1.0/houses/$',views.HouseSearch.as_view()),




]

