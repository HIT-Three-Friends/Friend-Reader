#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,time
import pickle,logging,re,configparser
import requests
from .sp_base import basespider
from .items import TweetsItem, InformationItem, RelationshipsItem
import .weibo_parser

class weibospider(basespider):
	def __init__(self):
		super().loadConfig()
		super().prepare()
		self.loadConfig()
		self.prepare()
		self.login()

	def loadConfig(self):
		self.config=self.allConfig['weibo']
		try: self.spConfig=self.spiderConfig['weibo']
		except Exception as e: pass
		
		self.data_path=self.socialRoot+self.config['data_path']
		self.TOKEN_FILE=self.data_path+self.config['TOKEN_FILE']
		self.friends_file=self.data_path+self.config['friends_file']
		
		#self.url_template_question="https://www.zhihu.com/question/%s"
		#self.url_template_answer="https://www.zhihu.com/question/%s/answer/%s"
		#self.url_template_article="https://zhuanlan.zhihu.com/p/%s"

	def prepare(self):
		if not os.path.isdir(self.data_path): os.makedirs(self.data_path)
		
		if os.path.isfile(self.friends_file):
			with open(self.friends_file,"rb") as f: self.name_map=pickle.load(f)
		else:
			self.name_map=dict()
			
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
		def getTargetText_Topic(target,actType):
			if isinstance(target,zhihu_oauth.Answer):
				return (target.content,target.question.topics,self.url_template_answer%(target.question.id,target.id))
			elif isinstance(target,zhihu_oauth.Question):
				return (target.title,target.topics,self.url_template_question%(target.id))
			elif isinstance(target,zhihu_oauth.Article):
				return (target.excerpt,[],self.url_template_article%(target.id))
			else:
				return (None,[],"")
		
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
			#print(entry['source_url'])
			imglist=re.findall(r'(?<=<img src=")(.*?)(?=")',entry['targetText'])
			if isinstance(act.target,zhihu_oauth.Article):imglist[0:0]=[act.target.image_url]
			if imglist: entry['imgs']=imglist

			activityList.append(entry)
			
			cnt+=1
			if cnt>=count:break
			
		return activityList
	
	def screen_name2userid(self,screen_name):
		url='https://api.weibo.com/2/users/show.json'
		params={'screen_name':screen_name,'access_token':self.spConfig['access_token']}
		r=requests.get(url,params=params)
		if r.status_code!=200: return None
		else: return str(r.json()['id'])

class People(Object):
	def __init__(self,id=None,session=None):
		self.id=id
		self.session=session
		self.url_template_activity="https://weibo.cn/u/%s"
		self.url_template_userinfo="https://weibo.cn/%s/info"
		self.url_template_following="https://weibo.cn/%s/follow"
		self.url_template_follower="https://weibo.cn/%s/fans"
		
		self.info=None
		self.activity=None
		self.following=None
		self.follower=None
		
	@property
	def url_activity(self):
		return self.url_template_activity%(self.id) if self.id else None
		
	@property
	def url_userinfo(self):
		return self.url_template_userinfo%(self.id) if self.id else None	
	
	@property
	def url_following(self):
		return self.url_template_following%(self.id) if self.id else None
	
	@property
	def url_follower(self):
		return self.url_template_follower%(self.id) if self.id else None
	
	@property
	def userInfo(self):
		if not self.id or not self.session: return None
		if self.info: return self.info
		
		r=self.session.get(self.url_userinfo)
		if r.status_code==200: self.info=weibo_parser.parse_information(r,self.session)
		return self.info
	
	@property
	def userActivity(self):
		if not self.id or not self.session: return None
		
		r=self.session.get(self.url_activity)
		if r.status_code==200: self.activity=weibo_parser.parse_tweets(r,self.session)
		return self.activity

	@property
	def userFollowing(self):
		if not self.id or not self.session: return None
		if self.following: return self.following
		
		r=self.session.get(self.url_following)
		if r.status_code==200: self.following=weibo_parser.parse_followings(r,self.session)
		return self.following

	@property
	def userFollower(self):
		if not self.id or not self.session: return None
		if self.follower: return self.follower
		
		r=self.session.get(self.url_follower)
		if r.status_code==200: self.follower=weibo_parser.parse_followers(r,self.session)
		return self.follower

if __name__=="__main__":
	test_weibo=weibospider()
	acts=test_weibo.getActivities('fake_fan',5)
	print("\n".join(map(str,acts)))
