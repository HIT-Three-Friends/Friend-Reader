#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
	'username':pp.name			--ql_info,
	'avatar_url':pp.avatar_url	--ql_info,
	'headline':pp.headline,		---ql_info bio
	'time':time.localtime(act.created_time),	--ql_act acted_time
	'actionType':act.type,	--ql_act acttype ?
	'summary':act2str(act),	--generate summary like github
	'targetText':targetInfo[0],	--commit comment	if not commit let it ""
	'topics':list(map(lambda topic:topic.name,targetInfo[1])),	--[]
	'source_url':targetInfo[2]	--find url
	imglist=re.findall(r'(?<=<img src=")(.*?)(?=")',entry['targetText'])	--[]
"""

import os
import time,datetime,traceback
import pickle,logging,re,configparser,json
import requests
from .sp_base import basespider

class githubspider(basespider):
	def __init__(self):
		super().loadConfig()
		super().prepare()
		self.loadConfig()
		self.prepare()
		self.login()

	def loadConfig(self):
		self.config=self.allConfig['github']
		try: self.spConfig=self.spiderConfig['github']
		except Exception as e: logging("load spConfig fail")
		
		self.data_path=self.socialRoot+self.config['data_path']
		self.HEAD_FILE=self.data_path+self.config['HEAD_FILE']
		self.friends_file=self.data_path+self.config['friends_file']
		
		self.url_graphql="https://api.github.com/graphql"

	def prepare(self):
		if not os.path.isdir(self.data_path): os.makedirs(self.data_path)
		
		try:
			with open(self.friends_file,"rb") as f: self.name_map=pickle.load(f)
		except Exception as e:
			logging.warning("load friends failed")
			self.name_map=dict()
			
	def login(self):
		def getFucken():
			with open(self.HEAD_FILE,"rb") as f:
				for i in range(6,10):
					f.seek(-(1<<i),2)
					lines=f.readlines()
					if len(lines)>1: return lines[-1].decode()

		self.session=requests.session()
		self.session.headers['Authorization']='bearer %s'%getFucken()

		self.me=People("Akaisorani",self.session)
		if not self.me.info:
			logging.error("github login failed")


	def getActivities(self,userid,count=10,timeOldest=None,timeLatest=None):
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
		for pn in pp.starredRepos:print(pn)
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
		self.session=session
		self.url_graphql="https://api.github.com/graphql"
		
		self._Info=None
	
	@property
	def info(self):
		if not self.id or not self.session: return None
		if self._Info: return self._Info
		data={
			"query":self.QUERY_USER_INFO,
			"variables":
				{
					"login_name":self.id
				}

		}
		r=self.session.post(self.url_graphql,data=json.dumps(data))
		if r.status_code==200:
			result=r.json()
			if "errors" in result:
				logging.error(self.id+" : "+result['errors'])
				return None
			result=result['data']['user']
			print(result)
			self._Info=result
			return self._Info
		else: return None
	
	@property
	def activities(self):
		if not self.id or not self.session: return None
		
		r=self.session.get(self.url_activity)
		if r.status_code==200: return parse_tweets(r,self.session)
		else: return None
		
	@property
	def starredRepos(self):
		if not self.id or not self.session: return None
		
		data={
			"query":self.QUERY_STARREDREPOS1,
			"variables":
				{
					"login_name":self.id
				}
		}
		r=self.session.post(self.url_graphql,data=json.dumps(data))
		failtimes=0
		while failtimes<3:
			if r.status_code==200:
				result=r.json()
				result=result['data']
				for pp in result['user']['starredRepositories']['edges']:	
					last_cursor=pp['cursor']
					yield {'name':pp['node']['name'],'date':pp['starredAt'],'URL':pp['node']['url']}
				if not result['user']['starredRepositories']['pageInfo']['hasNextPage']:raise StopIteration
				data={
					"query":self.QUERY_STARREDREPOS2,
					"variables":
						{
							"login_name":self.id,
							"last_cursor":last_cursor
						}
				}
				r=self.session.post(self.url_graphql,data=json.dumps(data))
			else:
				if "errors" in result:
					logging.error(self.id+" : "+result['errors'])
					failtimes+=1

	@property
	def createdRepos(self):
		if not self.id or not self.session: return None
		
		data={
			"query":self.QUERY_CREATEDREPOS1,
			"variables":
				{
					"login_name":self.id
				}
		}
		r=self.session.post(self.url_graphql,data=json.dumps(data))
		failtimes=0
		while failtimes<3:
			if r.status_code==200:
				result=r.json()
				result=result['data']
				for pp in result['user']['repositories']['edges']:	
					last_cursor=pp['cursor']
					yield {'name':pp['node']['name'],'date':pp['node']['createdAt'],'URL':pp['node']['url']}
				if not result['user']['repositories']['pageInfo']['hasNextPage']:raise StopIteration
				data={
					"query":self.QUERY_CREATEDREPOS2,
					"variables":
						{
							"login_name":self.id,
							"last_cursor":last_cursor
						}
				}
				r=self.session.post(self.url_graphql,data=json.dumps(data))
			else:
				if "errors" in result:
					logging.error(self.id+" : "+result['errors'])
					failtimes+=1					

	@property
	def pushedRepos(self):
		if not self.id or not self.session: return None
		
		data={
			"query":self.QUERY_PUSHEDREPOS1,
			"variables":
				{
					"login_name":self.id
				}
		}
		r=self.session.post(self.url_graphql,data=json.dumps(data))
		failtimes=0
		while failtimes<3:
			if r.status_code==200:
				result=r.json()
				result=result['data']
				for pp in result['user']['repositories']['edges']:	
					last_cursor=pp['cursor']
					yield {'name':pp['node']['name'],'owner':pp['node']['owner']['login'],'date':pp['pushedAt']}
				if not result['user']['repositories']['pageInfo']['hasNextPage']:raise StopIteration
				data={
					"query":self.QUERY_PUSHEDREPOS2,
					"variables":
						{
							"login_name":self.id,
							"last_cursor":last_cursor
						}
				}
				r=self.session.post(self.url_graphql,data=json.dumps(data))
			else:
				if "errors" in result:
					logging.error(self.id+" : "+result['errors'])
					failtimes+=1					

	@property
	def repoCommits(self,name,owner):
		if not self.id or not self.session: return None
		
		data={
			"query":self.QUERY_COMMITS1,
			"variables":
				{
					"repo_name":name,
					"repo_owner":owner,
					"author_id":self.info['id']
				}
		}
		r=self.session.post(self.url_graphql,data=json.dumps(data))
		failtimes=0
		while failtimes<3:
			if r.status_code==200:
				result=r.json()
				result=result['data']
				for pp in result['repository']['ref']['target']['history']['edges']:	
					last_cursor=pp['cursor']
					yield {'messageHeadline':pp['node']['messageHeadline'],'message':pp['node']['message'],'date':pp['node']['committedDate'],'URL':pp['node']['commitUrl']}
				if not result['repository']['ref']['target']['history']['pageInfo']['hasNextPage']:raise StopIteration
				data={
					"query":self.QUERY_COMMITS2,
					"variables":
						{
							"repo_name":name,
							"repo_owner":owner,
							"author_id":self.info['id'],
							"last_cursor":last_cursor
						}
				}
				r=self.session.post(self.url_graphql,data=json.dumps(data))
			else:
				if "errors" in result:
					logging.error(self.id+" : "+result['errors'])
					failtimes+=1
					
	@property
	def Commits(self):
		def addRepos(lis,count):
			for repo in self.pushedRepos:
				lis.append({'commits':self.repoCommits(repo['name'],repo['owner']),'date':repo['date'],'visited':False})
				count-=1
				if count<=0: break			
	
		if not self.id or not self.session: return None
		
		
		lis=[]
		addRepos(lis,5)
		failtimes=0
		unvisted
		while failtimes<3:
			if not existunvis(lis):addRepos(lis,5)
			latestRepo=max(lis,lambda x:x['date'])
			try:
				commit=next(latestRepo['commits'])
				latestRepo['visited']=True
				latestRepo['date']=commit['date']
				yield commit
			except StopIteration as e:
				latestRepo['date']='0'
				continue
			except Exception as e:
				logging.error(self.id+" : "+"getCommit fail")
				failtimes+=1

					
	@property
	def followings(self):
		if not self.id or not self.session: return None
		
		data={
			"query":self.QUERY_FOLLOWINGS1,
			"variables":
				{
					"login_name":self.id
				}
		}
		r=self.session.post(self.url_graphql,data=json.dumps(data))
		failtimes=0
		while failtimes<3:
			if r.status_code==200:
				result=r.json()
				result=result['data']
				for pp in result['user']['following']['edges']:	
					last_cursor=pp['cursor']
					yield pp['node']['login']
				if not result['user']['following']['pageInfo']['hasNextPage']:raise StopIteration
				data={
					"query":self.QUERY_FOLLOWINGS2,
					"variables":
						{
							"login_name":self.id,
							"last_cursor":last_cursor
						}
				}
				r=self.session.post(self.url_graphql,data=json.dumps(data))
			else:
				if "errors" in result:
					logging.error(self.id+" : "+result['errors'])
					failtimes+=1			
				
				

	@property
	def followers(self):
		if not self.id or not self.session: return None
		
		data={
			"query":self.QUERY_FOLLOWERS1,
			"variables":
				{
					"login_name":self.id
				}
		}
		r=self.session.post(self.url_graphql,data=json.dumps(data))
		failtimes=0
		while failtimes<3:
			if r.status_code==200:
				result=r.json()
				result=result['data']
				for pp in result['user']['followers']['edges']:	
					last_cursor=pp['cursor']
					yield pp['node']['login']
				if not result['user']['followers']['pageInfo']['hasNextPage']:raise StopIteration
				data={
					"query":self.QUERY_FOLLOWERS2,
					"variables":
						{
							"login_name":self.id,
							"last_cursor":last_cursor
						}
				}
				r=self.session.post(self.url_graphql,data=json.dumps(data))
			else:
				if "errors" in result:
					logging.error(self.id+" : "+result['errors'])
					failtimes+=1		
	
	QUERY_USER_INFO="""	
	query($login_name:String!){
	  user(login:$login_name){
		id
		name
		avatarUrl
		bioHTML
	  }
	}
	"""
	
	QUERY_FOLLOWINGS1="""	
	query($login_name:String!){
	  user(login: $login_name) {
		following(first:20){
		  edges{
			node{
			  login
			}
			cursor
		  }
		  pageInfo{
			hasNextPage
		  }
		}
	  }
	}
	"""

	QUERY_FOLLOWINGS2="""	
	query($login_name:String!,$last_cursor:String!){
	  user(login: $login_name) {
		following(first:20,after:$last_cursor){
		  edges{
			node{
			  login
			}
			cursor
		  }
		  pageInfo{
			hasNextPage
		  }
		}
	  }
	}
	"""
	
	QUERY_FOLLOWERS1="""	
	query($login_name:String!){
	  user(login: $login_name) {
		followers(first:20){
		  edges{
			node{
			  login
			}
			cursor
		  }
		  pageInfo{
			hasNextPage
		  }
		}
	  }
	}
	"""

	QUERY_FOLLOWERS2="""	
	query($login_name:String!,$last_cursor:String!){
	  user(login: $login_name) {
		followers(first:20,after:$last_cursor){
		  edges{
			node{
			  login
			}
			cursor
		  }
		  pageInfo{
			hasNextPage
		  }
		}
	  }
	}
	"""

	QUERY_STARREDREPOS1="""
	query($login_name:String!){
	  user(login: $login_name) {
		starredRepositories(first: 20, orderBy: {field: STARRED_AT, direction: DESC}) {
		  edges {
			node {
			  name
			  url
			}
			starredAt
			cursor
		  }
		  pageInfo{
			hasNextPage
		  }
		}
	  }
	}
	"""

	QUERY_STARREDREPOS2="""
	query($login_name:String!,$last_cursor:String!){
	  user(login: $login_name) {
		starredRepositories(first: 20, after:$last_cursor,orderBy: {field: STARRED_AT, direction: DESC}) {
		  edges {
			node {
			  name
			  url
			}
			starredAt
			cursor
		  }
		  pageInfo{
		    hasNextPage
		  }
		}
	  }
	}
	"""
	
	QUERY_CREATEDREPOS1="""
	query($login_name:String!){
	  user(login: $login_name) {
		repositories(first: 20, orderBy: {field: CREATED_AT, direction: DESC}) {
		  edges {
			node {
			  name
			  createdAt
			  url
			}
			cursor
		  }
		  pageInfo{
			hasNextPage
		  }
		}
	  }
	}
	"""

	QUERY_CREATEDREPOS2="""
	query($login_name:String!,$last_cursor:String!){
	  user(login: $login_name) {
		repositories(first: 20, after:$last_cursor,orderBy: {field: CREATED_AT, direction: DESC}) {
		  edges {
			node {
			  name
			  createdAt
			  url
			}
			cursor
		  }
		  pageInfo{
		    hasNextPage
		  }
		}
	  }
	}
	"""
	
	QUERY_PUSHEDREPOS1="""
	query($login_name:String!){
	  user(login: $login_name) {
		repositories(first: 5,affiliations:[OWNER,COLLABORATOR,ORGANIZATION_MEMBER] ,orderBy: {field: PUSHED_AT, direction: DESC}) {
		  edges {
			node {
			  name
			  owner{
				login
			  }
			  pushedAt
			}
			cursor
		  }
		  pageInfo{
			hasNextPage
		  }
		}
	  }
	}
	"""
	
	QUERY_PUSHEDREPOS2="""
	query($login_name:String!,$last_cursor:String!){
	  user(login: $login_name) {
		repositories(first: 5,after:$last_cursor,affiliations:[OWNER,COLLABORATOR,ORGANIZATION_MEMBER] ,orderBy: {field: PUSHED_AT, direction: DESC}) {
		  edges {
			node {
			  name
			  owner{
				login
			  }
			  pushedAt
			}
			cursor
		  }
		  pageInfo{
			hasNextPage
		  }
		}
	  }
	}
	"""
	
	QUERY_COMMITS1="""
	query($repo_name:String!,$repo_owner:String!,$author_id:String!){
	  repository(name: $repo_name,owner:$repo_owner) {
		ref(qualifiedName: "master") {
		  target {
			... on Commit {
			  id
			  history(first: 10,author:{id:$author_id}) {
				pageInfo {
				  hasNextPage
				}
				edges {
				  node {
					committedDate
					messageHeadline
					oid
					message
					commitUrl
					author {
					  name
					  email
					}
				  }
				  cursor
				}
			  }
			}
		  }
		}
	  }
	}
	"""
	
	QUERY_COMMITS2="""
	query($repo_name:String!,$repo_owner:String!,$author_id:String!,$last_cursor:String!){
	  repository(name: $repo_name,owner:$repo_owner) {
		ref(qualifiedName: "master") {
		  target {
			... on Commit {
			  id
			  history(first: 10,after:$last_cursor,author:{id:$author_id}) {
				pageInfo {
				  hasNextPage
				}
				edges {
				  node {
					committedDate
					messageHeadline
					oid
					message
					commitUrl
					author {
					  name
					  email
					}
				  }
				  cursor
				}
			  }
			}
		  }
		}
	  }
	}
	"""

if __name__=="__main__":
	test_weibo=weibospider()
	acts=test_weibo.getActivities('三星GALAXY盖乐世',5)
	print("\n".join(map(str,acts)))
					
					
					
