# -*- coding: utf-8 -*-
"""
    @Author  : LiuZhian
    @Time    : 2019/3/28 0028 下午 10:33
    @comment : 该文件定义了数据库中的表shceme
"""
from flaskblog.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


# 管理员表
class Admin(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20))
	password_hash = db.Column(db.String(128))
	blog_title = db.Column(db.String(60))  # 博客标题
	blog_sub_title = db.Column(db.String(100))  # 博客副标题
	name = db.Column(db.String(30))
	about = db.Column(db.Text)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def validate_password(self, password):
		return check_password_hash(self.password_hash, password)


# 评论表（回复也视为评论）
class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	author = db.Column(db.String(30))
	email = db.Column(db.String(254))  # 评论者的邮箱
	site = db.Column(db.String(255))
	body = db.Column(db.Text)
	# 某条评论是否来自管理员
	from_admin = db.Column(db.Boolean, default=False)
	# 某条评论是否通过审核
	reviewed = db.Column(db.Boolean, default=False)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

	# 对应的文章，外键, 参数为[表名.列名]
	post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
	post = db.relationship("Post", back_populates="commments")

	# 被回复的评论
	replied_id = db.Column(db.Integer, db.ForeignKey("comment.id"))
	replied = db.relationship("Comment", back_populates="replies", remote_side=[id])

	# 一条评论对应多条回复
	replies = db.relationship("Comment", back_populates="replied", cascade="all")


# 文章表
class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)  # id 主键
	title = db.Column(db.String(60))
	body = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
	can_comment = db.Column(db.Boolean, default=True)  # 文章是否可以评论

	# 和评论是一对多关系
	# 第一个参数是另一张表在模型文件中定义的类名,back_populates定义的反向关系,
	# 第三个是数据库级联操作（一定是在一对多中的一这边设置级联）
	commments = db.relationship("Comment", back_populates="post", cascade="all,delete-orphan")

	# 文章分类和文章是一对多关系
	category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
	category = db.relationship('Category', back_populates='posts')


# 文章分类表
class Category(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(30), unique=True)

	posts = db.relationship('Post', back_populates='category')

	def delete(self):
		# 第一类作为默认分类
		default_category = Category.query.get(1)
		# 当某一类别被删除时，其之前所对应的文章全部被归为默认分类
		posts = self.posts[:]
		for p in posts:
			p.category = default_category
		db.session.delete(self)
		db.session.commit()

