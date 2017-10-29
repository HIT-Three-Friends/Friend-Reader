from django.shortcuts import render
from django.http import JsonResponse
from backend.models import users,friends,social
from django.views.decorators.csrf import csrf_protect
from PIL import Image

# Create your views here.
def testfuck(request):
    return render(request, 'testindex.html')

@csrf_protect
#新建用户
def user(request):
    result = {'verdict': 'success', 'message': 'Successful!'}
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
    userinfo = users.objects.filter(email = email)
    if userinfo:
        result['verdict'] = 'fail'
        result['message'] = 'The email already exits!'
    else:
        users.objects.create(username = username , password = password ,email = email ,friendnum = 0)
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
    username = request.session['username']
    userinfo = users.objects.filter(username=username)
    #是否在线
    if userinfo:
        if request.method == 'GET':
            ans = friends.objects.filter(user = username).values('friendid','name','sex','avatar')
            result['friends'] = list(ans)
        else :
            name = request.POST['name']
            sex = request.POST['sex']
            name = str(name)
            sex = int(sex)
            userof = str(username)
            avatar = request.FILES.get('avatar')
            #新增计数
            friendid = int(userinfo[0]) + 1
            users.objects.filter(username = username).update(friendnum = int(friendid))
            #返回id
            result['id'] = friendid
            #新建好友
            friends.objects.create(user = userof,friendid = friendid,name = name, sex = sex,avatar = avatar)
    else:
        result['verdict'] = 'fail'
        result['message'] = 'Please log in first!'
    return JsonResponse(result)

#单个好友 查询 修改 删除
def friend(request,id):
    result = {'verdict': 'success', 'message': 'Successful'}
    username = request.session['username']
    userinfo = users.objects.filter(username=username)
    # 是否在线
    if userinfo:
        if request.method == 'GET':
            ans = friends.objects.filter(user=username,friendid = id).values('friendid', 'name', 'sex', 'avatar')
            dict2 = list(ans)[0]
            result.update(dict2)
        elif request.method == 'DELETE':
            friends.objects.filter(user=username,friendid = id).delete()
        else:
            name = request.POST['name']
            sex = request.POST['sex']
            name = str(name)
            sex = int(sex)
            userof = str(username)
            avatar = request.FILES.get('avatar')
            friends.objects.filter(user = userof,friendid=id).update(name=name, sex=sex, avatar=avatar)
    else:
        result['verdict'] = 'fail'
        result['message'] = 'Please log in first!'
    return JsonResponse(result)

#单个好友所有账号新建 + 列表
def socials(request,friendid):
    result = {'verdict': 'success', 'message': 'Successful'}
    username = request.session['username']
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
        result['verdict'] = 'fail'
        result['message'] = 'Please log in first!'
    return JsonResponse(result)

#单个好友单个社交账号查询 修改 删除
def asocial(request,friendid,socialid):
    result = {'verdict': 'success', 'message': 'Successful'}
    username = request.session['username']
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
        result['verdict'] = 'fail'
        result['message'] = 'Please log in first!'
    return JsonResponse(result)

