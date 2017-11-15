#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time,datetime,traceback
import pickle,logging,re,configparser
import requests
from .sp_base import basespider
from .items import TweetsItem, InformationItem
from .weibo_parser import *
from .cookies import getCookie

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
		except Exception as e: logging("load spConfig fail")
		
		self.data_path=self.socialRoot+self.config['data_path']
		self.COOKIE_FILE=self.data_path+self.config['COOKIE_FILE']
		self.friends_file=self.data_path+self.config['friends_file']
		
		#self.url_template_question="https://www.zhihu.com/question/%s"
		#self.url_template_answer="https://www.zhihu.com/question/%s/answer/%s"
		#self.url_template_article="https://zhuanlan.zhihu.com/p/%s"

	def prepare(self):
		if not os.path.isdir(self.data_path): os.makedirs(self.data_path)
		
		try:
			with open(self.friends_file,"rb") as f: self.name_map=pickle.load(f)
		except Exception as e:
			logging.warning("load friends failed")
			self.name_map=dict()
			
	def login(self):
		headers=eval(self.spConfig['headers'])
		self.session=requests.session()
		self.session.headers=headers
		"""
		if os.path.isfile(self.COOKIE_FILE):
			self.session.cookies=pickle.load(open(self.COOKIE_FILE,"rb"))
		else:
			new_cookies=getCookie(self.spConfig['username'],self.spConfig['password'])
			if new_cookies:
				self.session.cookies=new_cookies
				pickle.dump(new_cookies,open(self.COOKIE_FILE,"wb"))
			else:
				logging.error("get new cookies failed, login failed")
		"""
		self.me=People("2218968230",self.session)
		if not self.me.info:
			logging.error("weibo login failed")
		#self.CheckUpdateCookies(self.session)
	
	def CheckUpdateCookies(self,session):
		me=People("2218968230",session)
		if me.info: return True
		time.sleep(2)
		new_cookies=getCookie(self.spConfig['username'],self.spConfig['password'])
		if new_cookies:
			session.cookies=new_cookies
			me=People("2218968230",session)
			if me.info:
				logging.info("update new cookies sussess")
				return True
			else:
				logging.error("update new cookies sussess failed")
				return False
		else:
			logging.error("update new cookies sussess failed")
			return False
		
	
	def followings2name_map(self,me):
		for peo in me.followings: 
			self.name_map[peo[0]]=peo[1]
		with open(self.friends_file,"wb") as f: pickle.dump(self.name_map,f)

	def getActivities(self,userid,count=10,timeOldest=None,timeLatest=None):
		def transtime(timstr):
			lct=time.localtime()
			try:
				tim=time.strptime(timstr,"%Y-%m-%d %H:%M:%S")
				return tim
			except Exception as e:pass
			try:
				tim=time.strptime(timstr,"%m月%d日 %H:%M")
				timstr=timstr+time.strftime("+%Y",lct)
				tim=time.strptime(timstr,"%m月%d日 %H:%M+%Y")
				return tim
			except Exception as e:traceback.print_exc()
			try:
				tim=time.strptime(timstr,"今天 %H:%M")
				timstr=timstr+time.strftime("+%Y,%m,%d",lct)
				tim=time.strptime(timstr,"今天 %H:%M+%Y,%m,%d")
				return tim
			except Exception as e:pass
			try:
				deltamin=int(re.fullmatch("(\d{1,2})分钟前",timstr).group(1))
				tim=datetime.datetime.now()+datetime.timedelta(minutes=-deltamin)
				return time.localtime(time.mktime(tim.timetuple()))
			except Exception as e:pass
			try:
				deltasec=int(re.fullmatch("(\d{1,2})秒钟前",timstr).group(1))
				tim=datetime.datetime.now()+datetime.timedelta(seconds=-deltasec)
				return time.localtime(time.mktime(tim.timetuple()))
			except Exception as e:pass
			return time.localtime()
			
		def formsummary(pp,act):
			if 'Content' not in act:act['Content']=""
			if 'OriginContent' not in act:act['OriginContent']=""
			if 'TransFrom' not in act:act['TransFrom']=""
			
			if act['ActType']=="origin":
				return "%s 发表了微博 %s"%(pp.info['NickName'],act['Content'] if len(act['Content'])<30 else act['Content'][:27]+"...")
			elif act['ActType']=="trans":
				return "%s 转发了 %s 的微博 %s"%(pp.info['NickName'],act['TransFrom'],act['OriginContent'] if len(act['OriginContent'])<30 else act['OriginContent'][:27]+"...")
			else:
				return ""
		
		if isinstance(userid,int):userid=str(userid)
		backuserid=userid
		dtLatest=datetime.datetime(*timeLatest[0:6]) if timeLatest else None
		dtOldest=datetime.datetime(*timeOldest[0:6]) if timeOldest else None
		
		
		pp=People(userid,self.session)
		if not pp.info:
			if userid not in self.name_map:
				pass
				# try: self.followings2name_map(self.me)
				# except Exception as e: logging.error("followings2name_map failed "+str(e))
			if userid in self.name_map:
				userid=self.name_map[userid]
				pp=People(userid,self.session)
			if not pp.info:
				userid=self.screen_name2userid(userid)
				pp=People(userid,self.session)
				if not pp.info:
					logging.error("Can't find user "+backuserid+" or login failed")
					return []
					# logging.error("Can't find user "+backuserid+" or login failed, trying to get new cookies")
					# self.CheckUpdateCookies(self.session)
					# pp=People(userid,self.session)
					# if not pp.info:
						# logging.error("get new cookies failed")
						# return []
		
		activityList=[]
		
		cnt=0
		for act in pp.activities:
			try:
				entry={
					'username':pp.info['NickName'] if 'NickName' in pp.info else "",
					'avatar_url':pp.info['Avatar_url'] if 'Avatar_url' in pp.info else "",
					'headline':pp.info['BriefIntroduction'] if 'BriefIntroduction' in pp.info else "",
					'time':transtime(act['PubTime'] if 'PubTime' in act else ""),
					'actionType':act['ActType'] if 'ActType' in act else "",
					'summary':formsummary(pp,act),
					'targetText':act['Content'] if 'Content' in act else "",
					'topics':[],
					'source_url':"https://weibo.com/"+("u/" if re.fullmatch(r'\d+',pp.id) else "")+pp.id+"?is_all=1"
				}
				if 'ImageUrls' in act: entry['imgs']=act['ImageUrls']
				
				dt=datetime.datetime(*entry['time'][0:6])
				if dtLatest and dtLatest<dt:continue
				if dtOldest and dtOldest>dt:break
				activityList.append(entry)
				cnt+=1
				if cnt>=count:break
			except Exception as e:
				logging.error("getActivities of "+backuserid+" failed")
			
		return activityList
	
	def screen_name2userid(self,screen_name):
		url='https://api.weibo.com/2/users/show.json'
		params={'screen_name':screen_name,'access_token':self.spConfig['access_token']}
		r=requests.get(url,params=params)
		if r.status_code!=200: return None
		else: 
			self.name_map[screen_name]=str(r.json()['id'])
			with open(self.friends_file,"wb") as f: pickle.dump(self.name_map,f)
			return str(r.json()['id'])

class People(object):
	def __init__(self,id=None,session=None):
		self.id=id
		self._id=id
		self.session=session
		
		self.url_template_activity="https://weibo.cn/u/%s"
		self.url_template_userinfo="https://weibo.cn/%s/info"
		self.url_template_following="https://weibo.cn/%s/follow"
		self.url_template_follower="https://weibo.cn/%s/fans"
		
		self._Info=None
	
	@property
	def id(self):
		return self._id
	
	@id.setter
	def id(self,value):
		if isinstance(value,int):value=str(value)
		if value:
			self._id=value
			if re.fullmatch(r'\d+',value):
				self.url_template_activity="https://weibo.cn/u/%s"
			else:
				self.url_template_activity="https://weibo.cn/%s"
	
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
	def info(self):
		if not self.id or not self.session: return None
		if self._Info: return self._Info
		
		r=self.session.get(self.url_userinfo)
		if r.status_code==200:
			self._Info=parse_information(r,self.session)
			return self._Info
		else: return None
	
	@property
	def activities(self):
		if not self.id or not self.session: return None
		
		r=self.session.get(self.url_activity)
		if r.status_code==200: return parse_tweets(r,self.session)
		else: return None

	@property
	def followings(self):
		if not self.id or not self.session: return None
		
		r=self.session.get(self.url_following)
		if r.status_code==200: return parse_followings(r,self.session)
		else: return None

	@property
	def followers(self):
		if not self.id or not self.session: return None
		
		r=self.session.get(self.url_follower)
		if r.status_code==200: return parse_followers(r,self.session)
		else: return None

if __name__=="__main__":
	test_weibo=weibospider()
	acts=test_weibo.getActivities('三星GALAXY盖乐世',5)
	print("\n".join(map(str,acts)))
