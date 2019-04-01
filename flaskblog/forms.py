# -*- coding: utf-8 -*-
"""
    @Author  : LiuZhian
    @Time    : 2019/3/30 0030 上午 9:55
    @Comment : 各种表单的创建
"""
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms import StringField, SubmitField, SelectField, TextAreaField, BooleanField, HiddenField,PasswordField
from wtforms.validators import DataRequired, Length, Email, ValidationError, Optional, URL
from flaskblog.models import Category


# 登录表单
class LoginForm(FlaskForm):
	username = StringField(label="用户名", validators=[DataRequired("请输入用户名"), Length(1, 20)])
	password = PasswordField(label="密码", validators=[DataRequired("请输入密码"), Length(1, 128)])
	rememberMe = BooleanField(label="记住我")
	submit = SubmitField("登录")


# 创建文章表单
class PostForm(FlaskForm):
	title = TextAreaField(label="文章标题", validators=[DataRequired("请输入文章标题"), Length(1, 60)])
	category = SelectField(label="文章类别", coerce=int, default=1)
	body = CKEditorField(label="正文", validators=[DataRequired("请输入文章正文")])
	submit = SubmitField()

	def __init__(self, *args, **kwargs):
		super(PostForm, self).__init__(*args, **kwargs)
		# 从Category表中获得类别的id和类别的选项值
		self.category.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]


# 添加分类表单
class CategoryForm(FlaskForm):
	name = StringField(label="类别名称", validators=[DataRequired("请输入类别名称"), Length(1, 30)])
	submit = SubmitField()

	# 自定义验证器，flask中默认将validate_XXX()的函数作为验证器验证表单框，XXX为表单类中定义的组件名
	def validate_name(self, field):
		# 如果数据库中已经存在同名类别
		if Category.query.filter_by(name=field.data).first():
			raise ValidationError("类别已存在")


# 发表评论表单
class CommentForm(FlaskForm):
	author = StringField('作者', validators=[DataRequired("请输入你的名称"), Length(1, 30)])
	email = StringField('Email', validators=[DataRequired("请输入邮箱"), Email(), Length(1, 254)])
	site = StringField('Site', validators=[Optional(), URL(), Length(0, 255)])
	body = TextAreaField('评论内容', validators=[DataRequired("请输入评论内容")])
	submit = SubmitField()


# 管理员评论表单
class AdminCommentForm(CommentForm):
	author = HiddenField()
	email = HiddenField()
	site = HiddenField()


# 博客设置表单
class SettingForm(FlaskForm):
	name = StringField('姓名', validators=[DataRequired("请输入你的姓名"), Length(1, 70)])
	blog_title = StringField('博客标题', validators=[DataRequired("请输入博客标题"), Length(1, 60)])
	blog_sub_title = StringField('博客副标题', validators=[DataRequired("请输入博客副标题"), Length(1, 100)])
	about = CKEditorField('关于页面信息', validators=[DataRequired("请输入关于页面信息")])
	submit = SubmitField()
