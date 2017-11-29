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
import time,datetime,traceback,copy
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
			if act['type']=='starredRepos':
				return "%s starred %s"%(pp.info['login'],act['name'])
			elif act['type']=='createdRepos':
				return "%s created a repository %s"%(pp.info['login'],act['name'])
			elif act['type']=='commits':
				return "%s committed to master in %s"%(pp.info['login'],act['repository'])
			else:
				return ""
			
		def transtime(dt):
			return time.strptime(dt, "%Y-%m-%dT%H:%M:%SZ")
			
		if isinstance(userid,int):userid=str(userid)
		backuserid=userid
		dtLatest=datetime.datetime(*timeLatest[0:6]) if timeLatest else None
		dtOldest=datetime.datetime(*timeOldest[0:6]) if timeOldest else None
		
		pp=People(userid,self.session)

		if not pp.info:
			logging.error("cant get user info")
			return []
		
		activityList=[]
		
		cnt=0
		for act in pp.activities:
			try:
				entry={
					'username':pp.info['name'] if pp.info['name'] else userid,
					'avatar_url':pp.info['avatarUrl'] if pp.info['avatarUrl'] else "",
					'headline':pp.info['bioHTML'],
					'time':transtime(act['date']),
					'actionType':act['type'],
					'summary':formsummary(pp,act),
					'targetText':act['message'] if 'message' in act else "",
					'topics':[],
					'source_url':act['URL']
				}
				
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
			self._Info=result
			return self._Info
		else: return None
	
	@property
	def activities(self):
		
		def moveToNextAction(entry):
			try:entry['nextAction']=next(entry['gen'])
			except StopIteration as e:
				logging.info('Action exhausted')
				entry['nextAction']={'date':'0'}
		
		if not self.id or not self.session: return None
		actions={'starredRepos','createdRepos','commits'}
		
		dl={}
		for action in actions:
			gen=getattr(self,action)
			dl[action]={'gen':gen,'nextAction':{'date':'0'}}
			moveToNextAction(dl[action])
		
		failtimes=0
		while failtimes<3:
			try:
				latestAction=max(dl.items(),key=lambda x:x[1]['nextAction']['date'])
				ActionName,action=latestAction
				if action['nextAction']['date']=='0':raise StopIteration
				actionEntry=copy.deepcopy(action['nextAction'])
				moveToNextAction(action)
				actionEntry['type']=ActionName
				yield actionEntry
			except Exception as e:
				logging.error("get action failed")
				traceback.print_exc()
				failtimes+=1
			
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
		result=r.json()
		failtimes=0
		while failtimes<3:
			if r.status_code==200 and "errors" not in result:			
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
				failtimes+=1
				if "errors" in result:
					logging.error(self.id+" : "+result['errors'])
					

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
		result=r.json()
		failtimes=0
		while failtimes<3:
			if r.status_code==200 and "errors" not in result:
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
				failtimes+=1
				if "errors" in result:
					logging.error(self.id+" : "+result['errors'])
										

	@property
	def pushedRepos(self):
		if not self.id or not self.session: return None
		
		data={
			"query":self.QUERY_PUSHEDREPOS1,
			"variables":
				{
					"login_name":self.id,
					"author_id":self.info['id']
				}
		}
		r=self.session.post(self.url_graphql,data=json.dumps(data))
		result=r.json()
		failtimes=0
		while failtimes<3:
			if r.status_code==200 and "errors" not in result:			
				result=result['data']
				for pp in result['user']['repositories']['edges']:	
					last_cursor=pp['cursor']
					yield {'name':pp['node']['name'],'owner':pp['node']['owner']['login'],'date':pp['node']['pushedAt'],'precommits':{'data':{'repository':pp['node']}}}
				if not result['user']['repositories']['pageInfo']['hasNextPage']:raise StopIteration
				data={
					"query":self.QUERY_PUSHEDREPOS2,
					"variables":
						{
							"login_name":self.id,
							"author_id":self.info['id'],
							"last_cursor":last_cursor
						}
				}
				r=self.session.post(self.url_graphql,data=json.dumps(data))
			else:
				failtimes+=1	
				if "errors" in result:
					logging.error(self.id+" : "+str(result['errors']))
									

	def repoCommits(self,name,owner,precommits=None):
		if not self.id or not self.session: return None
		
		if precommits:
			result=precommits
			r=None
		else:
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
			result=r.json()

		failtimes=0
		while failtimes<3:
			if (not r or r.status_code==200) and "errors" not in result:
				result=result['data']
				for pp in result['repository']['ref']['target']['history']['edges']:	
					last_cursor=pp['cursor']
					yield {'repository':name,'messageHeadline':pp['node']['messageHeadline'],'message':pp['node']['message'],'date':pp['node']['committedDate'],'URL':pp['node']['commitUrl']}
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
				failtimes+=1
				if "errors" in result:
					logging.error(self.id+" : "+str(result['errors']))
					
					
	@property
	def commits(self):
		def addRepos(lis,count,pushedReposLis):
			while count>0:
				try:repo=next(pushedReposLis)
				except StopIteration as e:logging.info("pushedRepos exhausted");raise StopIteration
				repocommits=self.repoCommits(repo['name'],repo['owner'],repo['precommits'])
				try:nextcommit=next(repocommits)
				except StopIteration as e:nextcommit={'date':'0'}
				except Exception as e:logging.error("get next commit fail "+repo['name'])
				lis.append({'commits':repocommits,'nextcommit':nextcommit,'date':nextcommit['date'],'visited':False})
				count-=1
						
		def existunvis(lis):
			for repo in lis:
				if not repo['visited']:return True
			return False
			
		if not self.id or not self.session: return None
		
		pushedReposLis=self.pushedRepos
		lis=[]
		reponum=10
		try:addRepos(lis,reponum,pushedReposLis)
		except StopIteration as e:pass
		failtimes=0
		while failtimes<3:
			try:
				if not existunvis(lis):
					try:addRepos(lis,reponum,pushedReposLis)
					except StopIteration as e:pass
				latestRepo=max(lis,key=lambda x:x['date'])
				if latestRepo['date']=="0":raise StopIteration
				
				commit=latestRepo['nextcommit']
				try:latestRepo['nextcommit']=next(latestRepo['commits'])
				except StopIteration as e:latestRepo['nextcommit']['date']='0'
				latestRepo['visited']=True
				latestRepo['date']=latestRepo['nextcommit']['date']
				yield commit
			except Exception as e:
				failtimes+=1
				logging.error("get next commits fail")
				traceback.print_exc()

					
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
		result=r.json()
		failtimes=0
		while failtimes<3:
			if r.status_code==200 and "errors" not in result:
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
				failtimes+=1
				if "errors" in result:
					logging.error(self.id+" : "+result['errors'])
								
				
				

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
		result=r.json()
		failtimes=0
		while failtimes<3:
			if r.status_code==200 and "errors" not in result:	
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
				failtimes+=1	
				if "errors" in result:
					logging.error(self.id+" : "+result['errors'])
						
	
	QUERY_USER_INFO="""	
	query($login_name:String!){
	  user(login:$login_name){
		id
		login
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
	query($login_name:String!,$author_id:ID!){
	  user(login: $login_name) {
		repositories(first: 10,affiliations:[OWNER,COLLABORATOR,ORGANIZATION_MEMBER] ,orderBy: {field: PUSHED_AT, direction: DESC}) {
		  edges {
			node {
			  name
			  owner{
				login
			  }
			  pushedAt
			  
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
	query($login_name:String!,$last_cursor:String!,$author_id:ID!){
	  user(login: $login_name) {
		repositories(first: 10,after:$last_cursor,affiliations:[OWNER,COLLABORATOR,ORGANIZATION_MEMBER] ,orderBy: {field: PUSHED_AT, direction: DESC}) {
		  edges {
			node {
			  name
			  owner{
				login
			  }
			  pushedAt
			  
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
	query($repo_name:String!,$repo_owner:String!,$author_id:ID!){
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
	query($repo_name:String!,$repo_owner:String!,$author_id:ID!,$last_cursor:String!){
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
					
					
					
