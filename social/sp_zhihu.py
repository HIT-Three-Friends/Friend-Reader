#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.0.1'
__author__ = 'Han Yue (1224067801@qq.com)'

import os,time
import pickle,logging,re,configparser
from zhihu_oauth import ZhihuClient,ActType
from zhihu_oauth.helpers import act2str

from .sp_base import basespider

class zhihuspider(basespider):
	def __init__(self):
		super().loadConfig()
		super().prepare()
		self.loadConfig()
		self.prepare()
		self.login()

	def loadConfig(self):
		self.config=self.allConfig['zhihu']
		
		self.data_path=self.socialRoot+self.config['data_path']
		self.TOKEN_FILE=self.data_path+self.config['TOKEN_FILE']
		self.friends_file=self.data_path+self.config['friends_file']

	def prepare(self):
		if not os.path.isdir(self.data_path): os.makedirs(self.data_path)
		
		if os.path.isfile(self.friends_file):
			with open(self.friends_file,"rb") as f: self.name_map=pickle.load(f)
		else:
			self.name_map=dict()
		
		self.client = ZhihuClient()
			
	def login(self):
		if os.path.isfile(self.TOKEN_FILE):
			self.client.load_token(self.TOKEN_FILE)
		else:
			self.client.login_in_terminal()
			self.client.save_token(self.TOKEN_FILE)
		
		self.me=self.client.me()
		if self.me.over:
			logging.error("you are baned! Reason is "+self.me.over_reason)
		
	def followings2name_map(self,me):
		for peo in me.followings: self.name_map[peo.name]=peo.id
		with open(self.friends_file,"wb") as f: pickle.dump(self.name_map,f)

	def getActivities(self,userid,count=20):
		"""
		关于actionType
			CREATE_ANSWER
			CREATE_ARTICLE
			CREATE_QUESTION
			FOLLOW_QUESTION
			VOTEUP_ANSWER
		"""
		def getTargetText(target,actType):
			ma={
				ActType.CREATE_ANSWER:'content',
				ActType.CREATE_ARTICLE:'title',
				ActType.CREATE_QUESTION:'title',
				ActType.FOLLOW_QUESTION:'title',
				ActType.VOTEUP_ANSWER:'content'
			}
			if actType in ma:
				return getattr(target,ma[actType])
			else:
				return ""
		
		pp=self.client.people(userid)
		if pp.over:
			if userid not in self.name_map:
				try: self.followings2name_map(me)
				except Exception as e: logging.error(str(e))
			if userid in self.name_map:
				userid=self.name_map[userid]
				pp=self.client.people(userid)
			if pp.over:return []
		
		activityList=[]
		
		cnt=0
		for act in pp.activities:
			entry={
				'username':pp.name,
				'avatar_url':pp.avatar_url,
				'headline':pp.headline,
				'time':time.localtime(act.created_time),
				'actionType':act.type,
				'summary':act2str(act),
				'targetText':getTargetText(act.target,act.type)
			}
			imglist=re.findall(r'(?<=<img src=")(.*?)(?=")',entry['targetText'])
			if imglist: entry['imgs']=imglist

			activityList.append(entry)
			
			cnt+=1
			if cnt>=count:break
			
		return activityList
	

if __name__=="__main__":
	test_zhihu=zhihuspider()
	acts=test_zhihu.getActivities('kugwzk',5)
	print("\n".join(map(str,acts)))

