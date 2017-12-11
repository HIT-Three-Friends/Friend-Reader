from django.shortcuts import render
from django.http import JsonResponse
from backend.models import users,friends,social,Picture,allactivity,pics,topic,focus
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
from social import social as socialpc
from datetime import datetime
import  time
from PIL import Image

# Create your views here.
def testfuck(request):
    return render(request, 'testindex.html')

def refresh():
    ac = list(friends.objects.all.values('id'))
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
            friends.objects.filter(user=username,friendid = id).delete()
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
            if (oldaccount == account or account == '' ): return JsonResponse(result)
            social.objects.filter(father=id, platform=socialid).update(account=account)
            initact(id,int(socialid));
            return JsonResponse(result)
    else:
        result['verdict'] = 'error'
        result['message'] = 'Please log in first!'
    return JsonResponse(result)

def dt_to_t(newdatetime):
    c = newdatetime.strftime("%a %b %d %H:%M:%S %Y")
    return time.strptime(c,"%a %b %d %H:%M:%S %Y")

def t_to_dt(newtime):
    c = time.strftime("%a %b %d %H:%M:%S %Y",newtime)
    return datetime.strptime(c, "%a %b %d %H:%M:%S %Y")

#刷新id好友的所有动态
def refreshfriend(id):
    refreshsocial(id,0)
    refreshsocial(id, 1)
    refreshsocial(id, 2)
    return

#刷新id好友的socialid社交账号
def refreshsocial(id,socialid):
    ac = list(social.objects.filter(father=id, platform=socialid).values('id', 'account','time'))[0]
    client = socialpc()
    plat = ['zhihu', 'weibo', 'github']
    if ac['account'] == '':
        return
    mytime = dt_to_t(ac['time'])
    ans = client.getActivities(ac['account'], plat[socialid],100,mytime)
    ans.sort(key=lambda x: x['time'])
    ans.reverse()
    if len(ans) > 0 :
        mytime = t_to_dt(ans[0]['time'])
        social.objects.filter(father=id, platform=socialid).update(time=mytime)
        for act in ans:
            newact = allactivity.objects.create(father=ac['id'], username=act['username'], avatar_url=act['avatar_url'],
                                                headline=act['headline'], time=t_to_dt(act['time']),
                                                actionType=act['actionType'], summary=act['summary'],
                                                targetText=act['targetText'], source_url=act['source_url'])
            newact = newact.id
            if act.__contains__('imgs'):
                for pic in act['imgs']:
                    pics.objects.create(father=newact, imgs=pic)
            if act.__contains__('topics'):
                for top in act['topics']:
                    topic.objects.create(father=newact, topics=top)
    return

#初始化id好友的socialid社交账号
def initact(id,socialid):
    ac = list(social.objects.filter(father=id, platform=socialid).values('id','account'))[0]
    plat = ['zhihu', 'weibo', 'github']
    client = socialpc()
    if ac['account'] == '' :
        return
    ans = client.getActivities(ac['account'], plat[socialid],1000)
    ans.sort(key=lambda x: x['time'])
    ans.reverse()
    social.objects.filter(father=id, platform=socialid).update(time = datetime.now())

    if len(ans) == 0 :
        return
    for act in ans:
        newact = allactivity.objects.create(father = ac['id'],username = act['username'],avatar_url = act['avatar_url'],headline = act['headline'],time = t_to_dt(act['time']),actionType = act['actionType'],summary = act['summary'],targetText = act['targetText'],source_url = act['source_url'])
        newact = newact.id
        if act.__contains__('imgs'):
            for pic in act['imgs']:
                pics.objects.create(father=newact, imgs=pic)
        if act.__contains__('topics'):
            for top in act['topics']:
                topic.objects.create(father=newact, topics=top)
    return


#给定用户名，以及朋友编号，获取所有动态
def askactivity(username,friendid,page):
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
        acts = askactivity(username,friendid,page)
        if (len(acts) >= 10 * page):
            result['activitynum'] = 10
        else:
            result['activitynum'] = max(0,len(acts) - 10 * page + 10)
        result['activity'] = acts[(10 * page - 10):(10 * page)]
    else:
        result['verdict'] = 'error'
        result['message'] = 'Please log in first!'
    return JsonResponse(result)

#获取好友所有动态
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
            acts += askactivity(username,afriend['friendid'],page)
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
            for y in x['tags']:
                if mm.__contains__(y):
                    tmpp[int(mm[y])][1] += 1
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

