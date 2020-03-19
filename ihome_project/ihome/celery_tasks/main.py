# Celery入口文件
from celery import Celery

# 为celery使用django配置文件进行设置
import os

if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'ihome.settings'

# 创建Celery实例
celery_app = Celery('ihome')

# 加载配置
celery_app.config_from_object('celery_tasks.config')

# 注册任务

# 短信认证
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.ali_sms'])
