from celery_tasks.main import app
from django.core.mail import send_mail
from users.utils import verify_token

@app.task
def send_verify_email(id,email):

    subject = '美多商城激活邮件' # 主题
    message = '' # 内容
    from_email = 'sunsyw@163.com'
    recipient_list = [email]  # 收件人


    token = verify_token(id,email)
    verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=%s' % token
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)

    send_mail(subject, message, from_email, recipient_list,
              html_message=html_message)