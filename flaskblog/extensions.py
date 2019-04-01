# -*- coding: utf-8 -*-
"""
    @Author  : LiuZhian
    @Time    : 2019/3/28 0028 下午 10:27
    @Comment : 该文件包含一些程序中的扩展内容
"""
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_ckeditor import CKEditor
from flask_moment import Moment
from flask_login import LoginManager
from flask_wtf import CSRFProtect

# 实例化扩展对象
bootstrap = Bootstrap()
db = SQLAlchemy()
mail = Mail()
ckEditor = CKEditor()
moment = Moment()
login_manager = LoginManager()
csrfProtect = CSRFProtect()


# 加载用户函数
# 每当调用current_user时会调用此函数，user_id是flask-login会帮我们在cookie的session中设置的一个记录
@login_manager.user_loader
def load_user(user_id):
	from flaskblog.models import Admin
	user = Admin().query.get(int(user_id))
	return user


login_manager.login_view = "my_auth.login"
login_manager.login_message_category = "warning"
login_manager.login_message = "请先登录"
