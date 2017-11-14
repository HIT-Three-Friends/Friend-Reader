from django.shortcuts import render
from django.http import JsonResponse
from backend.models import users,friends,social
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
from social import social as socialpc
import  time
from PIL import Image

# Create your views here.
def testfuck(request):
    return render(request, 'testindex.html')

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
                avatar = request.FILES.get('avatar','upload/233.png')
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
            avatar = request.FILES.get('avatar', 'upload/233.png')
            if name != 'ljrsb':
                friendinfo.update(name = name)
            if sex != -1:
                friendinfo.update(sex = sex)
            if avatar != 'upload/233.png':
                friendinfo.update(avatar = avatar)
            result['avatar'] = avatar
    else:
        result['verdict'] = 'error'
        result['message'] = 'Please log in first!'
    return JsonResponse(result)
"""
#单个好友所有账号新建 + 列表
def socials(request,friendid):
    result = {'verdict': 'success', 'message': 'Successful'}
    username = request.session.get('username', '')
    userinfo = users.objects.filter(username=username)
    # 是否在线
    if userinfo:
        id = friends.objects.filter(user=username, friendid=friendid).values('id')
        id = int(list(id)[0]['id'])
        if request.method == 'GET':
            ans = social.objects.filter(father = id).values('platform', 'account')
            result['socials'] = list(ans)
        else:
            platform = request.POST['platform']
            account = request.POST['account']
            platform = int(platform)
            account = str(account)
            social.objects.create(father=id, platform = platform,account = account)
            return JsonResponse(result)
    else:
        result['verdict'] = 'error'
        result['message'] = 'Please log in first!'
    return JsonResponse(result)
"""
#单个好友单个社交账号查询 修改 删除
def asocial(request,friendid,socialid):
    result = {'verdict': 'success', 'message': 'Successful'}
    username = request.session.get('username', '')
    userinfo = users.objects.filter(username=username)
    # 是否在线
    if userinfo:
        id = friends.objects.filter(user = username,friendid = friendid).values('id')
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
            social.objects.filter(father=id, platform=socialid).update(account=account)
            return JsonResponse(result)
    else:
        result['verdict'] = 'error'
        result['message'] = 'Please log in first!'
    return JsonResponse(result)

#获取好友动态 全部
def activities(request):
    result = {'verdict': 'success', 'message': 'Successful'}
    plat = ['zhihu','weibo','tieba']
    username = request.session.get('username', '')
    userinfo = users.objects.filter(username=username)
    client = socialpc()
    acts = []
    if userinfo:
        id = friends.objects.filter(user = username).values('id','name','sex','avatar')
        id = list(id)
        for afriend in id:
            account = social.objects.filter(father = afriend['id']).values('platform', 'account')
            account = list(account)
            ans = []
            for ac in account:
                if ac['account'] == "":
                    continue
                if ac['platform'] != 0:
                    continue
                ans = client.getActivities(ac['account'],plat[int(ac['platform'])],10)
                for act in ans:
                    temp = {}
                    temp['name'] = afriend['name']
                    temp['sex'] = afriend['sex']
                    temp['avatar'] = act['avatar_url']
                    temp['t'] = time.mktime(act['time'])
                    temp['date'] = str(act['time'][0])+'-'+str(act['time'][1]) +'-'+str(act['time'][2])
                    temp['time'] = str(act['time'][3])+':'+str(act['time'][4]) +':'+str(act['time'][5])
                    temp['title'] = act['summary']+'<i>'+plat[int(ac['platform'])]+'.com</i>'
                    temp['word'] = act['targetText']
                    temp['url'] = act['source_url']
                    temp['tags'] = act['topics']
                    if act.__contains__('imgs'):
                        temp['pic'] = act['imgs']
                    else:
                        temp['pic'] = []
                    temp['Video'] = []
                    acts.append(temp)
        acts.sort(key=lambda x:x['t'])
        acts.reverse()
        result['activitynum'] = len(acts)
        result['activity'] = acts
    else:
        result['verdict'] = 'error'
        result['message'] = 'Please log in first!'
    return JsonResponse(result)

#获取某个好友动态
def askactivity(username,friendid,num):
    afriend = list(friends.objects.filter(user = username,friendid=friendid).values('id','name','sex','avatar'))[0]
    account = social.objects.filter(father=afriend['id']).values('platform', 'account')
    account = list(account)
    ans = []
    acts = []
    client = socialpc()
    plat = ['zhihu', 'weibo', 'tieba']
    for ac in account:
        if ac['account'] == "":
            continue
        if ac['platform'] != 0:
            continue
        ans = client.getActivities(ac['account'], plat[int(ac['platform'])], num)
        for act in ans:
            temp = {}
            temp['name'] = afriend['name']
            temp['sex'] = afriend['sex']
            temp['avatar'] = act['avatar_url']
            temp['t'] = time.mktime(act['time'])
            temp['G'] = act['time']
            temp['date'] = str(act['time'][0]) + '-' + str(act['time'][1]) + '-' + str(act['time'][2])
            temp['time'] = str(act['time'][3]) + ':' + str(act['time'][4]) + ':' + str(act['time'][5])
            temp['title'] = act['summary'] + '<i>' + plat[int(ac['platform'])] + '.com</i>'
            temp['word'] = act['targetText']
            temp['url'] = act['source_url']
            temp['tags'] = act['topics']
            if act.__contains__('imgs') :
                temp['pic'] = act['imgs']
            else:
                temp['pic'] = []
            temp['Video'] = []
            acts.append(temp)
    acts.sort(key=lambda x: x['t'])
    acts.reverse()
    return acts

def activity(request,friendid):
    result = {'verdict': 'success', 'message': 'Successful'}
    username = request.session.get('username', '')
    userinfo = users.objects.filter(username=username)
    if userinfo:
        ans = askactivity(username,friendid,20)
        result['activitynum'] = len(ans)
        result['activity'] = ans
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
    renum = days[month]
    if (year % 4 == 0 and year % 100 != 4) or year % 400 == 0 :
        renum += 1
    L = [0 for x in range(0,renum)]
    if userinfo:
        tnum = 20
        ans = askactivity(username, friendid, tnum)
        sum = len(ans)
        while (ans[-1]['G'][0] > year or (ans[-1]['G'][0] == year and ans[-1]['G'][1] >= month)) :
            tnum *= 2
            ans = askactivity(username, friendid, tnum)
            if sum == len(ans):
                break
            else:
                sum = len(ans)
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
        ans = askactivity(username, friendid,200)
        for x in ans:
            L[int(x['G'][3])]+=1
        result['vitality'] = L
    else:
        result['verdict'] = 'error'
        result['message'] = 'Please log in first!'
    return JsonResponse(result)

