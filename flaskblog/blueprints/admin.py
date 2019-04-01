# -*- coding: utf-8 -*-
"""
    @Author  : LiuZhian
    @Time    : 2019/3/29 0029 下午 12:00
    @Comment : 
"""

from flask import Blueprint, render_template, url_for, redirect, request, current_app, flash
from flask_login import login_required
from flaskblog.forms import SettingForm, PostForm, CategoryForm
from flaskblog.utils import redirect_back
from flaskblog.models import Post, Category, Comment, Admin
from flaskblog.extensions import db

admin_bp = Blueprint("my_admin", __name__)


# 博客设置路由(主要包括博主名称、博客标题、博客副标题等信息)
@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
	form = SettingForm()
	admin = Admin.query.get(1)

	if form.validate_on_submit():
		admin.name = form.name.data
		admin.blog_title = form.blog_title.data
		admin.blog_sub_title = form.blog_sub_title.data
		admin.about = form.about.data
		db.session.commit()
		flash('修改博客信息成功!', 'success')
		return redirect(url_for('.settings'))

	form.name.data = admin.name
	form.blog_title.data = admin.blog_title
	form.blog_sub_title.data = admin.blog_sub_title
	form.about.data = admin.about
	return render_template('admin/settings.html', form=form)


# 管理文章路由
@admin_bp.route('/post/manage')
@login_required
def manage_post():
	page = request.args.get("page", 1, type=int)
	post_per_page = current_app.config["BLOG_POST_PER_PAGE"]

	pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
		page=page, per_page=post_per_page
	)
	posts = pagination.items
	return render_template('admin/manage_post.html', page=page, pagination=pagination, posts=posts)


# 编辑文章路由
@admin_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
	form = PostForm()
	post = Post.query.get_or_404(post_id)  # 先从数据库拿到post对象
	if form.validate_on_submit():
		post.title = form.title.data
		post.body = form.body.data
		post.category = Category.query.get(form.category.data)
		db.session.commit()  # 注意！flask SQLAlchemy修改数据时不需要添加db.session.add()语句
		flash('更新文章成功！', 'success')
		# 编辑完后回到显示该文章内容页面
		return redirect(url_for('my_blog.show_post', post_id=post.id))

	form.title.data = post.title
	form.body.data = post.body
	form.category.data = post.category_id
	return render_template('admin/edit_post.html', form=form)


# 删除文章路由
@admin_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	db.session.delete(post)
	db.session.commit()
	flash('删除文章成功！', 'success')
	return redirect_back()


# 新建文章路由
@admin_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
	form = PostForm()
	if form.validate_on_submit():
		title = form.title.data
		body = form.body.data
		category = Category.query.get(form.category.data)
		post = Post(title=title, body=body, category=category)
		db.session.add(post)
		db.session.commit()  # 注意！flask SQLAlchemy修改数据时不需要添加db.session.add()语句
		flash('发表文章成功！', 'success')
		# 编辑完后回到显示该文章内容页面
		return redirect(url_for('my_blog.show_post', post_id=post.id))

	return render_template('admin/new_post.html', form=form)


# 设置某篇文章是否可以评论路由
@admin_bp.route('/post/<int:post_id>/set-comment', methods=['POST'])
@login_required
def set_comment(post_id):
	post = Post.query.get_or_404(post_id)
	if post.can_comment:  # 如果可以评论就设置为禁止评论
		post.can_comment = False
		flash("该文章评论功能已被关闭！", "info")
	else:
		post.can_comment = True
		flash("该文章评论功能已被打开！", "info")
	db.session.commit()
	return redirect_back(url_for("my_blog.show_post", post_id=post_id))


@admin_bp.route('/comment/manage')
@login_required
def manage_comment():
	# 从查询字符串获取过滤规则
	# 有'all', 'unreviewed', 'admin'三种情况
	filter_rule = request.args.get('filter', 'all')
	page = request.args.get('page', 1, type=int)
	per_page = current_app.config['BLOG_COMMENT_PER_PAGE']
	if filter_rule == 'unread':
		filtered_comments = Comment.query.filter_by(reviewed=False)
	elif filter_rule == 'admin':
		filtered_comments = Comment.query.filter_by(from_admin=True)
	else:
		filtered_comments = Comment.query

	pagination = filtered_comments.order_by(Comment.timestamp.desc()).paginate(page, per_page=per_page)
	comments = pagination.items
	return render_template('admin/manage_comment.html', comments=comments, pagination=pagination)


# 将某条评论通过审核路由
@admin_bp.route('/comment/<int:comment_id>/approve', methods=['POST'])
@login_required
def approve_comment(comment_id):
	comment = Comment.query.get_or_404(comment_id)
	comment.reviewed = True
	db.session.commit()
	flash("来自%s的评论审核通过！" % comment.author, "success")
	return redirect_back()


# 删除评论路由
@admin_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
	comment = Comment.query.get_or_404(comment_id)
	db.session.delete(comment)
	db.session.commit()
	flash('删除评论成功！', 'success')
	return redirect_back()


# 管理分类路由
@admin_bp.route('/category/manage')
@login_required
def manage_category():
	categories = Category.query.all()
	return render_template('admin/manage_category.html', categories=categories)


@admin_bp.route('/category/new', methods=['GET', 'POST'])
@login_required
def new_category():
	form = CategoryForm()
	if form.validate_on_submit():
		name = form.name.data
		category = Category(name=name)
		db.session.add(category)
		db.session.commit()
		flash('新建分类成功!', 'success')
		return redirect(url_for('.manage_category'))
	return render_template('admin/new_category.html', form=form)


# 编辑某个类别
@admin_bp.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
	category = Category.query.get_or_404(category_id)
	form = CategoryForm()
	# 不能编辑默认分类
	if category.id == 1:
		flash("对不起，你不能编辑默认类别", "warning")
		return redirect(url_for("my_blog.index"))

	if form.validate_on_submit():
		category.name = form.name.data
		db.session.commit()
		flash("修改分类信息成功！", "success")
		return redirect(url_for(".manage_category"))

	form.name.data = category.name
	return render_template('admin/edit_category.html', form=form)


# 删除某个分类路由
@admin_bp.route('/category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
	category = Category.query.get_or_404(category_id)
	if category.id == 1:
		flash('不能删除默认分类！', 'warning')
		return redirect(url_for('my_blog.index'))
	category.delete()  # 这是一个自定义删除方法
	flash('删除分类%s成功！' % category.name, 'success')
	return redirect(url_for('.manage_category'))
