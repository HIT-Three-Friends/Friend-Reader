#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .sp_zhihu import zhihuspider

class social(object):
	def __init__(self):
		self.allSpider={
			'zhihu':zhihuspider()
		}
	
	def getActivities(self,userid,socialPlatform,count):
		"""
		userid:用户唯一标识符
		socialPlatform:平台名称
			=======	=========
			平台	platform
			=======	=========
			知乎	zhihu
			=======	=========
		count:获取的动态条数
		
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
			=============	===============
			建议使用前检查一下key是否存在
		"""
		return self.allSpider[socialPlatform].getActivities(userid,count)
		
if __name__=="__main__":
	testsocial=social()
	acts=testsocial.getActivities('kugwzk','zhihu',4)
	print("\n".join(map(str,acts)))