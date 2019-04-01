# -*- coding: utf-8 -*-
"""
    @Author  : LiuZhian
    @Time    : 2019/3/30 0030 下午 6:06
    @Comment : 辅助函数
"""
from urllib.parse import urlparse, urljoin
from flask import request, redirect, url_for


# 判断一个链接是否安全，排除开放重定向问题
def is_safe_url(target):
	# request.host_url只包括scheme和域名
	ref_url = urlparse(request.host_url)
	test_url = urlparse(urljoin(request.host_url, target))

	return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


# 重定向回上一个页面，默认为博客主页
def redirect_back(default="my_blog.index", **kwargs):
	for target in request.args.get("next"), request.referrer:
		if not target:
			continue
		if is_safe_url(target):
			return redirect(target)
	# 否则返回默认的博客主页
	return redirect(url_for(default, **kwargs))
