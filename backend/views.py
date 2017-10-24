from django.shortcuts import render
from django.http import JsonResponse
from backend.models import users
from django.views.decorators.csrf import csrf_protect

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
    result = {'verdict':'success','message':'Successful'}
    return JsonResponse(result)

def friend(request,id):
    if request.method == 'GET':
        name = ''
        sex = ''
        avatar = ''
        result = {'id':id ,'name':name ,'sex' : sex , avatar : 'avator','verdict':'success','message':'Successful'}
        result['verdict'] = 'success'
        return JsonResponse(result)
    elif request.method == 'PUT':
        result = {'verdict': 'success', 'message': 'Successful'}
        result['verdict'] = 'success'
        return JsonResponse(result)
    else :
        result = {'verdict': 'success', 'message': 'Successful'}
        result['verdict'] = 'success'
        return JsonResponse(result)

def friends(request):
    if request.method == 'GET':
        result = {'friends': ' ','verdict': 'success', 'message': 'Successful'}
        result['verdict'] = 'success'
        return JsonResponse(result)
    else:
        name = request.POST['name']
        sex = request.POST['sex']
        avatar = request.POST['avatar']
        name = str(name)
        sex = int(sex)
        avatar = str(avatar)
        result = {'friends': ' ', 'verdict': 'success', 'message': 'Successful'}
        result['verdict'] = 'success'
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