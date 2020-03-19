
from django.conf.urls import url
from . import views

urlpatterns = [

    # 展示订单列表
    url(r'^api/v1.0/orders/$', views.GetOrderView.as_view(), ),

    # 接单和拒单
    url(r'^api/v1.0/orders/(?P<order_id>\d+)/status/$', views.OrderClerkView.as_view()),
    url(r'^api/v1.0/orders/(?P<order_id>\d+)/comment/$', views.OrderCommentView.as_view()),
]


