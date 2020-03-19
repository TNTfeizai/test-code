
from django.conf.urls import url
from . import views

urlpatterns = [
    # 首页房屋推荐
    url(r'^api/v1.0/houses/index/', views.IndexView.as_view()),
    # 用户注册
    url(r'^api/v1.0/users/$', views.RegisterView.as_view()),
    # 用户登录
    url(r'^api/v1.0/session/$', views.LoginView.as_view()),
    # 修改用户名
    url(r'^api/v1.0/user/name/$', views.ChangeUsernameView.as_view()),
    # 用户认证身份证信息　api/v1.0/user/auth
    url(r'^api/v1.0/user/auth/$', views.AuthUserView.as_view()),
    # 展示用户中心
    url(r'^api/v1.0/user/$', views.UserCenter.as_view()),
    # 上传个人头像
    url(r'^api/v1.0/user/avatar/$', views.UserCenterImage.as_view()),
    # 找回密码
    url(r'^api/v1.0/retrieve/password/', views.RetrievePasswordView.as_view()),
    # 重置密码
    url(r'^api/v1.0/reset/password/', views.ResetPasswordView.as_view()),
]
