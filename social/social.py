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
		"""
		return self.allSpider[socialPlatform].getActivities(userid,count)
		
if __name__=="__main__":
	testsocial=social()
	acts=testsocial.getActivities('kugwzk','zhihu',4)
	print("\n".join(map(str,acts)))