# -*- coding: utf-8 -*-
"""
    @Author  : LiuZhian
    @Time    : 2019/3/29 0029 下午 12:30
    @Comment : 
"""

from flask import Blueprint, render_template, current_app, request, flash, redirect, url_for, abort, make_response
from flaskblog.models import Post, Category, Comment
from flaskblog.forms import AdminCommentForm, CommentForm
from flaskblog.extensions import db
from flaskblog.emails import send_new_reply_email, send_new_comment_email
from flaskblog.utils import redirect_back
from flask_login import current_user

blog_bp = Blueprint("my_blog", __name__)


@blog_bp.route("/", defaults={"page": 1})
@blog_bp.route("/page/<int:page>")
def index(page):
	post_per_page = current_app.config["BLOG_POST_PER_PAGE"]
	# flask-SQLAlchemy中，查询返回结果可生成分页对象 https://baagee.vip/index/article/id/63.html
	pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=post_per_page)
	# 该分页中的所有文章
	posts = pagination.items

	categories = Category.query.all()

	return render_template("blog/index.html", pagination=pagination, posts=posts, categories=categories)


@blog_bp.route("/about")
def about():
	return render_template("blog/about.html")


# 显示某分类下对应的所有文章
@blog_bp.route("/category/<int:category_id>")
def show_category(category_id):
	category = Category.query.get_or_404(category_id)
	page = request.args.get("page", 1, type=int)
	post_per_page = current_app.config["BLOG_POST_PER_PAGE"]
	# 该类别下对应的文章
	pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page, per_page=post_per_page)
	posts = pagination.items

	return render_template("blog/category.html", category=category, pagination=pagination, posts=posts)


# 显示某篇文章的具体内容
@blog_bp.route("/post/<int:post_id>", methods=['GET', 'POST'])
def show_post(post_id):
	post = Post.query.get_or_404(post_id)
	page = request.args.get("page", 1, type=int)
	comment_per_page = current_app.config["BLOG_COMMENT_PER_PAGE"]
	# 得到该文章的对应评论的第一页(没通过审核的评论不显示)
	pagination = Comment.query.with_parent(post).filter_by(reviewed=True) \
		.order_by(Comment.timestamp.asc()).paginate(page, per_page=comment_per_page)
	comments = pagination.items

	if current_user.is_authenticated:  # 用户已登录,则用管路员评论表单
		form = AdminCommentForm()
		form.author.data = current_user.name
		form.email.data = current_app.config["BLOG_EMAIL"]
		form.site.data = url_for(".index")
		from_admin = True  # 管理员评论默认通过审核
		reviewed = True

	else:
		form = CommentForm()
		from_admin = False
		reviewed = False

	# 提交评论或者回复表单后
	if form.validate_on_submit():
		author = form.author.data
		email = form.email.data
		site = form.site.data
		body = form.body.data

		comment = Comment(
			author=author,
			email=email,
			site=site,
			body=body,
			from_admin=from_admin,
			reviewed=reviewed,
			post=post
		)
		# 如果URL中reply参数存在，则说明是回复
		# 被回复的评论的id（这里可以是访客回复管理员消息，也可以是管理员回复游客消息）
		replied_id = request.args.get("reply")
		if replied_id:
			replied_comment = Comment.query.get_or_404(replied_id)
			comment.replied = replied_comment
			send_new_reply_email(replied_comment)
		db.session.add(comment)
		db.session.commit()

		# 不同身份用户评论后，页面闪现出的提示消息也略有不同
		if current_user.is_authenticated:  # 管理员回复就免去了向自己发送邮件的过程
			flash('成功回复！', 'success')
		else:
			flash('感谢你的回复，管理员审核后将被发布！', 'info')
			# 当有游客对某篇文章进行评论/回复时，通知管理员审核
			send_new_comment_email(post)
		return redirect(url_for(".show_post", post_id=post_id))

	return render_template("blog/post.html", post=post, pagination=pagination, form=form, comments=comments)


# 回复某条评论
@blog_bp.route("/reply/comment/<int:comment_id>")
def reply_comment(comment_id):
	comment = Comment.query.get_or_404(comment_id)
	# 如果该评论对应的文章不可评论的
	if not comment.post.can_comment:
		flash("该文章的评论功能已被关闭！", "warning")
		return redirect(url_for(".show_post", post_id=comment.post.post_id))

	return redirect(
		url_for(".show_post", post_id=comment.post_id, reply=comment_id, author=comment.author) + "#comment-form")


@blog_bp.route("/change_theme/<theme_name>")
def change_theme(theme_name):
	if theme_name not in current_app.config["BLOG_THEMES"].keys():
		abort(404)

	# 回到主页
	rsps = make_response(redirect_back())
	rsps.set_cookie("theme", theme_name, max_age=24 * 60 * 60)
	return rsps
