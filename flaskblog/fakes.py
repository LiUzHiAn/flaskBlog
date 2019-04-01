# -*- coding: utf-8 -*-
"""
    @Author  : LiuZhian
    @Time    : 2019/3/28 0028 下午 11:51
	@comment : 生成虚拟数据库数据
"""
from flaskblog.extensions import db
from sqlalchemy.exc import IntegrityError
from flaskblog.models import Admin, Category, Post, Comment
from faker import Faker
import random

fake = Faker("zh_CN")  # 生成虚拟中文数据


def fake_admin():
	admin = Admin(
		username='admin',
		blog_title='刘知安的Blog',
		blog_sub_title="Hola~ Bienvenido a mi blog!",
		name='刘知安',
		about="Umm...这是我用flask搭建的个人博客"
	)
	admin.set_password("admin")
	db.session.add(admin)
	db.session.commit()


def fake_categories(cnt=10):
	category = Category(
		name="Default"
	)
	db.session.add(category)
	db.session.commit()

	# 添虚拟分类
	for i in range(cnt):
		# 可能产生相同的分类名，而category表中的name字段定义为unique，从而数据库可能抛出异常
		category_item = Category(
			name=fake.word()
		)
		db.session.add(category_item)
		try:
			db.session.commit()
		except IntegrityError as e:
			db.session.rollback()


def fake_posts(cnt=50):
	# 添虚拟分类
	for i in range(cnt):

		post = Post(
			title=fake.sentence(),
			body=fake.text(2000),
			timestamp=fake.date_time_this_year(),
			# 随机选取一个分类作为该文章的类别
			category=Category.query.get(random.randint(1, Category.query.count()))
		)
		db.session.add(post)
		try:
			db.session.commit()
		except IntegrityError as e:
			db.session.rollback()


def fake_comments(count=500):
	for i in range(count):
		comment = Comment(
			author=fake.name(),
			email=fake.email(),
			site=fake.url(),
			body=fake.sentence(),
			timestamp=fake.date_time_this_year(),
			reviewed=True,
			post=Post.query.get(random.randint(1, Post.query.count()))
		)
		db.session.add(comment)

	salt = int(count * 0.1)  # 50 条
	for i in range(salt):
		# 未审核通过的评论
		comment = Comment(
			author=fake.name(),
			email=fake.email(),
			site=fake.url(),
			body=fake.sentence(),
			timestamp=fake.date_time_this_year(),
			reviewed=False,
			post=Post.query.get(random.randint(1, Post.query.count()))
		)
		db.session.add(comment)

		# 管理员的评论
		comment = Comment(
			author='刘知安',
			email='929910266@qq.com',
			site='https://github.com/LiUzHiAn',
			body=fake.sentence(),
			timestamp=fake.date_time_this_year(),
			from_admin=True,
			reviewed=True,
			post=Post.query.get(random.randint(1, Post.query.count()))
		)
		db.session.add(comment)
	db.session.commit()

	# 50条追评
	for i in range(salt):
		comment = Comment(
			author=fake.name(),
			email=fake.email(),
			site=fake.url(),
			body=fake.sentence(),
			timestamp=fake.date_time_this_year(),
			reviewed=True,
			replied=Comment.query.get(random.randint(1, Comment.query.count())),
			post=Post.query.get(random.randint(1, Post.query.count()))
		)
		db.session.add(comment)
	db.session.commit()

