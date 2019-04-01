# -*- coding: utf-8 -*-
"""
    @Author  : LiuZhian
    @Time    : 2019/3/29 0029 上午 11:28
    @Comment : 主程序
"""
import os
import click
from flask import Flask, render_template

from flaskblog.blueprints.auth import auth_bp
from flaskblog.blueprints.admin import admin_bp
from flaskblog.blueprints.blog import blog_bp
from flaskblog.settings import config
from flaskblog.extensions import bootstrap, db, mail, ckEditor, moment, login_manager, csrfProtect
from flaskblog.models import Admin, Category, Comment
from flask_login import current_user

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


# 工厂函数
def create_app(config_name=None):
	if config_name is None:
		config_name = "dev"  # 默认开发环境,具体环境参数配置在settings.py中可以找到
	app = Flask(__name__)

	app.config.from_object(config[config_name])

	# 注册所有定义的蓝本
	register_blueprints(app)
	# 注册所有定义的扩展
	register_extensions(app)
	# 注册自定义命令
	register_commands(app)
	# 注册错误处理
	register_errors(app)
	# 注册模板上下文处理函数
	register_template_context(app)

	return app


# 注册蓝本函数
def register_blueprints(app):
	app.register_blueprint(auth_bp, url_prefix="/auth")
	app.register_blueprint(admin_bp, url_prefix="/admin")
	app.register_blueprint(blog_bp)


# 注册外部扩展函数
def register_extensions(app):
	bootstrap.init_app(app)
	db.init_app(app)
	ckEditor.init_app(app)
	moment.init_app(app)
	mail.init_app(app)
	login_manager.init_app(app)
	csrfProtect.init_app(app)


# 注册错误处理handler
def register_errors(app):
	@app.errorhandler(400)
	def bad_request(e):
		return render_template("error/400.html"), 400

	@app.errorhandler(404)
	def page_not_found(e):
		return render_template("error/404.html"), 404

	@app.errorhandler(500)
	def internal_server_error(e):
		return render_template("error/500.html"), 500


# 模板上下文函数（避免每次渲染模板时，页面的标题、管理员姓名等部分数据重复传参）
def register_template_context(app):
	@app.context_processor
	def make_template_context():
		admin = Admin.query.first()
		catogories = Category.query.order_by(Category.name).all()

		# 如果当前用户登录了，把未处理的评论信息构造到模板上下文中
		if current_user.is_authenticated:
			unread_comments = Comment.query.filter_by(reviewed=False).count()
		else:
			unread_comments = None
		return dict(admin=admin, catogories=catogories, unread_comments=unread_comments)  # 以字典形式返回


# 注册自定义命令
def register_commands(app):
	# 新建数据库命令
	@app.cli.command()
	@click.option("--drop", is_flag=True, help="删除原来的数据后新建数据库。")
	def initdb(drop):  # 命令就是函数名
		"""初始化数据库"""
		# 初始化数据库
		if drop:
			# 询问是否确认drop数据库
			click.confirm(text="这将要删除数据库，真的要继续吗？", abort=True)
			db.drop_all()
			click.echo("数据库删除成功！")
		db.create_all()
		click.echo("重新生成数据库...")

	# 生成虚拟数据命令
	@app.cli.command()
	@click.option("--category", default=10, help="生成的虚拟文章分类数，默认为10")
	@click.option("--post", default=50, help="生成的虚拟文章数，默认为50")
	@click.option("--comment", default=100, help="生成的虚拟评论数，默认为100")
	def forge(category, post, comment):
		"""生成虚拟数据"""
		# 开始生成虚拟数据
		from flaskblog.fakes import fake_admin, fake_categories, fake_comments, fake_posts
		# # 先清空数据库
		# db.drop_all()
		# db.create_all()

		click.echo("正在生成管理员身份...")
		fake_admin()

		click.echo("正在生成%d个文章分类..." % category)
		fake_categories(category)

		click.echo("正在生成%d篇文章..." % post)
		fake_posts(post)

		click.echo("正在生成%d条评论..." % comment)
		fake_comments(comment)

		click.echo("所有虚拟数据生成成功!")

	@app.cli.command()
	@click.option("--username", prompt=True, help="用户名")
	@click.option("--password", prompt=True, confirmation_prompt=True, hide_input=True, help="密码")
	def init(username, password):
		"""创客一个博客系统"""
		# 初始化数据库用户名密码
		click.echo("initializing database...")
		db.create_all()

		admin = Admin.query.first()
		# 如果已经存在管理员记录，就更新
		if admin:
			click.echo("该管理员已存在，更新中...")
			admin.username = username
			admin.set_password(password)

		# 否则创建新的管理员
		else:
			click.echo("创建一个新的管理员...")
			admin = Admin(
				username=username,
				blog_title="FlaskBlog",  # 博客标题
				blog_sub_title="This is a blog system build by %s" % username,  # 博客副标题
				name="Admin",
				about="Feel free to add some comments here."
			)
			admin.set_password(password)
			db.session.add(admin)

		category = Category.query.first()
		# 创建文章分类
		if category is None:
			click.echo("create the default category...")
			category = Category(name="默认")
			db.session.add(category)

		db.session.commit()
		click.echo("Done!")


if __name__ == '__main__':
	app = create_app("dev")
	app.run(host='0.0.0.0', port=5000, debug='True')
