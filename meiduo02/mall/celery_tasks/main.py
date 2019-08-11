from celery import Celery
import os


# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mall.settings")
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'mall.settings'

# 设置脚本
app = Celery(main='celery_tasks')

# 加载配置文件
app.config_from_object('celery_tasks.config')

# 自动加载任务
app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.mail'])

# celery -A celery_tasks.main worker -l info