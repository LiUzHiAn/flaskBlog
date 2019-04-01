# -*- coding: utf-8 -*-
"""
    @Author  : LiuZhian
    @Time    : 2019/3/30 0030 下午 6:39
    @Comment : 用来发送邮件
"""
from threading import Thread
from flask import url_for, current_app
from flask_mail import Message
from flaskblog.extensions import mail


def _send_async_mail(app, msg):
	with app.app_context():
		mail.send(msg)


def send_email(subject, to, html):
	# 获取到当前的app对象
	app = current_app._get_current_object()
	msg = Message(subject=subject, recipients=[to], html=html)
	# 后台异步发送
	thr = Thread(target=_send_async_mail, args=[app, msg])
	thr.start()

	return thr


# 当某人对一篇文章评论时，邮件通知管理员
def send_new_comment_email(post):
	"""post参数为数据库中一个文章对象"""
	# #comments是页面锚点，设置post_url的目的是可以从邮件中快速转到评论区
	post_url = url_for("my_blog.show_post", post_id=post.id, _external=True) + "#comments"
	send_email(subject="new comment", to=current_app.config["BLOG_EMAIL"],
			   html='<p>文章<i>%s</i>有新评论了,点击以下链接查看具体内容:</p>'
					'<p><a href="%s">%s</a></P>'
					'<p><small style="color: #868e96">请不要回复此邮件.</small></p>'
					% (post.title, post_url, post_url))


# 当评论被回复时邮箱通知评论者
def send_new_reply_email(comment):
	"""comment参数为一条回复 """
	post_url = url_for('my_blog.show_post', post_id=comment.post_id, _external=True) + '#comments'
	send_email(subject='New reply', to=comment.email,
			   html='<p>您在文章“<i>%s</i>”下的评论有了新的回复,点击以下链接查看具体内容:</p>'
					'<p><a href="%s">%s</a></P>'
					'<p><small style="color: #868e96">请不要回复此邮件.</small></p>'
					% (comment.post.title, post_url, post_url))
