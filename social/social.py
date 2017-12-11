#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .sp_zhihu import zhihuspider
from .sp_weibo import weibospider
from .sp_github import githubspider

class social(object):
	def __init__(self):
		self.allSpider={
			'zhihu':zhihuspider(),
			'weibo':weibospider(),
			'github':githubspider()
		}
	
	def getActivities(self,userid,socialPlatform,count,timeOldest=None,timeLatest=None):
		"""
		userid:用户唯一标识符
		socialPlatform:平台名称
			=======	=========
			平台	platform
			=======	=========
			知乎	zhihu
			微博	weibo
			github	github
			=======	=========
		count:获取的动态条数，优先于时间限制
		timeOldest(None):最老时间(包含)，None默认不限制，time就是普通time struct类
		timeLatest(None):最新时间(包含)，None默认不限制
		
		RETURN:dict
			=============	===============
			'mid'			微博条目id
			'username'		用户名
			'avatar_url'	用户头像url
			'headline'		用户头像旁边那行字
			'time'			动态发布时间，time类
			'actionType'	动作类型，详见sp_zhihu.py
			'summary'		动态概要
			'targetText'	目标文本
			'imgs'			图片url列表
			'topics'		话题列表
			'source_url'	原文链接
			=============	===============
			建议使用前检查一下key是否存在
			
		SAMPLE Useage
		===============begin====================
			import social
			import time

			cli=social.social()

			latest=time.strptime("2017-11-14 12:12:00","%Y-%m-%d %H:%M:%S")
			oldest=time.strptime("2017-11-10 08:23:00","%Y-%m-%d %H:%M:%S")
			print(cli.getActivities('kugwzk','weibo',10,oldest,latest))
		===============end=======================
		"""
		return self.allSpider[socialPlatform].getActivities(userid,count,timeOldest,timeLatest)
	
	def getFollowings(self,userid,socialPlatform,count):
		"""
		返回关注列表的生成器
		userid:用户唯一标识符
		socialPlatform:平台名称
		count:数量
			=======	=========
			平台	platform
			=======	=========
			微博	weibo
			=======	=========
		RETURN 用户名字符串
		
		SAMPLE Useage
		===============begin====================
			import social

			cli=social.social()

			for p in cli.getFollowings('fake_fan','weibo',80):
				print(p)
		===============end=======================
		"""
		if socialPlatform!="weibo":return []
		return self.allSpider[socialPlatform].getFollowings(userid,count)
		
	def getFollowers(self,userid,socialPlatform,count):
		"""
		返回粉丝列表的生成器
		userid:用户唯一标识符
		socialPlatform:平台名称
		count:数量
			=======	=========
			平台	platform
			=======	=========
			微博	weibo
			=======	=========
		RETURN 用户名字符串
		
		SAMPLE Useage
		===============begin====================
			import social

			cli=social.social()

			for p in cli.getFollowers('fake_fan','weibo',80):
				print(p)
		===============end=======================
		"""
		if socialPlatform!="weibo":return []
		return self.allSpider[socialPlatform].getFollowers(userid,count)
	
	def putComment(self,socialPlatform,comment,mid,token):
		"""
		对某一微博进行评论
		socialPlatform:平台名称
		comment:评论
		mid:微博mid
		token:AccessToken
			=======	=========
			平台	platform
			=======	=========
			微博	weibo
			=======	=========

		RETURN True/False
		
		SAMPLE Useage
		===============begin====================
			import social

			cli=social.social()

			cli.putComment('weibo','郑爹强啊',mid,AccessToken)
		===============end=======================
		"""
		if socialPlatform!="weibo":return False
		return self.allSpider[socialPlatform].putComment(comment,mid,token)
		
	def checkToken(self,socialPlatform,token):
		"""
		检查Token是否有效
		socialPlatform:平台名称
		token:AccessToken
			=======	=========
			平台	platform
			=======	=========
			微博	weibo
			=======	=========

		RETURN True/False
		
		SAMPLE Useage
		===============begin====================
			import social

			cli=social.social()

			cli.checkToken('weibo',AccessToken)
		===============end=======================
		"""
		if socialPlatform!="weibo":return False
		return self.allSpider[socialPlatform].checkToken(token)
		
	def getAuthorizationUrl(self,socialPlatform):
		"""
		生成授权页面链接
		socialPlatform:平台名称
			=======	=========
			平台	platform
			=======	=========
			微博	weibo
			=======	=========

		RETURN 字符串,链接Url
		
		SAMPLE Useage
		===============begin====================
			import social

			cli=social.social()

			Url=cli.getAuthorizationUrl('weibo')
		===============end=======================
		"""
		if socialPlatform!="weibo":return None
		return self.allSpider[socialPlatform].getAuthorizationUrl()
		
	def getAccessToken(self,socialPlatform,code):
		"""
		获得用户的Token
		socialPlatform:平台名称
		code:授权页面重定向后附带的参数code
			=======	=========
			平台	platform
			=======	=========
			微博	weibo
			=======	=========

		RETURN True/False
		
		SAMPLE Useage
		===============begin====================
			import social

			cli=social.social()
			
			AccessToken=cli.getAccessToken('weibo',code)
		===============end=======================
		"""
		if socialPlatform!="weibo":return False
		return self.allSpider[socialPlatform].getAccessToken(code)
		
if __name__=="__main__":
	testsocial=social()
	acts=testsocial.getActivities('fake_fan','weibo',4)
	print("\n".join(map(str,acts)))