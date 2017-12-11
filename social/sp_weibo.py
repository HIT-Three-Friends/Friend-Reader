#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time,datetime,traceback
import pickle,logging,re,configparser
import requests
from .sp_base import basespider
from .items import TweetsItem, InformationItem
from .weibo_parserpc import *
from .cookies import getCookie

strangecode="100505"

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


	def prepare(self):
		if not os.path.isdir(self.data_path): os.makedirs(self.data_path)
		
		try:
			with open(self.friends_file,"rb") as f: self.name_map=pickle.load(f)
		except Exception as e:
			logging.warning("load friends failed")
			traceback.print_exc()
			print(e)
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
				tim=time.strptime(timstr,"%Y-%m-%d %H:%M")
				return tim
			except Exception as e:pass
			return time.localtime()
			
		def formsummary(pp,act):
			if 'Content' not in act:act['Content']=""
			if 'OriginContent' not in act:act['OriginContent']=""
			if 'TransFrom' not in act:act['TransFrom']=""
			
			if act['ActType']=="origin":
				return "%s 发表了微博 | %s"%(pp.info['NickName'],act['Content'])   # if len(act['Content'])<30 else act['Content'][:27]+"...")
			elif act['ActType']=="trans":
				return "%s 转发了 %s 的微博 | %s//@%s:%s"%(pp.info['NickName'],act['TransFrom'],act['Content'],act['TransFrom'],act['OriginContent'])   #if len(act['OriginContent'])<30 else act['OriginContent'][:27]+"...")
			elif act['ActType']=="like":
				return "%s 赞了 %s 的微博 | %s"%(pp.info['NickName'],act['TransFrom'],act['OriginContent'])   #if len(act['OriginContent'])<30 else act['OriginContent'][:27]+"...")
			else:
				return ""
		
		if isinstance(userid,int):userid=str(userid)
		backuserid=userid
		if not re.fullmatch(r'\d+',userid):userid=self.screen_name2userid(userid)
		
		dtLatest=datetime.datetime(*timeLatest[0:6]) if timeLatest else None
		dtOldest=datetime.datetime(*timeOldest[0:6]) if timeOldest else None
		
		
		pp=People(userid,self.session)
		
		print(pp.info)
		
		if not pp.info:return []
		
		activityList=[]
		
		cnt=0
		for act in pp.activities:
			try:
				#print(act['PubTime'],act)
				entry={
					'mid':act['mid'] if 'mid' in act else "",
					'username':pp.info['NickName'] if 'NickName' in pp.info else "",
					'avatar_url':pp.info['Avatar_url'] if 'Avatar_url' in pp.info else "",
					'headline':pp.info['BriefIntroduction'] if 'BriefIntroduction' in pp.info else "",
					'time':transtime(act['PubTime'] if 'PubTime' in act else ""),
					'actionType':act['ActType'] if 'ActType' in act else "",
					'summary':formsummary(pp,act),
					'targetText':act['Content'] if 'Content' in act else (act['OriginContent'] if 'OriginContent' in act else ""),
					'topics':[],
					'source_url':pp.url_activity
				}
				if 'ImageUrls' in act: entry['imgs']=act['ImageUrls']
				elif act['ActType']=="like" and 'OriginImageUrls' in act: entry['imgs']=act['OriginImageUrls']
				if 'Comments' in act:
					entry['comments']=act['Comments']
				
				
				dt=datetime.datetime(*entry['time'][0:6])
				if dtLatest and dtLatest<dt:continue
				if dtOldest and dtOldest>dt:break
				activityList.append(entry)
				cnt+=1
				if cnt>=count:break
			except Exception as e:
				logging.error("getActivities of "+backuserid+" failed")
			
		return activityList
	
	def getFollowings(self,userid,count=10):
		if isinstance(userid,int):userid=str(userid)
		backuserid=userid
		if not re.fullmatch(r'\d+',userid):userid=self.screen_name2userid(userid)

		pp=People(userid,self.session)
		
		if not pp.info:return []
		
		cnt=0
		for p in pp.followings:
			yield p[0]
			cnt+=1
			if cnt>=count:break

	def getFollowers(self,userid,count=10):
		if isinstance(userid,int):userid=str(userid)
		backuserid=userid
		if not re.fullmatch(r'\d+',userid):userid=self.screen_name2userid(userid)

		pp=People(userid,self.session)
		
		if not pp.info:return []
		
		cnt=0
		for p in pp.followers:
			yield p[0]
			cnt+=1
			if cnt>=count:break
		
	def putComment(self,comment,mid,token):
		url="https://api.weibo.com/2/comments/create.json"
		payload={'access_token':token,'comment':comment,'id':int(mid)}
		r=requests.post(url,data=payload)
		
		if r.status_code!=200:
			logging.error("putComment status_code=%d"%r.status_code)
			print(r.json())
			return False
		js=r.json()
		if 'created_at' not in js:
			return False
			print(js)
		return True
		
	def checkToken(self,token):
		url="https://api.weibo.com/oauth2/get_token_info"
		payload={'access_token':token}
		r=requests.post(url,data=payload)
		
		js=r.json()
		if r.status_code!=200 or 'error' in js:
			logging.error("putComment status_code=%d"%r.status_code)
			print(js)
			return False
		
		expire_in=int(js['expire_in'])
		if expire_in<=0:return False
		else:return True
	
	def getAuthorizationUrl(self):
		url="https://api.weibo.com/oauth2/authorize"
		payload={'client_id':self.spConfig['APP_KEY'],'response_type':'code','redirect_uri':self.spConfig['CALLBACK_URL']}
		url=url+"?"+"&".join(map(lambda x:x[0]+"="+x[1],payload.items()))
		return url
	
	def getAccessToken(self,code):
		url="https://api.weibo.com/oauth2/access_token"
		payload={'client_id':self.spConfig['APP_KEY'],'client_secret':self.spConfig['APP_SECRET'],'grant_type':'authorization_code','code':code,'redirect_uri':self.spConfig['CALLBACK_URL']}
		r=requests.post(url,data=payload)
		js=r.json()
		if "access_token" in js:
			return js['access_token']
		else:
			print(js)
			return False
	
	def screen_name2userid(self,screen_name):
		if screen_name in self.name_map:return self.name_map[screen_name]
		
		url='https://api.weibo.com/2/users/show.json'
		params={'screen_name':screen_name,'access_token':self.spConfig['access_token']}
		r=requests.get(url,params=params)
		if r.status_code!=200:
			print(r.json())
			return None
		else: 
			self.name_map[screen_name]=str(r.json()['id'])
			with open(self.friends_file,"wb") as f: pickle.dump(self.name_map,f)
			return str(r.json()['id'])

class People(object):
	def __init__(self,id=None,session=None):
		self.id=id
		self._id=id
		self.session=session
		
		self.url_template_activity="https://weibo.com/p/100505%s/home?profile_ftype=1&is_all=1"
		self.url_template_userinfo="https://weibo.com/p/"+strangecode+"%s/info"
		self.url_template_following="https://weibo.com/p/"+strangecode+"%s/follow"
		self.url_template_follower="https://weibo.com/p/"+strangecode+"%s/follow?relate=fans"
		
		self._Info=None
	
	@property
	def id(self):
		return self._id
	
	@id.setter
	def id(self,value):
		if isinstance(value,int):value=str(value)
		if value:
			self._id=value
	
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
		if r.status_code==200: 
			#with open("AkaisoraTestActPage.html","wb") as f:f.write(r.content)
			return parse_tweets(r,self.session)
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
