# -*- coding: utf-8 -*-
"""
    @Author  : LiuZhian
    @Time    : 2019/3/28 0028 下午 10:26
"""

from flask import Blueprint, render_template, flash
from flaskblog.forms import LoginForm
from flaskblog.utils import redirect_back
from flask_login import current_user, login_user, logout_user, login_required
from flaskblog.models import Admin

# 注册一个蓝本实例，这是一个用于注册路由的临时对象
auth_bp = Blueprint("my_auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
	# 如果已经登陆，直接跳到主页
	if current_user.is_authenticated:
		return render_template("blog/index.html")
	else:
		form = LoginForm()
		if form.validate_on_submit():
			username = form.username.data
			password = form.password.data
			rememberMe = form.rememberMe.data
			admin = Admin.query.first()
			if admin:
				if username == admin.username and admin.validate_password(password):
					# login_user()是flask-login中提供的登录函数
					# 将根据从数据库中查询到的对象和表单张是否记住我选项，
					# 封装一个user_id和remember字段放入cookie的session中
					login_user(admin, rememberMe)
					flash('%s欢迎回来' % admin.name, 'info')
					return redirect_back()
				flash('用户名或密码错误.', 'warning')
			# 数据库中还没有管理员记录
			else:
				flash('No account in database!', 'warning')

		return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
	logout_user()
	flash("退出登录成功！", "info")
	return redirect_back()



