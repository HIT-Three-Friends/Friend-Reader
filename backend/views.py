from django.shortcuts import render
from django.http import JsonResponse
from backend.models import users,friends
from django.views.decorators.csrf import csrf_protect
from PIL import Image

# Create your views here.
def testfuck(request):
    return render(request, 'testindex.html')

@csrf_protect
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

def logout(request):
    del request.session["username"]
    result = {'verdict':'success','message':'Successful'}
    return JsonResponse(result)

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

def friend(request,id):
    result = {'verdict': 'success', 'message': 'Successful'}
    username = request.session['username']
    userinfo = users.objects.filter(username=username)
    # 是否在线
    result['method'] = request.method
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

def socials(request,friendid):
    if request.method == 'GET':
        result = {'verdict': 'success', 'message': 'Successful'}
        result['verdict'] = 'success'
        return JsonResponse(result)
    else:
        platform = request.POST['platform']
        account = request.POST['account']
        platform = str(platform)
        account = str(account)
        result = {'verdict': 'success', 'message': 'Successful'}
        result['verdict'] = 'success'
        return JsonResponse(result)

def social(request,friend,socialid):
    if request.method == 'GET':
        platform = ''
        account = ''
        result = {'platform': platform, 'account': account, 'verdict': 'success', 'message': 'Successful'}
        result['verdict'] = 'success'
        return JsonResponse(result)
    elif request.method == 'PUT':
        platform = request.POST['platform']
        account = request.POST['account']
        platform = str(platform)
        account = str(account)
        result = {'verdict': 'success', 'message': 'Successful'}
        result['verdict'] = 'success'
        return JsonResponse(result)
    else:
        result = {'verdict': 'success', 'message': 'Successful'}
        result['verdict'] = 'success'
        return JsonResponse(result)