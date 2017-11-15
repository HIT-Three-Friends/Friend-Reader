#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import os
import requests
import time
import json
import logging

IDENTIFY = 1  # 验证码输入方式:        1:看截图aa.png，手动输入     2:云打码
COOKIE_GETWAY = 0 # 0 代表从https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18) 获取cookie   # 1 代表从https://weibo.cn/login/获取Cookie

logger = logging.getLogger(__name__)
logging.getLogger("selenium").setLevel(logging.WARNING)  # 将selenium的日志级别设成WARNING，太烦人

myWeiBo = [
    ('13467408430', 'aogan571'),
]


def getCookie(account, password):
    if COOKIE_GETWAY == 0:
        return get_cookie_from_login_sina_com_cn(account, password)
    elif COOKIE_GETWAY ==1:
        #return get_cookie_from_weibo_cn(account, password)
        logger.error("COOKIE_GETWAY 1 unimplemented!")
    else:
        logger.error("COOKIE_GETWAY Error!")

def get_cookie_from_login_sina_com_cn(account, password):
    """ 获取一个账号的Cookie """
    loginURL = "https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)"
    username = base64.b64encode(account.encode("utf-8")).decode("utf-8")
    postData = {
        "entry": "sso",
        "gateway": "1",
        "from": "null",
        "savestate": "30",
        "useticket": "0",
        "pagerefer": "",
        "vsnf": "1",
        "su": username,
        "service": "sso",
        "sp": password,
        "sr": "1440*900",
        "encoding": "UTF-8",
        "cdult": "3",
        "domain": "sina.com.cn",
        "prelt": "0",
        "returntype": "TEXT",
    }
    session = requests.Session()
    r = session.post(loginURL, data=postData)
    jsonStr = r.content.decode("gbk")
    info = json.loads(jsonStr)
    if info["retcode"] == "0":
        logger.warning("Get Cookie Success!( Account:%s )" % account)
        # cookie = session.cookies.get_dict()
        # return json.dumps(cookie)
        cookie = session.cookies
        return cookie
    else:
        logger.warning("Failed!( Reason:%s )" % info["reason"])
        return None

if __name__=="__main__":
	cookie=getCookie("13467408430","aogan571")
	print(cookie)
