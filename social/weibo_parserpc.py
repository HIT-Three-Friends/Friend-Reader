#coding: utf-8

import sys,io
import logging,traceback
import datetime
import requests
import re
from lxml import etree
from lxml import html
import logging

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030')         #改变标准输出的默认编码

host = "https://weibo.com"
pageBarUrl="https://weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=100505&profile_ftype=1&is_all=1&pagebar=%d&pl_name=%s&id=100505%s&script_uri=/p/100505%s/home&feed_type=0&page=%d&pre_page=%d&domain_op=100505"
commentSmallUrl="https://weibo.com/aj/v6/comment/small?ajwvr=6&act=list&mid=%s&uid=%s&isMain=true&dissDataFromFeed=%5Bobject%20Object%5D&ouid=%s&location=page_100505_home&comment_type=0&_t=0"
commentSmallisAllUrl="https://weibo.com/aj/v6/comment/small?ajwvr=6&mid=%s&filter=all"
def parse_information(response,session):
	""" 抓取个人信息 """
	
	try:
		
		informationItem = {}
		root=html.fromstring(response.text)
		ID = re.search(r"\$CONFIG\['oid'\]='(\d+)'", response.text).group(1)
		#print(ID)
		scriptList=root.xpath("//script")
		peoInfo=None
		for script in scriptList:
			if "\"domid\":\"Pl_Official_PersonalInfo" in script.text:
				peoInfo=html.fromstring("<html>"+escapeHtml(eval(re.search(r"FM.view\((.*)\)",script.text).group(1))['html'])+"</html>")
			elif "\"domid\":\"Pl_Official_Header" in script.text:
				headImg=html.fromstring("<html>"+escapeHtml(eval(re.search(r"FM.view\((.*)\)",script.text).group(1))['html'])+"</html>")
			elif "\"domid\":\"Pl_Core_T8CustomTriColumn" in script.text:
				statistics=html.fromstring("<html>"+escapeHtml(eval(re.search(r"FM.view\((.*)\)",script.text).group(1))['html'])+"</html>")
		
		if peoInfo is None:return None
		
		#抽取个人信息
		infoList=peoInfo.xpath("/html/body/div[./div/div/div/h2/text()='基本信息']//ul[@class='clearfix']/li")
		
		infoKeyMap={'昵称':'NickName','性别':'Gender','所在地':'Place','简介':'BriefIntroduction','生日':'Birthday',
					'微博':'Num_Tweets','关注':'Num_Follows','粉丝':'Num_Fans'}
			
		for li in infoList:
			classi=li.xpath('./*[1]')[0].text
			value=li.xpath('./*[2]')[0].text
			classi=classi.strip(':').strip('：')
			if classi in infoKeyMap:
				informationItem[infoKeyMap[classi]]=value
	
		#抽取头像链接
		try:
			avatar_url=headImg.xpath("//img[@class='photo']/@src")[0]
			if avatar_url:informationItem["Avatar_url"]="https:"+avatar_url
		except Exception as e: logging.debug("get user img failed")
		
		#抽取数据关注数，粉丝数，微博条数
		try:
			statisticsList=statistics.xpath("//td")
			for sta in statisticsList:
				value=sta.xpath(".//strong/text()")[0]
				classi=sta.xpath(".//span/text()")[0]
				
				if classi in infoKeyMap:
					informationItem[classi]=int(value)
		except Exception as e: logging.debug("get user statistics failed")

	except Exception as e:
		logging.warning("get weibo user info failed "+str(e))
		traceback.print_exc()
		return None
	else:
		return informationItem

		
def parse_tweets(response,session):
	""" 爬取微博数据"""
	pageNum=1
	pagebarNum=-1
	flagNewPage=True
	ID = re.search(r"\$CONFIG\['oid'\]='(\d+)'", response.text).group(1)
	onick=re.search(r"\$CONFIG\['onick'\]='(.+)'", response.text).group(1)
	while(True):
		
		if flagNewPage:
			logging.debug("get new page")
			root = html.fromstring(response.text)
			scriptList=root.xpath("//script")
			for script in scriptList:
				if "\"domid\":\"Pl_Official_MyProfileFeed" in script.text:
					blogs=html.fromstring("<html>"+escapeHtml(eval(re.search(r"FM.view\((.*)\)",script.text).group(1))['html'])+"</html>")
					plname=re.search(r"Pl_Official_MyProfileFeed__\d+",script.text).group()
			flagNewPage=False
		else:
			logging.debug("get new page bar")
			blogs=html.fromstring("<html>"+response.json()['data']+"</html>")
		
		blogList=blogs.xpath("//div[@action-type='feed_list_item']")
		for blog in blogList:
			try:
				tweetsItems = {}
				#print("\n"+blog.xpath("@tbinfo")[0])
				
				if blog.xpath("@minfo"):
					tweetsItems['ActType']="trans"
					tweetsItems['userid']=ID
					tweetsItems['Username']=onick
					tweetsItems['mid']=blog.xpath("@mid")[0]
					tweetsItems['Content']=sharpContent("".join(blog.xpath(".//div[@node-type='feed_list_content']//text()")))
					tweetsItems['PubTime']=blog.xpath(".//a[@node-type='feed_list_item_date' and @name='"+tweetsItems['mid']+"']/@title")[0]
					if blog.xpath("./div/div[@class='web_detail']/div/div[@class='media_box']"):
						tweetsItems['ImageUrls']=blog.xpath("./div/div[@class='web_detail']/div/div[@class='media_box']//img/@src")
					#originBlog
					rinfo=blog.xpath("@minfo")[0]
					tweetsItems['TransFromUserid']=re.search(r'\d+',rinfo.split('&')[0]).group()
					tweetsItems['Originmid']=re.search(r'\d+',rinfo.split('&')[1]).group()
					rblog=blog.xpath(".//div[@node-type='feed_list_forwardContent']")[0]
					tweetsItems['TransFrom']=rblog.xpath("./div[@class='WB_info']/a[@node-type='feed_list_originNick']/@nick-name")[0]
					tweetsItems['OriginContent']=sharpContent("".join(rblog.xpath("./div[@node-type='feed_list_reason']/text()")))
					if rblog.xpath(".//div[@class='media_box']"):
						tweetsItems['OriginImageUrls']=rblog.xpath(".//div[@class='media_box']//img/@src")
					
					
				elif blog.xpath("./div[@class='WB_cardtitle_b S_line2']") and '赞' in "".join(blog.xpath("./div[1]//text()")):
					tweetsItems['ActType']="like"
					tweetsItems['userid']=ID
					tweetsItems['Username']=onick
					tweetsItems['TransFromUserid']=re.search(r'ouid=(\d+)',blog.xpath("@tbinfo")[0]).group(1)
					tweetsItems['TransFrom']=blog.xpath(".//div[@node-type='feed_list_content']/@nick-name")[0]
					tweetsItems['OriginContent']=sharpContent("".join(blog.xpath(".//div[@node-type='feed_list_content']/text()")))
					tweetsItems['Originmid']=blog.xpath("@mid")[0]
					tweetsItems['PubTime']=transtime(sharpContent(blog.xpath(".//div[@class='WB_cardtitle_b S_line2']//span[@class='subtitle']/a/text()")[0]))
					if blog.xpath(".//div[@class='media_box']"):
						tweetsItems['OriginImageUrls']=blog.xpath(".//div[@class='media_box']//img/@src")

				else:
					tweetsItems['ActType']="origin"
					tweetsItems['userid']=re.search(r'ouid=(\d+)',blog.xpath("@tbinfo")[0]).group(1)
					tweetsItems['mid']=blog.xpath("@mid")[0]
					tweetsItems['Content']=sharpContent("".join(blog.xpath(".//div[@node-type='feed_list_content']/text()")))
					tweetsItems['Username']=blog.xpath(".//div[@class='WB_info']/a/text()")[0]
					tweetsItems['PubTime']=blog.xpath(".//a[@node-type='feed_list_item_date']/@title")[0]
					if blog.xpath(".//div[@class='media_box']"):
						tweetsItems['ImageUrls']=blog.xpath(".//div[@class='media_box']//img/@src")
				if 'mid' in tweetsItems:
					tweetsItems['Comments']=getComments(ID,tweetsItems['mid'],session)
				
				yield tweetsItems
			except Exception as e:
				traceback.print_exc()

		url_next=getNextPageUrl(blogs)
		#print("URL_NEXT==============",url_next)
		if url_next=="end":
			break
		elif url_next:
			url=host+url_next
			response=session.get(url=url)
			pageNum=int(re.search(r"page=(\d+)",url).group(1))
			pagebarNum=-1
			flagNewPage=True
		else:
			pagebarNum+=1
			url=pageBarUrl%(pagebarNum,plname,ID,ID,pageNum,pageNum)
			response=session.get(url=url)
		
		if response.status_code!=200:
			logging.error("gate page data fail "+url)

def getComments(userid,mid,session):
	url=commentSmallisAllUrl%(mid)
	r=session.get(url)
	js=r.json()
	if r.status_code!=200:
		print(js)
		logging.error("getComment fail status_code=%d"%r.status_code)
	total=js['data']['count']
	if total<=0:return []
	
	root=html.fromstring("<html>"+js['data']['html']+"</html>")
	commentList=root.xpath(".//div[@node-type='root_comment']")
	for comment in commentList:
		commentItem={}
		
		commentItem['commentId']=comment.xpath("./@comment_id")[0]
		commentItem['commentNickName']=comment.xpath("./div[@node-type='replywrap']/div[@class='WB_text']/a[@usercard]/text()")[0]
		commentItem['commentContent']=sharpContent("".join(comment.xpath("./div[@node-type='replywrap']/div[@class='WB_text']/text()"))).strip(':').strip('：')
		commentItem['commentImgUrls']=list(map(lambda x:"https:"+x,comment.xpath("./div[@node-type='replywrap']//div[@class='media_box']//img/@src")))
		
		yield commentItem

def parse_followings(response,session):
	""" 抓取关注人列表 """
	while(True):
	
		root = html.fromstring(response.text)
		scriptList=root.xpath("//script")
		for script in scriptList:
			if "\"domid\":\"Pl_Official_HisRelation__" in script.text:
				peoples=html.fromstring("<html>"+escapeHtml(eval(re.search(r"FM.view\((.*)\)",script.text).group(1))['html'])+"</html>")
	
		peopleList = peoples.xpath(".//ul[@class='follow_list']/li")
		for people in peopleList:
			try:
				screen_name=people.xpath(".//a[@usercard]/text()")[0]
				id=re.search(r"uid=(\d+)",people.xpath("@action-data")[0]).group(1)
				yield (screen_name,id)
			except Exception as e:
				logging.warning(str(e))

		url_next = peoples.xpath(".//div[@class='W_pages']//a[@class='page next S_txt1 S_line1']/@href")
		if not url_next: break
		response=session.get(url=host + url_next[0])
		if response.status_code!=200:break

def parse_followers(response,session):
	""" 抓取粉丝列表 """
	while(True):
	
		root = html.fromstring(response.text)
		scriptList=root.xpath("//script")
		for script in scriptList:
			if "\"domid\":\"Pl_Official_HisRelation__" in script.text:
				peoples=html.fromstring("<html>"+escapeHtml(eval(re.search(r"FM.view\((.*)\)",script.text).group(1))['html'])+"</html>")
	
		peopleList = peoples.xpath(".//ul[@class='follow_list']/li")
		for people in peopleList:
			try:
				screen_name=people.xpath(".//a[@usercard]/text()")[0]
				id=re.search(r"uid=(\d+)",people.xpath("@action-data")[0]).group(1)
				yield (screen_name,id)
			except Exception as e:
				logging.warning(str(e))

		url_next = peoples.xpath(".//div[@class='W_pages']//a[@class='page next S_txt1 S_line1']/@href")
		if not url_next: break
		response=session.get(url=host + url_next[0])
		if response.status_code!=200:break

def escapeHtml(ss):
	return ss.replace("\\r","\r").replace("\\n","\n").replace("\\t","\t").replace("\\\"","\"").replace("\\/","/")

def sharpContent(ss):
	ss=ss.replace('\u200b','').replace('\xa0','').strip()
	return ss
	
def getNextPageUrl(blogs):
	listPage=blogs.xpath(".//div[@node-type='feed_list_page']")
	lazyload=blogs.xpath(".//div[@node-type='lazyload']")
	if lazyload:return None
	if not listPage:return "end"
	# print("="*30)
	# print(etree.tostring(listPage[0]))
	# print("="*30)
	nextPage=listPage[0].xpath("./div[@class='W_pages']/a[@class='page next S_txt1 S_line1']/@href")
	if not nextPage:return "end"
	return nextPage[0]

def transtime(timstr):
	"""2017-12-09 02:34"""
	
	timstr=re.search(r'昨天\d+:\d+|\d+月\d+日|今天\d+:\d+|\d+分钟前|\d+秒钟前|\d+小时前|\d+-\d+-\d+',timstr).group()
	lct=datetime.datetime.now()
	try:
		tim=datetime.datetime.strptime(timstr,"%Y-%m-%d %H:%M")
		return tim.strftime("%Y-%m-%d %H:%M")
	except Exception as e:pass
	try:
		tim=datetime.datetime.strptime(timstr,"%m月%d日")
		timstr=timstr+lct.strftime("+%Y")
		tim=datetime.datetime.strptime(timstr,"%m月%d日+%Y")
		return tim.strftime("%Y-%m-%d %H:%M")
	except Exception as e:pass
	try:
		tim=datetime.datetime.strptime(timstr,"今天%H:%M")
		timstr=timstr+lct.strftime("+%Y,%m,%d")
		tim=datetime.datetime.strptime(timstr,"今天%H:%M+%Y,%m,%d")
		return tim.strftime("%Y-%m-%d %H:%M")
	except Exception as e:pass
	try:
		tim=datetime.datetime.strptime(timstr,"昨天%H:%M")
		timstr=timstr+lct.strftime("+%Y,%m,%d")
		tim=datetime.datetime.strptime(timstr,"昨天%H:%M+%Y,%m,%d")
		tim=tim+datetime.timedelta(days=-1)
		return tim.strftime("%Y-%m-%d %H:%M")
	except Exception as e:pass
	try:
		deltamin=int(re.fullmatch("(\d{1,2})分钟前",timstr).group(1))
		tim=datetime.datetime.now()+datetime.timedelta(minutes=-deltamin)
		return tim.strftime("%Y-%m-%d %H:%M")
	except Exception as e:pass
	try:
		deltasec=int(re.fullmatch("(\d{1,2})秒钟前",timstr).group(1))
		tim=datetime.datetime.now()+datetime.timedelta(seconds=-deltasec)
		return tim.strftime("%Y-%m-%d %H:%M")
	except Exception as e:pass
	try:
		deltahour=int(re.fullmatch("(\d{1,2})小时前",timstr).group(1))
		tim=datetime.datetime.now()+datetime.timedelta(hours=-deltahour)
		return tim.strftime("%Y-%m-%d %H:%M")
	except Exception as e:pass
	try:
		tim=datetime.datetime.strptime(timstr,"%Y-%m-%d")
		return tim.strftime("%Y-%m-%d %H:%M")
	except Exception as e:pass
	return datetime.datetime.now()
	
if __name__=="__main__":
	class repon(object):
		def __init__(self,filename):
			self.text=open(filename,"rb").read().decode('utf-8')
	r=repon("AkaisoraTestActPage.html")
	print(next(parse_tweets(r,None)))
	