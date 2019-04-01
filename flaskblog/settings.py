# -*- coding: utf-8 -*-
"""
    @Author  : LiuZhian
    @Time    : 2019/3/29 0029 上午 11:36
    @Comment : 程序配置组织，可用于工厂函数创建主程序
"""
import os

base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))  # 项目base目录 F:\Python\blogProject


class BaseConfig(object):
	SECRET_KEY = "secret key"
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	# DEBUG = True
	BLOG_EMAIL = "929910266@qq.com"  # 管理员邮箱地址
	MAIL_SERVER = "smtp.qq.com"  # 邮件服务器的主机名或IP地址
	MAIL_PORT = 465  # 邮件服务器的端口
	MAIL_USE_SSL = True
	MAIL_USERNAME = "929910266@qq.com"
	
	MAIL_DEFAULT_SENDER = ('FlaskBlog管理员', MAIL_USERNAME)

	BLOG_POST_PER_PAGE = 10
	BLOG_COMMENT_PER_PAGE = 15

	# 系统主题(到时候会配置在程序cookies中)
	BLOG_THEMES = {"perfect_blue": "闪亮蓝", "black_swan": "炫酷黑", "sketchy": "素描风格", "pulse": "高级紫"}


class DevConfig(BaseConfig):
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_dir, "data-dev.db")


config = {
	"dev": DevConfig
}
