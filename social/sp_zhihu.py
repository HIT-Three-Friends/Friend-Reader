#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,time,datetime,traceback
import pickle,logging,re,configparser
import zhihu_oauth
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
		
		self.url_template_question="https://www.zhihu.com/question/%s"
		self.url_template_answer="https://www.zhihu.com/question/%s/answer/%s"
		self.url_template_article="https://zhuanlan.zhihu.com/p/%s"

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
			logging.error("login failed! Reason is "+self.me.over_reason)
			self.client.login_in_terminal()
			self.client.save_token(self.TOKEN_FILE)	
		
	def followings2name_map(self,me):
		for peo in me.followings: self.name_map[peo.name]=peo.id
		with open(self.friends_file,"wb") as f: pickle.dump(self.name_map,f)

	def getActivities(self,userid,count=10,timeOldest=None,timeLatest=None):
		"""
		关于actionType
			CREATE_ANSWER
			CREATE_ARTICLE
			CREATE_QUESTION
			FOLLOW_QUESTION
			VOTEUP_ANSWER
		"""
		def getTargetText_Topic(target,actType):
			if isinstance(target,zhihu_oauth.Answer):
				return (target.content,target.question.topics,self.url_template_answer%(target.question.id,target.id))
			elif isinstance(target,zhihu_oauth.Question):
				print(target.detail)
				return (target.detail,target.topics,self.url_template_question%(target.id))
			elif isinstance(target,zhihu_oauth.Article):
				return (target.content,[],self.url_template_article%(target.id))
			else:
				return ("",[],"")
		
		if isinstance(userid,int):userid=str(userid)
		backuserid=userid
		dtLatest=datetime.datetime(*timeLatest[0:6]) if timeLatest else None
		dtOldest=datetime.datetime(*timeOldest[0:6]) if timeOldest else None
		
		pp=self.client.people(userid)
		if pp.over:
			if userid not in self.name_map:
				try: self.followings2name_map(self.me)
				except Exception as e: logging.error(str(e))
			if userid in self.name_map:
				userid=self.name_map[userid]
				pp=self.client.people(userid)
			if pp.over:return []
		
		activityList=[]
		
		cnt=0
		for act in pp.activities:
			try:
				targetInfo=getTargetText_Topic(act.target,act.type)
				entry={
					'username':pp.name,
					'avatar_url':pp.avatar_url,
					'headline':pp.headline,
					'time':time.localtime(act.created_time),
					'actionType':act.type,
					'summary':act2str(act),
					'targetText':targetInfo[0],
					'topics':list(map(lambda topic:topic.name,targetInfo[1])),
					'source_url':targetInfo[2]
				}
				
				imglist=re.findall(r'(?<=<img src=")(.*?)(?=")',entry['targetText'])
				if isinstance(act.target,zhihu_oauth.Article) and act.target.image_url:imglist[0:0]=[act.target.image_url]
				if imglist: entry['imgs']=imglist

				dt=datetime.datetime(*entry['time'][0:6])
				if dtLatest and dtLatest<dt:continue
				if dtOldest and dtOldest>dt:break
				activityList.append(entry)
				
				cnt+=1
				if cnt>=count:break
			except Exception as e:
				logging.error("getActivities of "+backuserid+" failed")
				traceback.print_exc()
			
		return activityList
	

if __name__=="__main__":
	test_zhihu=zhihuspider()
	acts=test_zhihu.getActivities('kugwzk',5)
	print("\n".join(map(str,acts)))

