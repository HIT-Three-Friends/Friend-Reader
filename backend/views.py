from django.shortcuts import render
from django.http import JsonResponse
from backend.models import users,friends,social,Picture,allactivity,pics,topic,focus,friendfriend,friendtopic
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
from social import social as socialpc
from datetime import datetime
import  time
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from PIL import Image
from email.utils import formataddr
import urllib.request
# Create your views here.
client = socialpc()
def testfuck(request):
    return render(request, 'testindex.html')
def gettopic(text,account):
    uri_base = "https://api.ltp-cloud.com/analysis/?"
    api_key = "F1a5e3k9w7UPcXnfjcETgQFTwWZVoCvKwIwEEtmQ"
    # Note that if your text contain special characters such as linefeed or '&',
    # you need to use urlencode to encode your data
    format = 'plain'
    pattern = "all"
    text = urllib.request.quote(text)
    url = (uri_base
           + "api_key=" + api_key + "&"
           + "text=" + text + "&"
           + "format=" + format + "&"
           + "pattern=" + 'pos')
    top = []
    try:
        response = urllib.request.urlopen(url)
        content = response.read().strip().decode('utf8')
        ans = content.split()
        for a in ans:
            if a[-2:] == "_a":
                newtop = a.replace('_a', '')
                if newtop != "微博" and newtop not in account:
                    top.append(newtop)
            elif a[-2:] == '_n':
                newtop = a.replace('_n', '')
                if newtop != "微博" and newtop not in account:
                    top.append(newtop)
            elif a[-2:] == '_i':
                newtop = a.replace('_i', '')
                if newtop != "微博" and newtop not in account:
                    top.append(newtop)
            elif a[-3:] == '_nz':
                newtop = a.replace('_nz', '')
                if newtop != "微博" and newtop not in account:
                    top.append(newtop)
    except :
        top = []
    top = list(set(top))
    return top

def refresh():
    print("ojbk")
    ac = list(friends.objects.values('id'))
    for all in ac:
        refreshfriend(all['id'])

@csrf_protect
#新建用户 get用户信息
def user(request):
    result = {'verdict': 'success', 'message': 'Successful!'}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        username = str(username)
        password = str(password)
        email = str(email)
        result['email'] = email
        result['password'] = password
        result['username'] = username
        #return JsonResponse(result)
        userinfo = users.objects.filter(Q(email = email)|Q(username = username))
        if userinfo:
            result['verdict'] = 'fail'
            result['message'] = 'The email or username already exits!'
        else:
            users.objects.create(username = username , password = password ,email = email ,friendnum = 0)
        return JsonResponse(result)
    else :
        username = request.session.get('username','')
        userinfo = users.objects.filter(username=username)
        if userinfo:
            result['username'] = username
            result['email'] = str(list(userinfo.values('email'))[0]['email'])
            #result['avatar'] = '/media/'+str(list(userinfo.values('avatar'))[0]['avatar'])
        else:
            result['verdict'] = 'error'
            result['message'] = 'Please log in first!'
        return JsonResponse(result)

#登录
def login(request):
    username = request.POST['username']
    password = request.POST['password']
    username = str(username)
    password = str(password)
    result = {'verdict': 'success', 'message': 'Successful'}
    userinfo = users.objects.filter(username = username,password = password)
    if userinfo:
        request.session["username"] = username
    else:
        result['verdict'] = 'fail'
        result['message'] = 'The Username or Password is not correct'
    return JsonResponse(result)

#登出
def logout(request):
    del request.session["username"]
    result = {'verdict':'success','message':'Successful'}
    return JsonResponse(result)

#新建好友 好友列表
def myfriends(request):
    result = {'verdict': 'success', 'message': 'Successful'}
    username = request.session.get('username', '')
    userinfo = users.objects.filter(username=username)
    #是否在线
    if userinfo:
        if request.method == 'GET':
            ans = friends.objects.filter(user = username).values('id','friendid','name','sex','avatar')
            ans = list(ans)
            for x in ans:
                x['avatar'] =  '/media/' + x['avatar']
                xsocial = social.objects.filter(father = int(x['id'])).values('platform','account')
                x['social'] = list(xsocial)
            result['friends'] = ans
        else :
            name = request.POST['name']
            name = str(name)
            userof = str(username)
            friendinfo = friends.objects.filter(user = username,name = name)
            if friendinfo:
                result['verdict'] = 'fail'
                result['message'] = '好友已存在'
            else:
                sex = request.POST['sex']
                sex = int(sex)
                avatar = 'upload/2345.bmp'
                #新增计数
                friendid = int(userinfo[0]) + 1
                users.objects.filter(username = username).update(friendnum = int(friendid))
                #返回id
                result['id'] = friendid
                #新建好友
                friends.objects.create(user=userof, friendid=friendid, name=name, sex=sex, avatar=avatar)
                newid = friends.objects.filter(user=username, friendid=friendid).values('id')
                newid = int(list(newid)[0]['id'])
                social.objects.create(father=newid, platform=0, account="")
                social.objects.create(father=newid, platform=1, account="")
                social.objects.create(father=newid, platform=2, account="")
    else:
        result['verdict'] = 'error'
        result['message'] = 'Please log in first!'
    return JsonResponse(result)

#标签列表
def myfocus(request):
    result = {'verdict': 'success', 'message': 'Successful'}
    username = request.session.get('username', '')
    userinfo = users.objects.filter(username=username)
    #是否在线
    if userinfo:
        if request.method == 'GET':
            ans = focus.objects.filter(father = username).values('tag','id')
            ans = list(ans)
            result['tags'] = ans
        else :
            name = request.POST['tag']
            name = str(name)
            userof = str(username)
            friendinfo = focus.objects.filter(father = username,tag = name)
            if friendinfo:
                result['verdict'] = 'fail'
                result['message'] = '标签已存在'
            else:
                d = focus.objects.create(father = username,tag = name)
                d = d.id
                result['id'] = d
    else:
        result['verdict'] = 'error'
        result['message'] = 'Please log in first!'
    return JsonResponse(result)

#单个好友 查询 修改 删除
def friend(request,id):
    result = {'verdict': 'success', 'message': 'Successful'}
    username = request.session.get('username', '')
    userinfo = users.objects.filter(username=username)
    # 是否在线
    if userinfo:
        if request.method == 'GET':
            ans = friends.objects.filter(user=username,friendid = id).values('id','friendid', 'name', 'sex', 'avatar')
            dict2 = list(ans)[0]
            dict2['avatar'] = '/media/' + dict2['avatar']
            xsocial = social.objects.filter(father=int(dict2['id'])).values('platform', 'account')
            dict2['social'] = list(xsocial)
            result.update(dict2)
        elif request.method == 'DELETE':
            ff = friends.objects.filter(user=username, friendid=id)
            ffid = list(ff.values('id'))
            for fffid in ffid :
                socialc = (social.objects.filter(father=fffid['id']).values('id'))[0]['id']
                clear(socialc)
            ff.delete()
        else:
            friendinfo = friends.objects.filter(user=username, friendid=id)
            name = request.POST.get('name','ljrsb')
            sex = request.POST.get('sex',-1)
            name = str(name)
            sex = int(sex)
            avatar = request.FILES.get('avatar', 'upload/2345.bmp')
            idd = int(list(friendinfo.values('id'))[0]['id'])
            if name != 'ljrsb':
                friendinfo.update(name = name)
            if sex != -1:
                friendinfo.update(sex = sex)
            # 待修改
            if str(avatar) != 'upload/2345.bmp':
                Picture.objects.filter(user = idd).delete()
                Picture.objects.create(user=idd,image = avatar)
                s = list( Picture.objects.filter(user = idd).values('image'))[0]['image']
                s = str(s)
                result['verdict'] = 's'
                friendinfo.update(avatar=s)
    else:
        result['verdict'] = 'error'
        result['message'] = 'Please log in first!'
    return JsonResponse(result)

#标签的修改、查询、删除
def focu(request,id):
    result = {'verdict': 'success', 'message': 'Successful'}
    username = request.session.get('username', '')
    userinfo = users.objects.filter(username=username)
    # 是否在线
    if userinfo:
        if request.method == 'GET':
            ans = focus.objects.filter(father = username,id = id).values('id','tag')
            dict2 = list(ans)[0]
            result.update(dict2)
        else :
            focus.objects.filter(father=username, id=id).delete()
    else:
        result['verdict'] = 'error'
        result['message'] = 'Please log in first!'
    return JsonResponse(result)

#单个好友单个社交账号查询 修改 删除
def asocial(request,friendid,socialid):
    result = {'verdict': 'success', 'message': 'Successful'}
    username = request.session.get('username', '')
    userinfo = users.objects.filter(username=username)
    # 是否在线
    if userinfo:
        id = friends.objects.filter(user = username,friendid = friendid).values('id')
        #id为好友编号
        id = int(list(id)[0]['id'])
        if request.method == 'GET':
            ans = social.objects.filter(father = id,platform=socialid).values('platform', 'account')
            dict2 = list(ans)[0]
            result.update(dict2)
        elif request.method == 'DELETE':
            social.objects.filter(father=id, platform=socialid).delete()
        else:
            account = request.POST['account']
            account = str(account)
            oldaccount = social.objects.get(father=id, platform=socialid).account
            if (oldaccount == account and account != ''): return JsonResponse(result)
            social.objects.filter(father=id, platform=socialid).update(account=account)
            initact(id,int(socialid));
            return JsonResponse(result)
    else:
        result['verdict'] = 'error'
        result['message'] = 'Please log in first!'
    return JsonResponse(result)

def dt_to_t(newdatetime):
    c = newdatetime.strftime("%a %b %d %H:%M:%S %Y")
    c = c + " UTC"
    return time.strptime(c,"%a %b %d %H:%M:%S %Y %Z")

def t_to_dt(newtime):
    c = time.strftime("%a %b %d %H:%M:%S %Y",newtime)
    c = c + " UTC"
    return datetime.strptime(c, "%a %b %d %H:%M:%S %Y %Z")

#刷新id好友的所有动态
def refreshfriend(id):
    refreshsocial(id,0)
    refreshsocial(id, 1)
    refreshsocial(id, 2)
    return

def sendmessage(useremail,username,flag,act,name):
    my_sender = '18800427105@163.com'  # 发件人邮箱账号，为了后面易于维护，所以写成了变量
    my_user = useremail  # 收件人邮箱账号，为了后面易于维护，所以写成了变量
    try:
        text = '你的好友 ' + name +  ' 发布了关于 '
        for ff in flag:
            text += ff + ' '
        text += '的内容\n'
        text += act['summary'] + '\n' + act['targetText']
        msg = MIMEText(text, 'plain', 'utf-8')
        msg['From'] = formataddr(["FriendReader", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr([username, my_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "FriendReader订阅提醒"  # 邮件的主题，也可以说是标题

        server = smtplib.SMTP("smtp.163.com", 25)  # 发件人邮箱中的SMTP服务器，端口是25
        server.login(my_sender, "123321aaa")  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender, [my_user, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 这句是关闭连接的意思
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")
#刷新id好友的socialid社交账号
def refreshsocial(id,socialid):
    father = list(friends.objects.filter(id = id).values('user','name'))[0]
    user = list(users.objects.filter(username=father['user']).values("email","username"))[0]
    ac = list(social.objects.filter(father=id, platform=socialid).values('id', 'account','time'))[0]
    initfriendfriend(id, socialid)
    plat = ['zhihu', 'weibo', 'github']
    if ac['account'] == '':
        return
    mytime = dt_to_t(ac['time'])
    ans = client.getActivities(ac['account'], plat[socialid],100,mytime)
    if len(ans) > 0 :

        social.objects.filter(father=id, platform=socialid).update(time=datetime.now())
        for act in ans:
            flag = []
            newact = allactivity.objects.create(father=ac['id'], username=act['username'], avatar_url=act['avatar_url'],
                                                headline=act['headline'], time=t_to_dt(act['time']),
                                                actionType=act['actionType'], summary=act['summary'],
                                                targetText=act['targetText'], source_url=act['source_url'])
            newact = newact.id
            if act.__contains__('imgs'):
                for pic in act['imgs']:
                    pics.objects.create(father=newact, imgs=pic)
            if act['topics'] == []:
                act['topics'] = gettopic(act['targetText'] + " "+act['summary'],ac['account'])
            addmylove(act, ac['id'])
            for top in act['topics']:
                findtop = focus.objects.filter(father=father['user'], tag=top)
                if findtop:
                    flag.append(top)
                topic.objects.create(father=newact, topics=top)
            if len(flag) > 0:
                sendmessage(user['email'],user['username'],flag,act,father['name'])

    return

#清空一个账号
def clear(id):
    act = list(allactivity.objects.filter(father = id).values('id'))
    ffll = list(friendfriend.objects.filter(father = id).values('id'))
    allactivity.objects.filter(father=id).delete()
    time.sleep(0.1)
    friendfriend.objects.filter(father=id).delete()
    for a in act :
        pics.objects.filter(father=a['id']).delete()
        topic.objects.filter(father=a['id']).delete()
    for fff in ffll:
        friendtopic.objects.filter(father=fff['id']).delete()

#初始化id好友的socialid社交账号
def initact(id,socialid):
    ac = list(social.objects.filter(father=id, platform=socialid).values('id','account'))[0]
    clear(ac['id'])
    plat = ['zhihu', 'weibo', 'github']
    if ac['account'] == '' :
        return

    ans = client.getActivities(ac['account'], plat[socialid],1000)
    social.objects.filter(father=id, platform=socialid).update(time = datetime.now())
    initfriendfriend(id,socialid)
    if len(ans) == 0 :
        return
    for act in ans:
        newact = allactivity.objects.create(father = ac['id'],username = act['username'],avatar_url = act['avatar_url'],headline = act['headline'],time = t_to_dt(act['time']),actionType = act['actionType'],summary = act['summary'],targetText = act['targetText'],source_url = act['source_url'])
        newact = newact.id

        if act.__contains__('imgs'):
            for pic in act['imgs']:
                pics.objects.create(father=newact, imgs=pic)
        if act['topics']==[]:
            act['topics'] = gettopic(act['targetText'] + " "+act['summary'],ac['account'])
        addmylove(act,ac['id'])
        for top in act['topics']:
            topic.objects.create(father=newact, topics=top)
    return


#给定用户名，以及朋友编号，获取所有动态
def askactivity(username,friendid,page,socialid = -1):
    #获取好友信息
    friendinfo = friends.objects.filter(user=username, friendid=friendid)
    if friendinfo:
        afriend = list(friends.objects.filter(user=username, friendid=friendid).values('friendid','id', 'name', 'sex', 'avatar'))[0]
        #刷新动态
        if page == 1 : refreshfriend(afriend['id'])
        #获取好友社交账号
        account = social.objects.filter(father=afriend['id']).values('platform', 'account','id')
        account = list(account)
        acts = []
        plat = ['zhihu', 'weibo', 'github']
        #枚举每个账号，寻找动态
        for anacount in account:
            if socialid !=-1 and socialid != int(anacount['platform']):
                continue
            #获取动态信息
            allacts = list(allactivity.objects.filter(father = anacount['id']).values('time','summary','targetText','id','source_url'))
            #枚举每条动态，构造返回列表
            for act in allacts:
                act['time'] = dt_to_t(act['time'])
                temp = {}
                temp['name'] = afriend['name']
                temp['sex'] = afriend['sex']
                temp['friendid'] = int(afriend['friendid'])
                temp['avatar'] = '/media/' + str(afriend['avatar'])
                temp['t'] = time.mktime(act['time'])
                temp['G'] = act['time']
                temp['date'] = str(act['time'][0]) + '年' + str(act['time'][1]) + '月' + str(act['time'][2]) + '日'
                temp['time'] = str(act['time'][3]) + ':' + str(act['time'][4]) + ':' + str(act['time'][5])
                temp['title'] = act['summary'] + '<i>' + plat[int(anacount['platform'])] + '.com</i>'
                temp['word'] = act['targetText']
                temp['url'] = act['source_url']
                #根据动态id，寻找动态的imgs和topics
                pic = list(pics.objects.filter(father=act['id']).values('imgs'))
                tag = list(topic.objects.filter(father=act['id']).values('topics'))
                temp['tags'] = []
                temp['pic'] = []
                for p in pic:
                    temp['word'] +=  '<hr /><img src="'+p['imgs']+'">'
                    temp['pic'].append(p['imgs'])
                for t in tag:
                    temp['tags'].append(t['topics'])
                temp['Video'] = []
                acts.append(temp)
        #按时间排序
        acts.sort(key=lambda x: x['t'])
        acts.reverse()
        #返回动态列表
        return acts
    else:
        return []

#外部请求，获取一个好友的全部动态
def activity(request,friendid):
    result = {'verdict': 'success', 'message': 'Successful'}
    username = request.session.get('username', '')
    userinfo = users.objects.filter(username=username)
    page = int(request.GET['page'])
    if userinfo:
        acts = askactivity(username,friendid,page,-1)
        if (len(acts) >= 10 * page):
            result['activitynum'] = 10
        else:
            result['activitynum'] = max(0,len(acts) - 10 * page + 10)
        result['activity'] = acts[(10 * page - 10):(10 * page)]
    else:
        result['verdict'] = 'error'
        result['message'] = 'Please log in first!'
    return JsonResponse(result)

#外部请求，获取一个好友的全部动态 平台筛选
def activityplatform(request,friendid):
    result = {'verdict': 'success', 'message': 'Successful'}
    username = request.session.get('username', '')
    userinfo = users.objects.filter(username=username)
    page = int(request.GET['page'])
    platform = int(request.GET['platform'])
    if userinfo:
        acts = askactivity(username,friendid,page,platform)
        if (len(acts) >= 10 * page):
            result['activitynum'] = 10
        else:
            result['activitynum'] = max(0,len(acts) - 10 * page + 10)
        result['activity'] = acts[(10 * page - 10):(10 * page)]
    else:
        result['verdict'] = 'error'
        result['message'] = 'Please log in first!'
    return JsonResponse(result)

#获取好友所有动态 平台筛选
def activitiesplatform(request):
    result = {'verdict': 'success', 'message': 'Successful'}
    plat = ['zhihu','weibo','github']
    username = request.session.get('username', '')
    userinfo = users.objects.filter(username=username)
    page = int(request.GET['page'])
    platform = int(request.GET['platform'])
    acts = []
    if userinfo:
        #获取好友列表
        id = friends.objects.filter(user=username).values('id', 'name', 'sex', 'avatar', 'friendid')
        id = list(id)
        #对于每个好友获取动态列表
        for afriend in id:
            acts += askactivity(username,afriend['friendid'],page,platform)
        #所有信息按照时间排序
        acts.sort(key=lambda x: x['t'])
        acts.reverse()
        #统计动态个数和page的关系
        if (len(acts) >= 10 * page):
            result['activitynum'] = 10
        else:
            result['activitynum'] = max(0,len(acts) - 10 * page + 10)
        result['activity'] = acts[(10 * page - 10):(10 * page)]
    else:
        result['verdict'] = 'error'
        result['message'] = 'Please log in first!'
    return JsonResponse(result)

#外部请求，获取一个好友的全部动态
def activities(request):
    result = {'verdict': 'success', 'message': 'Successful'}
    plat = ['zhihu','weibo','github']
    username = request.session.get('username', '')
    userinfo = users.objects.filter(username=username)
    page = int(request.GET['page'])
    acts = []
    if userinfo:
        #获取好友列表
        id = friends.objects.filter(user=username).values('id', 'name', 'sex', 'avatar', 'friendid')
        id = list(id)
        #对于每个好友获取动态列表
        for afriend in id:
            acts += askactivity(username,afriend['friendid'],page,-1)
        #所有信息按照时间排序
        acts.sort(key=lambda x: x['t'])
        acts.reverse()
        #统计动态个数和page的关系
        if (len(acts) >= 10 * page):
            result['activitynum'] = 10
        else:
            result['activitynum'] = max(0,len(acts) - 10 * page + 10)
        result['activity'] = acts[(10 * page - 10):(10 * page)]
    else:
        result['verdict'] = 'error'
        result['message'] = 'Please log in first!'
    return JsonResponse(result)

#获取月活跃度
def vitalitymon(request,friendid):
    result = {'verdict': 'success', 'message': 'Successful'}
    days = [0,31,28,31,30,31,30,31,31,30,31,30,31]
    username = request.session.get('username', '')
    userinfo = users.objects.filter(username=username)
    year = int(request.GET['year'])
    month = int(request.GET['month'])
    #确定这个月有多少天
    renum = days[month]
    if (year % 4 == 0 and year % 100 != 4) or year % 400 == 0 :
        renum += 1
    L = [0 for x in range(0,renum)]
    if userinfo:
        ans = askactivity(username, friendid,0)

        for x in ans:
            if x['G'][0] == year and x['G'][1] == month :
                L[x['G'][2]-1]+=1
        result['days'] = renum
        result['vitality'] = L
    else:
        result['verdict'] = 'error'
        result['message'] = 'Please log in first!'
    return JsonResponse(result)

#获取日活跃度
def vitalityday(request,friendid):
    result = {'verdict': 'success', 'message': 'Successful'}
    username = request.session.get('username', '')
    userinfo = users.objects.filter(username=username)
    L = [0 for x in range(1,25)]
    if userinfo:
        ans = askactivity(username, friendid,0)
        result['test'] = len(ans)
        for x in ans:
            L[int(x['G'][3])]+=1
        result['vitality'] = L
    else:
        result['verdict'] = 'error'
        result['message'] = 'Please log in first!'
    return JsonResponse(result)

def interests(request,friendid):
    result = {'verdict': 'success', 'message': 'Successful'}
    username = request.session.get('username', '')
    userinfo = users.objects.filter(username=username)
    byear = int(request.GET['byear'])
    bmonth = int(request.GET['bmonth'])
    bday = int(request.GET['bday'])
    eyear = int(request.GET['eyear'])
    emonth = int(request.GET['emonth'])
    eday = int(request.GET['eday'])
    if userinfo:
        ans = askactivity(username, friendid,0)
        mm = {}
        percent = [] #比例
        tags = [] #标签
        interestnum = 0 #兴趣种类数
        inttag = 0 #兴趣标签总个数
        tmpp = [] #统计用的数组
        for x in ans:
            if (x['G'][0] > eyear) or ( x['G'][0] == eyear and x['G'][1] > emonth ) or (x['G'][0] == eyear and x['G'][1] == emonth and x['G'][2] > eday): continue
            if (x['G'][0] < byear) or ( x['G'][0] == byear and x['G'][1] < bmonth ) or (x['G'][0] == byear and x['G'][1] == bmonth and x['G'][2] < bday): break
            L = len(x['tags'])
            for y in x['tags']:
                if mm.__contains__(y):
                    tmpp[int(mm[y])][1] += 1/L
                else:
                    mm[y] = interestnum
                    interestnum += 1
                    tmpp.append([y,1])
                inttag += 1
        #按照出现次数排序
        tmpp.sort(key=lambda x: x[1])
        tmpp.reverse()
        result['ans'] = tmpp[:10]

        res = 0
        for x in result['ans']:
            percent.append(x[1])
            tags.append(x[0])
            res+=1
        result['interestnum'] = res
        result['tags'] = tags
        result['percent'] = percent
    else:
        result['verdict'] = 'error'
        result['message'] = 'Please log in first!'
    return JsonResponse(result)

def interestyear(request,friendid):
    result = {'verdict': 'success', 'message': 'Successful'}
    username = request.session.get('username', '')
    userinfo = users.objects.filter(username=username)
    year = int(request.GET['year'])
    if userinfo:
        ans = askactivity(username, friendid,0)
        mm = {}
        tags = []
        percent = [[0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0]] #比例
        interestnum = 0 #兴趣种类数
        tmpp = [] #统计用的数组
        for x in ans:
            if (x['G'][0] > year): continue
            if (x['G'][0] < year): break
            L = len(x['tags'])
            for y in x['tags']:
                if mm.__contains__(y):
                    tmpp[int(mm[y])][1] += 1/L
                else:
                    mm[y] = interestnum
                    interestnum += 1
                    tmpp.append([y,1])
        #按照出现次数排序
        tmpp.sort(key=lambda x: x[1])
        tmpp.reverse()
        tmpp = tmpp[:3]
        intt = 0
        for tt in tmpp:
            tags.append(tt[0])
        for x in ans :
            if (x['G'][0] > year): continue
            if (x['G'][0] < year): break
            L = len(x['tags'])
            for y in x['tags']:
                intt = 0
                for tt in tags:
                    if tt == y:
                        percent[intt][x['G'][1]-1] += 1/L
                    intt+=1
        result['num'] = len(tmpp)
        result['topic'] = tags
        result['percent1'] = percent[0]
        result['percent2'] = percent[1]
        result['percent3'] = percent[2]
    else:
        result['verdict'] = 'error'
        result['message'] = 'Please log in first!'
    return JsonResponse(result)

def interestmonth(request,friendid):
    result = {'verdict': 'success', 'message': 'Successful'}
    username = request.session.get('username', '')
    days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    userinfo = users.objects.filter(username=username)
    year = int(request.GET['year'])
    month = int(request.GET['month'])
    # 确定这个月有多少天
    renum = days[month]
    if (year % 4 == 0 and year % 100 != 4) or year % 400 == 0:
        renum += 1
    L = [[0 for x in range(0, renum)],[0 for x in range(0, renum)],[0 for x in range(0, renum)]]
    result['day'] = renum
    if userinfo:
        ans = askactivity(username, friendid,0)
        mm = {}
        tags = []
        percent = L #比例
        interestnum = 0 #兴趣种类数
        tmpp = [] #统计用的数组
        for x in ans:

            if (x['G'][0] < year): break
            if (x['G'][0] == year and x['G'][1] == month):
                L = len(x['tags'])
                for y in x['tags']:
                    if mm.__contains__(y):
                        tmpp[int(mm[y])][1] += 1.0/L
                    else:
                        mm[y] = interestnum
                        interestnum += 1
                        tmpp.append([y,1])
        #按照出现次数排序
        tmpp.sort(key=lambda x: x[1])
        tmpp.reverse()
        tmpp = tmpp[:3]
        intt = 0
        for tt in tmpp:
            tags.append(tt[0])
        for x in ans :
            if (x['G'][0] < year): break
            if (x['G'][0] == year and x['G'][1] == month):
                for y in x['tags']:
                    intt = 0
                    L = len(tags)
                    for tt in tags:
                        if tt == y:
                            percent[intt][x['G'][2]-1] += 1.0/L
                        intt+=1
        result['num'] = len(tmpp)
        result['topic'] = tags
        result['percent1'] = percent[0]
        result['percent2'] = percent[1]
        result['percent3'] = percent[2]
    else:
        result['verdict'] = 'error'
        result['message'] = 'Please log in first!'
    return JsonResponse(result)

#初始化好友列表 好友数据库编号 社交平台
def initfriendfriend(friendid,socialid):
    plat = ['zhihu', 'weibo', 'github']
    #获取关注人+被关注人
    myid = list(social.objects.filter(father=friendid,platform=socialid).values('id','account'))[0]
    print(myid['account'])
    if (socialid != 1) :
        return
    mylove = client.getFollowings(myid['account'],plat[socialid],300)
    loveme = client.getFollowers(myid['account'],plat[socialid],300)
    lovelove = []#和你好友互相关注的人
    for love in mylove:
        if love in loveme:
            lovelove.append(love) # 求互相关注列表
    for love in lovelove:
        loveinfo = friendfriend.objects.filter(father = myid['id'],account=love) #检测关系数据是否存在
        if loveinfo: # 老的好友
            #continue
            #oldfriendfriend()
            # 爬 动态
            tloved = 0.0 # 你得好友被互动次数 = 0
            ac = list(friendfriend.objects.filter(father=myid, account=love).values('id', 'account', 'time','loved'))[0] # 获取当前 关系数据
            mytime = dt_to_t(ac['time'])
            ans = client.getActivities(ac['account'], plat[socialid],100,mytime) # 更新你的好友 的 关注人 的动态
            social.objects.filter(father=myid, account=love).update(time=datetime.now()) # 更新最新 数据时间
            for act in ans :
                # 和 我相关 留下
                # 提取话题
                # 保存话题
                if myid['account'] in act['actionType'] or myid['account'] in act['summary'] or myid['account'] in act['targetText']:
                    top = gettopic(act['targetText']+" "+act['summary']) # 获取好友的话题
                    L = len(top)
                    for tt in top:
                        tloved += 1.0/L
                        ttinfo = friendtopic.objects.filter(father=ac['id'],topics=tt)
                        if ttinfo:
                            pp = list(ttinfo.values('pp'))[0]
                            ttinfo.update(pp = pp['pp'] + 1.0/L)
                        else:
                            friendtopic.objects.create(father = ac['id'],topics = tt,pp = 1.0/L)
            friendfriend.objects.filter(father=myid['id'], account=love).update(loved = ac['loved'] + tloved)
        else:
            # newfriendfriend
            # 数据库新建
            # 爬 动态
            newf = friendfriend.objects.create(father=myid['id'], account=love,time=datetime.now())
            #continue
            ans = client.getActivities(love, plat[socialid], 100)
            tloved = 0.0
            for act in ans :
                # 和 我相关 留下
                # 提取话题
                # 保存话题
                if myid['account'] in act['actionType'] or myid['account'] in act['summary'] or myid['account'] in act['targetText']:
                    top = gettopic(act['targetText'] + " "+act['summary'])
                    L = len(top)
                    for tt in top:
                        tloved += 1.0/L
                        ttinfo = friendtopic.objects.filter(father=newf.id,topics=tt)
                        if ttinfo:
                            pp = list(ttinfo.values('pp'))[0]
                            ttinfo.update(pp = pp['pp'] + 1.0/L)
                        else:
                            friendtopic.objects.create(father = newf.id,topics = tt,pp = 1.0/L)
            newf.update(loved = tloved)
    return

def addmylove(act,socialtid):
    ffll = friendfriend.objects.filter(father=socialtid)#你的好友账号的 所有好友 的 关系数据
    if ffll:
        ffll = list(friendfriend.objects.filter(father=socialtid).values('id', 'loved', 'love', 'account'))
        for fff in ffll :
            if fff['account'] in act['actionType'] or fff['account'] in act['summary'] or fff['account'] in act['targetText']: # 如果他的名字出现在这条动态中
                L = len(act['topics']) #获取主题列表
                for tt in act['topics']:
                    ttinfo = friendtopic.objects.filter(father=fff['id'], topics=tt) #检查互动主题是否存在
                    #计数互动主题
                    if ttinfo:
                        pp = list(ttinfo.values('pp'))[0]
                        ttinfo.update(pp=pp['pp'] + 1.0 / L)
                    else:
                        friendtopic.objects.create(father=fff['id'], topics=tt, pp=1.0 / L)
                #更新 关系数据
                friendfriend.objects.filter(father=socialtid, account=fff['account']).update(love=fff['love'] + 1)
    return
# 获取好友互动排名，互动话题数+话题top3
def interaction(request,id):
    result = {'verdict': 'success', 'message': 'Successful'}
    socialid = 1
    username = request.session.get('username', '')
    userinfo = users.objects.filter(username=username)
    if userinfo:
        friendinfo = friends.objects.filter(user=username, friendid=id)
        if friendinfo :
            afriend = \
            list(friends.objects.filter(user=username, friendid=id).values('friendid', 'id', 'name', 'sex', 'avatar'))[0]
            socialaccount = list(social.objects.filter(platform=socialid,father=afriend['id']).values('id','account'))[0]
            ffll = list(friendfriend.objects.filter(father = socialaccount['id']).values('id','loved','love','account'))
            for fff in ffll:
                fff['total'] = fff['love']+ fff['loved']
            ffll.sort(key=lambda x: x['total'])
            ffll.reverse()
            res = []
            cnt = 1
            for fff in ffll:
                tmp = {}
                tmp['ID'] = cnt
                tmp['Name'] = fff['account']
                tmp['InteractioNum'] = fff['total']
                tops = list(friendtopic.objects.filter(father = fff['id']).values('topics','pp'))
                tops.sort(key=lambda x: x['pp'])
                tops.reverse()
                nowpp = 0.0
                topcnt = 1
                tmp['Tag1'] = ''
                tmp['Num1'] = 0.0
                tmp['Tag2'] = ''
                tmp['Num2'] = 0.0
                tmp['Tag3'] = ''
                tmp['Num3'] = 0.0
                for top in tops[:3]:
                    tmp['Tag' + str(topcnt)] = top['topics']
                    tmp['Num' + str(topcnt)] = top['pp']
                    nowpp += top['pp']
                    topcnt+=1
                tmp['NumN'] = fff['total'] - nowpp
                res.append(tmp)
            result['interactions'] = res
        else :
            result['verdict'] = 'error'
            result['message'] = 'FUCK YOU'
    else :
        result['verdict'] = 'error'
        result['message'] = 'Please log in first!'
    return JsonResponse(result)

