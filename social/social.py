#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .sp_zhihu import zhihuspider
from .sp_weibo import weibospider

class social(object):
	def __init__(self):
		self.allSpider={
			'zhihu':zhihuspider(),
			'weibo':weibospider()
		}
	
	def getActivities(self,userid,socialPlatform,count,timeOldest=None,timeLatest=None):
		"""
		userid:用户唯一标识符
		socialPlatform:平台名称
			=======	=========
			平台	platform
			=======	=========
			知乎	zhihu
			=======	=========
		count:获取的动态条数，优先于时间限制
		timeOldest(None):最老时间(包含)，None默认不限制，time就是普通time struct类
		timeLatest(None):最新时间(包含)，None默认不限制
		
		RETURN:dict
			=============	===============
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
		
if __name__=="__main__":
	testsocial=social()
	acts=testsocial.getActivities('fake_fan','weibo',4)
	print("\n".join(map(str,acts)))