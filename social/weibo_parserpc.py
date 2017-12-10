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

host = "https://weibo.cn"

def parse_information(response,session):
	""" 抓取个人信息 """
	
	try:
		
		informationItem = {}
		root=html.fromstring(response.text)
		ID = re.search(r"\$CONFIG\['oid'\]='(\d+)'", response.text).group(1)
		print(ID)
		scriptList=root.xpath("//script")
		peoInfo=None
		for script in scriptList:
			if "\"domid\":\"Pl_Official_PersonalInfo" in script.text:
				peoInfo=html.fromstring("<html>"+escapeHtml(eval(re.search(r"FM.view\((.*)\)",script.text).group(1))['html'])+"</html>")
		if peoInfo is None:return None
		infoList=peoInfo.xpath("/html/body/div[./div/div/div/h2/text()='基本信息']//ul[@class='clearfix']/li")
		print(infoList)
		return
		
		keymap={'昵称':'nickname','性别':'gender','所在地':'place','简介':'briefIntroduction','生日','birthday'}
			
		for li in infoList:
			
	
		text1 = ";".join(selector.xpath('body/div[@class="c"]//text()').extract())  # 获取标签里的所有text()
		nickname = re.findall('昵称[：:]?(.*?);', text1)
		gender = re.findall('性别[：:]?(.*?);', text1)
		place = re.findall('地区[：:]?(.*?);', text1)
		briefIntroduction = re.findall('简介[：:]?(.*?);', text1)
		birthday = re.findall('生日[：:]?(.*?);', text1)
		sexOrientation = re.findall('性取向[：:]?(.*?);', text1)
		sentiment = re.findall('感情状况[：:]?(.*?);', text1)
		vipLevel = re.findall('会员等级[：:]?(.*?);', text1)
		authentication = re.findall('认证[：:]?(.*?);', text1)
		url = re.findall('互联网[：:]?(.*?);', text1)
		return
		informationItem["_id"] = ID
		if nickname and nickname[0]:
			informationItem["NickName"] = nickname[0].replace(u"\xa0", "")
		if gender and gender[0]:
			informationItem["Gender"] = gender[0].replace(u"\xa0", "")
		if place and place[0]:
			place = place[0].replace(u"\xa0", "").split(" ")
			informationItem["Province"] = place[0]
			if len(place) > 1:
				informationItem["City"] = place[1]
		if briefIntroduction and briefIntroduction[0]:
			informationItem["BriefIntroduction"] = briefIntroduction[0].replace(u"\xa0", "")
		if birthday and birthday[0]:
			try:
				birthday = datetime.datetime.strptime(birthday[0], "%Y-%m-%d")
				informationItem["Birthday"] = birthday - datetime.timedelta(hours=8)
			except Exception:
				informationItem['Birthday'] = birthday[0]   # 有可能是星座，而非时间
		if sexOrientation and sexOrientation[0]:
			if sexOrientation[0].replace(u"\xa0", "") == gender[0]:
				informationItem["SexOrientation"] = "同性恋"
			else:
				informationItem["SexOrientation"] = "异性恋"
		if sentiment and sentiment[0]:
			informationItem["Sentiment"] = sentiment[0].replace(u"\xa0", "")
		if vipLevel and vipLevel[0]:
			informationItem["VIPlevel"] = vipLevel[0].replace(u"\xa0", "")
		if authentication and authentication[0]:
			informationItem["Authentication"] = authentication[0].replace(u"\xa0", "")
		if url:
			informationItem["URL"] = url[0]
		
		try: avatar_url=selector.xpath('body/div[@class="c"]/img/@src').extract()[0]
		except Exception as e: logging.debug("get user img failed")

		if avatar_url:
			informationItem["Avatar_url"] =avatar_url

		try:
			urlothers = "https://weibo.cn/attgroup/opening?uid=%s" % ID
			r = session.get(urlothers, timeout=5)
			if r.status_code == 200:
				selector = etree.HTML(r.content)
				texts = ";".join(selector.xpath('//body//div[@class="tip2"]/a//text()'))
				if texts:
					num_tweets = re.findall('微博\[(\d+)\]', texts)
					num_follows = re.findall('关注\[(\d+)\]', texts)
					num_fans = re.findall('粉丝\[(\d+)\]', texts)
					if num_tweets:
						informationItem["Num_Tweets"] = int(num_tweets[0])
					if num_follows:
						informationItem["Num_Follows"] = int(num_follows[0])
					if num_fans:
						informationItem["Num_Fans"] = int(num_fans[0])
		except Exception as e:
			pass

	except Exception as e:
		logging.warning("get weibo user info failed "+str(e))
		traceback.print_exc()
		return None
	else:
		return informationItem

def parse_tweets(response,session):
	""" 抓取微博数据 """
	while(True):
		selector = Selector(response)
		ID = re.findall(r'(?<=/)[^/]*$', response.url)[0]
		divs = selector.xpath('body/div[@class="c" and @id]')
		for div in divs:
			try:
				tweetsItems = TweetsItem()
				id = div.xpath('@id').extract_first()  # 微博ID
				content = div.xpath('div/span[@class="ctt"]//text()').extract()  # 微博内容
				cooridinates = div.xpath('div/a/@href').extract()  # 定位坐标
				like = re.findall('赞\[(\d+)\]', div.extract())  # 点赞数
				transfer = re.findall('转发\[(\d+)\]', div.extract())  # 转载数
				comment = re.findall('评论\[(\d+)\]', div.extract())  # 评论数
				others = div.xpath('div/span[@class="ct"]/text()').extract()  # 求时间和使用工具（手机或平台）
				
				insidedivs=div.xpath('div')
				for subdiv in insidedivs:
					cmt = subdiv.xpath('span//text()').extract()
					if ('转发理由:' in cmt):
						tweetsItems['ActType']="trans"
						
						originContent=subdiv.xpath('text()').extract()[0]
						originContent="".join(originContent).replace(u"\xa0", "").replace("\u200b","")
						content,originContent=originContent,content
						
						transFrom=div.xpath('div[1]/span[@class="cmt"]/a//text()').extract()
						transFrom="".join(transFrom).replace("\u200b","").replace(u"\xa0", "")
					else:
						tweetsItems['ActType']="origin"
					
				imgs=div.xpath('div//img[@alt="图片"]/@src').extract()
				if imgs:
					tweetsItems['ImageUrls']=imgs
				
				tweetsItems["_id"] = id
				tweetsItems["ID"] = ID
				if content:
					tweetsItems["Content"] = "".join(content).strip('[位置]').replace("\u200b","").replace(u"\xa0", "")  # 去掉最后的"[位置]"
				if cooridinates:
					cooridinates = re.findall('center=([\d.,]+)', cooridinates[0])
					if cooridinates:
						tweetsItems["Co_oridinates"] = cooridinates[0]
				if like:
					tweetsItems["Like"] = int(like[0])
				if transfer:
					tweetsItems["Transfer"] = int(transfer[0])
				if comment:
					tweetsItems["Comment"] = int(comment[0])
				if others:
					others = others[0].split('来自')
					tweetsItems["PubTime"] = others[0].replace(u"\xa0", "")
					if len(others) == 2:
						tweetsItems["Tools"] = others[1].replace(u"\xa0", "")
				if tweetsItems['ActType']=="trans":
					tweetsItems["OriginContent"]="".join(originContent).replace("\u200b","").replace(u"\xa0", "")
					tweetsItems["TransFrom"]=transFrom
					
					
				yield tweetsItems
			except Exception as e:
				traceback.print_exc()

		url_next = selector.xpath('body/div[@class="pa" and @id="pagelist"]/form/div/a[text()="下页"]/@href').extract()
		if not url_next: break
		response=session.get(url=host + url_next[0])
		if response.status_code!=200:break

def parse_followings(response,session):
	""" 抓取关注人列表 """
	while(True):
		selector = Selector(response)
		peoples = selector.xpath('body/table/tr/td[2]/a[1]')
		for people in peoples:
			try:
				screen_name=people.xpath('text()').extract()[0]
				id_url=people.xpath('@href').extract()[0]
				id=re.search(r'(?<=/)[^/]*$',id_url).group()
				yield (screen_name,id)
			except Exception as e:
				logging.warning(str(e))

		url_next = selector.xpath('body/div[@class="pa" and @id="pagelist"]/form/div/a[text()="下页"]/@href').extract()
		if not url_next: break
		response=session.get(url=host + url_next[0])
		if response.status_code!=200:break

def parse_followers(response,session):
	""" 抓取粉丝列表 """
	while(True):
		selector = Selector(response)
		peoples = selector.xpath('body/table/tr/td[2]/a[1]')
		for people in peoples:
			try:
				screen_name=people.xpath('text()').extract()[0]
				id_url=people.xpath('@href').extract()[0]
				id=re.search(r'(?<=/)[^/]*$',id_url).group()
				yield (screen_name,id)
			except Exception as e:
				logging.warning(str(e))

		url_next = selector.xpath('body/div[@class="pa" and @id="pagelist"]/form/div/a[text()="下页"]/@href').extract()
		if not url_next: break
		response=session.get(url=host + url_next[0])
		if response.status_code!=200:break

def escapeHtml(ss):
	return ss.replace("\\r","\r").replace("\\n","\n").replace("\\t","\t").replace("\\\"","\"").replace("\\/","/")
		
if __name__=="__main__":
	class repon(object):
		def __init__(self,filename):
			self.text=open(filename,"rb").read().decode('utf-8')
	r=repon("AkaisoraTestInfoPage.html")
	parse_information(r,None)
	