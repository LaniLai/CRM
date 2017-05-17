# ！/usr/bin/env python
# -*- coding:utf-8 -*-
# __Author__ Jianer


import smtplib, random, string
from email.mime.text import MIMEText
from repository import models

mail_host = "smtp.163.com"  # 使用的邮箱的smtp服务器地址，这里是163的smtp地址
mail_user = "18803561683@163.com"  # 用户名
mail_pass = "1314leguan"  # 密码
mail_postfix = "163.com"  # 邮箱的后缀，网易就是163.com


def initialization(customer_obj):
    mailto_list = [customer_obj.email, ]  # 收件人(列表)
    # 生成账号密码
    stu_user = 'stu1702020{id}'.format(id=customer_obj.id)
    stu_pwd = ''.join(random.sample(string.ascii_lowercase+string.digits, 8))
    content = """
        欢迎加入老男孩：
        在线登陆CRM，随时查看您的成绩，账号：{0}，密码：{1}
        网址 xxxx.com
            """.format(stu_user, stu_pwd)
    for i in range(1):  # 发送1封，上面的列表是几个人，这个就填几
        if send_mail(mailto_list, "欢迎加入老男孩", content):  # 邮件主题和邮件内容
            # 发送成功的话, 创建用户和密码用于登陆并绑定学生角色
            return True
        else:
            return False


def send_mail(to_list, sub, content):
    me = "Hello, Girl or Boy" + "<" + mail_user + "@" + mail_postfix + ">"
    msg = MIMEText(content, _subtype='plain')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)  # 将收件人列表以‘；’分隔
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)  # 连接服务器
        server.login(mail_user, mail_pass)  # 登录操作
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        return True
    except Exception as e:
        return False







