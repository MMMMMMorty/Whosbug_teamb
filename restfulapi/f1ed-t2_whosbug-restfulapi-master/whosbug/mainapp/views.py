from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.contrib.auth import authenticate, login
from django.shortcuts import render_to_response
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework.response import Response
from .models import app, file, function, commit, modifiedfunction
from .serializers import modifiedfunctionModelSerializer2,appModelSerializer, fileModelSerializer, functionModelSerializer, commitModelSerializer, commitSerializers, modifiedfunctionModelSerializer
from django.db.models import Q
import json

# 任何Viewset的会被添加到路由
# class appViewSet(viewsets.ModelViewSet):
    # 指定结果集并设置排序
    # queryset = app.objects.all()
    # 指定序列化的类
    # serializer_class = appSerializers

def Paginate(cur, perpage, list):
    """
    args: ALL NOT NULL
    """
    try:
        paginator = Paginator(list, perpage)
        Page = paginator.get_page(cur)
    except PageNotAnInteger:
        Page = paginator.get_page(1)
    except EmptyPage:
        Page = paginator.get_page(paginator.num_pages)
    return Page.object_list, paginator.num_pages, paginator.count


def checkParams(params, exParams):
    """
    检查request的参数是否全部给全
    :param _model: fields:待检查字段  ex_fields:不在检查范围内的字段，比如外键
    :param params:
    :return: True,'' / False, key
    """
    if params:
        reqParams = list(params.keys())
    else:
        return False, 'all'

    lost = []
    for key in exParams:
        if key not in reqParams:
            lost.append(key)
        elif params[key] == 'None':
            lost.append(key)
    if len(lost) == 0:
        return True, ''
    else:
        return False, lost

class LoginView(View):
    def get(self,request):
        return render(request,'login.html')

    def post(self,request):#是post请求取出form表单中传过来的用户名和密码
        # login_form=LoginForm(request.POST)#实列化Login_Form传入request.POST字典
        user_name=request.POST.get('username','')
        pass_word=request.POST.get('password','')
        user=authenticate(username=user_name,password=pass_word)
        #调用authenticate方法来验证用户名和密码合法性。
        # authenticate方法验证合法返回user对象，不合法返回None
        if user is not None:
            login(request,user) #调用login函数登陆
            return render(request,'index.html')
        else:#当user对象用户名密码不正确返回login页面，
            context={ 'error_msg':'密码或账号错误'}
            return render(request,'login.html',context)

@api_view(['GET','PATCH'])
@login_required
def getPatchApp(request, pappname):
    appobj = app.objects.filter(appname=pappname)
    if appobj.exists():
        appobj=appobj[0]
        print("appname exist!")
        pappid = appobj.appid
    else:
        resobj = {"code":404, "error":{"message":"appname {} 不存在".format(pappname)}}
        return Response(resobj, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        appSerialize=appModelSerializer(appobj)
        # resobj={"message":"查找成功","result":appSerialize.data}
        return Response(appSerialize.data, status=status.HTTP_200_OK)
    else:
        request_dict =json.loads(request.body.decode('utf-8'))
        if request_dict.get('appname') is None:
            resobj = {"code":422,"error":{ "message":"未传入需要修改的属性或属性有误！","editable_poperties":['appname']}}
            ResponseObj = Response(resobj, status=422)
            ResponseObj.reason_phrase="UNPROCESSABLE ENTITY"
            return ResponseObj
        else:
            limitname=request_dict.get('appname')
            limitname=limitname[:30]
            limitappobj=app.objects.filter(appname=limitname)
            if limitappobj.exists():
                resobj = {"code":409, "error":{"message":"appname {} 已经存在".format(limitname)}}
                return Response(resobj, status=status.HTTP_409_CONFLICT)
            appobj.appname=limitname
            appobj.save()
            appSerialize=appModelSerializer(appobj)
            ResponseObj= Response(appSerialize.data, status=301)
            ResponseObj.reason_phrase="MOVE PEMANENTLY"
            return ResponseObj

@login_required
@api_view(['GET'])
def getAllApps(request):
    appobj = app.objects.all()
    if appobj.exists():
        if not request.GET.get('page') is None:
            page = request.GET.get('page')
        else:
            page = 1
        if not request.GET.get('per_page') is None:
            per_page= request.GET.get('per_page')
        else:
            per_page=10
        res, pages_num,count=Paginate(page,per_page,appobj)
        objSerializeList = []
        for obj in res:
           appSerialize=appModelSerializer(obj)
           objSerializeList.append(appSerialize.data) 
        resobj={"apps":objSerializeList,"total_objects": count,"objects_per_page":per_page, "total_pages":pages_num}
        return Response(resobj, status=status.HTTP_200_OK)
    else:
        resobj = {"apps": [], "total_objects": 0,"objects_per_page":0, "total_pages": 0}
        return Response(resobj, status=status.HTTP_200_OK)

@api_view(['GET','PATCH'])
@login_required
def getPatchFile(request, pappname, pfilename):
    appobj = app.objects.filter(appname=pappname)
    if appobj.exists():
        appobj=appobj[0]
        pappid = appobj.appid
    else:
        resobj = {"code":404,"error":{"message":"appname {} 不存在".format(pappname)}}
        return Response(resobj, status=status.HTTP_404_NOT_FOUND)
    fileobj = file.objects.filter( Q(appid = pappid) & Q(filename = pfilename))
    if fileobj.exists():
        fileobj = fileobj[0]
        pfileid = fileobj.fileid
    else:
        resobj = {"code":404,"error":{"message":"{}项目下的{}文件不存在".format(appobj.appname,pfilename)}}
        return Response(resobj, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        fileSerialize=fileModelSerializer(fileobj)
        resobj={"message":"查找成功","result":fileSerialize.data}
        return Response(fileSerialize.data, status=status.HTTP_200_OK)
    else:
        request_dict =json.loads(request.body.decode('utf-8'))
        if request_dict.get('filename') is None:
            resobj = {"code":422,"error":{"message":"未传入需要修改的属性或属性有误！","editable_poperties":['appname']}}
            ResponseObj = Response(resobj, status=422)
            ResponseObj.reason_phrase = "UNPROCESSABLE ENTITY"
            return ResponseObj
        else:
            limitname=request_dict.get('filename')
            limitname=limitname[:130]
            limitfileobj = file.objects.filter( Q(appid = pappid) & Q(filename = limitname))
            if limitfileobj.exists():
                resobj = {"code":409, "error":{"message":"appname {} 中的filename {} 已经存在".format(pappname,limitname)}}
                return Response(resobj, status=status.HTTP_409_CONFLICT)
            fileobj.filename=limitname
            fileobj.save()
            fileSerialize=fileModelSerializer(fileobj)
            ResponseObj= Response(fileSerialize.data, status=301)
            ResponseObj.reason_phrase="MOVE PEMANENTLY"
            return ResponseObj

@login_required
@api_view(['GET'])
def getAllFiles(request, pappname):
    appobj = app.objects.filter(appname=pappname)
    if appobj.exists():
        appobj = appobj[0]
        pappid = appobj.appid
    else:
        resobj = {"code":404,"error":{"message": "appname {} 不存在".format(pappname)}}
        return Response(resobj, status=status.HTTP_404_NOT_FOUND)
    fileobj = file.objects.filter(appid=pappid)
    if fileobj.exists():
        if not request.GET.get('page') is None:
            page = request.GET.get('page')
        else:
            page = 1
        if not request.GET.get('per_page') is None:
            per_page= request.GET.get('per_page')
        else:
            per_page=10
        res, pages_num,count=Paginate(page,per_page,fileobj)
        appSerialize = appModelSerializer(appobj)
        objSerializeList = []
        for obj in res:
            fileSerialize = fileModelSerializer(obj)
            fileSerialize.data["appid"] = appSerialize.data
            objSerializeList.append(fileSerialize.data)
        resobj = {"files": objSerializeList, "total_objects": count, "objects_per_page":per_page, "total_pages": pages_num}
        return Response(resobj, status=status.HTTP_200_OK)
    else:
        resobj = {"files": [], "total_objects": 0,"objects_per_page":0, "total_pages": 0}
        return Response(resobj, status=status.HTTP_200_OK)


@login_required
@api_view(['GET'])
def getAllCommits(request, pappname):
    appobj = app.objects.filter(appname=pappname)
    if appobj.exists():
        appobj = appobj[0]
        pappid = appobj.appid
    else:
        resobj = {"code":404,"error":{"message": "appname {} 不存在".format(pappname)}}
        return Response(resobj, status=status.HTTP_404_NOT_FOUND)
    commitobj = commit.objects.filter(appid=pappid)
    if commitobj.exists():
        if not request.GET.get('page') is None:
            page = request.GET.get('page')
        else:
            page = 1
        if not request.GET.get('per_page') is None:
            per_page= request.GET.get('per_page')
        else:
            per_page=10
        res, pages_num,count=Paginate(page,per_page,commitobj)
        appSerialize = appModelSerializer(appobj)
        objSerializeList = []
        for obj in res:
            commitSerialize = commitModelSerializer(obj)
            commitSerialize.data["appid"] = commitSerialize.data
            objSerializeList.append(commitSerialize.data)
        resobj = {"files": objSerializeList, "total_objects": count, "objects_per_page":per_page, "total_pages": pages_num}
        return Response(resobj, status=status.HTTP_200_OK)
    else:
        resobj = {"files": [], "total_objects": 0,"objects_per_page":0, "total_pages": 0}
        return Response(resobj, status=status.HTTP_200_OK)

@api_view(['GET','PATCH'])
@login_required
def getPatchFunction(request, pappname, pfilename, pfunctionname):
    appobj = app.objects.filter(appname=pappname)
    if appobj.exists():
        appobj=appobj[0]
        pappid = appobj.appid
    else:
        resobj = {"code":404,"error":{"message": "appname {} 不存在".format(pappname)}}
        return Response(resobj, status=status.HTTP_404_NOT_FOUND)
    fileobj = file.objects.filter( Q(appid = pappid) & Q(filename = pfilename))
    if fileobj.exists():
        fileobj = fileobj[0]
        pfileid = fileobj.fileid
    else:
        resobj = {"code":404,"error":{"message":"{}项目下的{}文件不存在".format(appobj.appname,pfilename)}}
        return Response(resobj, status=status.HTTP_404_NOT_FOUND)
        appobj = app.objects.filter(appname=pappname)
    functionobj = function.objects.filter( Q(fileid = pfileid) & Q(functionname = pfunctionname))
    if functionobj.exists():
        functionobj = functionobj[0]
        pfunctionid = functionobj.functionid
    else:
        resobj = {"code":404,"error":{"message":"{}项目下的{}文件中的{}函数不存在".format(appobj.appname,pfilename,pfunctionname)}}
        return Response(resobj, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        functionSerialize=functionModelSerializer(functionobj)
        # resobj={"message":"查找成功","result":functionSerialize.data}
        return Response(functionSerialize.data, status=status.HTTP_200_OK)
    else:
        request_dict =json.loads(request.body.decode('utf-8'))
        if request_dict.get('functionname') is None:
            resobj = {"code":422,"error":{"message":"未传入需要修改的属性或属性有误！","editable_poperties":['functionname']}}
            ResponseObj = Response(resobj, status=422)
            ResponseObj.reason_phrase = "UNPROCESSABLE ENTITY"
            return ResponseObj
        else:
            limitname=request_dict.get('functionname')
            limitname=limitname[:100]
            limitfunctionobj = function.objects.filter( Q(fileid = pfileid) & Q(functionname =limitname))
            if limitfunctionobj.exists():
                resobj = {"code":409, "error":{"message":"appname {} 中{} 文件下 {} 函数已经存在".format(pappname,pfilename,limitname)}}
                return Response(resobj, status=status.HTTP_409_CONFLICT)                
            functionobj.functionname=limitname
            functionobj.save()
            functionSerialize=functionModelSerializer(functionobj)
            ResponseObj= Response(functionSerialize.data, status=301)
            ResponseObj.reason_phrase="MOVE PEMANENTLY"
            return ResponseObj


@api_view(['GET','PATCH'])
@login_required
def getFunctionCommits(request, pappname, pfilename, pfunctionname):
    appobj = app.objects.filter(appname=pappname)
    if appobj.exists():
        appobj=appobj[0]
        pappid = appobj.appid
    else:
        resobj = {"code":404,"error":{"message": "appname {} 不存在".format(pappname)}}
        return Response(resobj, status=status.HTTP_404_NOT_FOUND)
    fileobj = file.objects.filter( Q(appid = pappid) & Q(filename = pfilename))
    if fileobj.exists():
        fileobj = fileobj[0]
        pfileid = fileobj.fileid
    else:
        resobj = {"code":404,"error":{"message":"{}项目下的{}文件不存在".format(appobj.appname,pfilename)}}
        return Response(resobj, status=status.HTTP_404_NOT_FOUND)
        appobj = app.objects.filter(appname=pappname)
    functionobj = function.objects.filter( Q(fileid = pfileid) & Q(functionname = pfunctionname))
    if functionobj.exists():
        functionobj = functionobj[0]
        pfunctionid = functionobj.functionid
    else:
        resobj = {"code":404,"error":{"message":"{}项目下的{}文件中的{}函数不存在".format(appobj.appname,pfilename,pfunctionname)}}
        return Response(resobj, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        mfobjs=modifiedfunction.objects.filter(appid=appobj,fileid=fileobj,functionid=functionobj)
        if mfobjs.exists():
            mflist=[]
            for mf in mfobjs:
                s = modifiedfunctionModelSerializer(mf)
                mflist.append(s.data)
            return Response(mflist, status=status.HTTP_200_OK)
        else:
            resobj = {"code": 404,"error": {"message": "{}函数没有修改记录".format(pfunctionname)}}
            return Response(resobj, status=status.HTTP_404_NOT_FOUND)




@api_view(['GET'])
@login_required
def getAllFunctions(request, pappname, pfilename):
    appobj = app.objects.filter(appname=pappname)
    if appobj.exists():
        appobj = appobj[0]
        pappid = appobj.appid
    else:
        resobj = {"code":404,"error":{"message": "appname {} 不存在".format(pappname)}}
        return Response(resobj, status=status.HTTP_404_NOT_FOUND)
    fileobj = file.objects.filter(filename=pfilename, appid=appobj)
    if fileobj.exists():
        fileobj = fileobj[0]
        pfileid = fileobj.fileid
    else:
        msg = "appname {} 中的filename {} 不存在".format(pappname, pfilename)
        resobj = {"code":404,"error":{"message": msg}}
        return Response(resobj, status=status.HTTP_404_NOT_FOUND)
    if request.GET.get("keyword") is None:
        functionobj = function.objects.filter(fileid=pfileid)
    else:
        keyword=request.GET.get("keyword")
        functionobj = function.objects.filter(Q(fileid=pfileid)&Q(functionname__icontains=keyword))
    if functionobj.exists():
        if not request.GET.get('page') is None:
            page = request.GET.get('page')
        else:
            page = 1
        if not request.GET.get('per_page') is None:
            per_page = request.GET.get('per_page')
        else:
            per_page = 10
        res, pages_num,count = Paginate(page, per_page, functionobj)
        objSerializeList = []
        for obj in res:
            functionSerialize = functionModelSerializer(obj)
            objSerializeList.append(functionSerialize.data)
        resobj = {"functions": objSerializeList, "total_objects": count, "objects_per_page":per_page, "total_pages": pages_num}
        return Response(resobj, status=status.HTTP_200_OK)
    else:
        resobj = {"functions": [], "total_objects": 0, "objects_per_page":0, "total_pages": 0}
        return Response(resobj, status=status.HTTP_200_OK)

def numListToString(list):
    str3 = ', '
    seq5 = []
    for i in range(len(list)):
        seq5.append(str(list[i]))
    print(str3.join(seq5))
    return str3.join(str(i) for i in seq5)

@api_view(['POST','GET'])
def getPostCommit(request):
    if request.method == 'POST':
        request_arr = request.data
        rewrite_commitid=[]
        if len(request_arr) ==  0:
            resobj={"code":400,"error":{"message":"未传递任何数据"}}
            return Response(resobj, status=status.HTTP_400_BAD_REQUEST)
        for request_dict in request_arr:
            exParams = ['commit','committer_name','committer_email','tree','parents','message','committer_time','committer_timezone','diffs']
            checkres, checkkey = checkParams(request_dict, exParams)
            if not checkres:
                if checkkey == 'all':
                    resobj = {"code":400,"error":{"message":"未传递任何参数", "lostkeys":exParams}}
                else:
                    resobj = {"code":400,"error":{"message":"未传递以下参数", "lostkeys":checkkey}}
                return Response(resobj, status=status.HTTP_400_BAD_REQUEST)
            # 获取全部记录
            pcommitid = request_dict.get('commit')
            if not request_dict.get('appname') is None:
                pappname = request_dict.get('appname')
            else:
                pappname = "默认项目名"
            if not request_dict.get('version') is None:
                pversion = request_dict.get('version')
                pversion=pversion[:10]
            else:
                pversion = "1.0"
            pcommittername = request_dict.get('committer_name')
            pcommittername=pcommittername[:50]
            pcommitteremail = request_dict.get('committer_email')
            pcommitteremail=pcommitteremail[:70]
            ptree = request_dict.get('tree')
            pparent = request_dict.get('parents')
            pmessage = request_dict.get('message')
            if len(pmessage) > 390:
                pmessage = pmessage[:389]
            ptime = request_dict.get('committer_time')
            ptimezone = request_dict.get('committer_timezone')
            pdiffs = request_dict.get('diffs')

            # 判断appname 是否存在,存在则取appid,不存在则新建
            appobj = app.objects.filter(appname=pappname)
            if appobj.exists():
                appobj=appobj[0]
                pappid = appobj.appid
            else:
                print("appname not exist!")
                appobj = app.objects.create(appname=pappname)
                pappid = appobj.appid
            print("appid is {}".format(appobj.appid))
            # 判断是否已有COMMIT记录
            commitobj = commit.objects.filter(commitid=pcommitid,appid=pappid)
            if commitobj.exists():
                commitobj=commitobj[0]
                delmfobjs = modifiedfunction.objects.filter(commitpk=commitobj)
                for delmfobj in delmfobjs:
                    delmfobj.delete()
                    print("删除已存在的modifiedfunction in commitpk")
            else:
                commitobj = commit.objects.create(commitid=pcommitid,appid=appobj,version=pversion,committername=pcommittername,committeremail=pcommitteremail,tree=ptree,parent=pparent,message=pmessage,time=ptime,timezone=ptimezone)
                print("创建COMMIT表 {} 成功！".format(pcommitid))
            # Loop diffs and check
            for pdiff in pdiffs:
                pindex = pdiff['index']
                pfilename = pdiff["diff_file"]
                if 'error_message' in pdiff:
                    perrormsg = pdiff['error_message']
                else:
                    perrormsg = ''
                # 取appid = appid and filename=filename的fileid, 不存在则新建
                fileobj = file.objects.filter( Q(appid = pappid) & Q(filename = pfilename))
                if fileobj.exists():
                    fileobj = fileobj[0]
                    print("file {} exist!".format(pfilename))
                    pfileid = fileobj.fileid
                else:
                    print("filename not exist!")
                    fileobj = file.objects.create(filename=pfilename,appid=appobj)
                    pfileid = fileobj.fileid
                print("fileid is {}".format(pfileid))
                if 'diff_content' in pdiff:
                    keys = list(pdiff['diff_content'].keys())
                    for key in keys:
                        # 取fileid=fileid and functionname=functionname的functionid, 不存在则新建
                        pfunctionname = key
                        functionobj = function.objects.filter( Q(fileid = pfileid) & Q(functionname = pfunctionname))
                        if functionobj.exists():
                            functionobj = functionobj[0]
                            print("function {} exist!".format(pfunctionname))
                            pfunctionid = functionobj.functionid
                        else:
                            print("functionname not exist!")
                            functionobj = function.objects.create(functionname=pfunctionname,fileid=fileobj)
                            pfunctionid = functionobj.functionid
                        print("functionid is {}".format(pfunctionid))
                        mfdic = pdiff['diff_content'][key]
                        plines = numListToString(mfdic['lines'])
                        if len(plines) > 390:
                            plines=plines[:389]
                        mfobj = modifiedfunction.objects.create(time=ptime,version=pversion,appid=appobj, fileid=fileobj, functionid=functionobj, lines=plines, commitpk=commitobj, functionscale=mfdic['method_scale'], functionerror=perrormsg)
                        print("创建MODIFIEDFUNCTION表成功!")
                    
                # end of key in keys
            # end of diff in diffs
        # end of request_dict in request_arr
        if len(rewrite_commitid) > 0:
            resobj = {"message":"插入所有记录成功，部分已存在 commit 已被本次提交覆盖", "request_params":request_arr, "rewrited_existed_commit":rewrite_commitid}
        else:
            resobj = {"message":"插入所有记录成功", "request_params":request_arr}

        return Response(resobj, status=status.HTTP_201_CREATED)
    elif request.method == 'GET':
        if request.GET.get('committer') is not None:
            pcommittername = request.GET.get('committer')
            if request.GET.get('app') is not None:
                papp=request.GET.get('app')
                appobj = app.objects.filter(appname=papp)
                if appobj.exists():
                    appobj=appobj[0]
                    print("appname exist!")
                    pappid = appobj.appid
                    commitobj = commit.objects.filter( Q(appid = pappid) & Q(committername = pcommittername)).order_by('-time')
                    filter={"committer":pcommittername,"app":papp}
                else:
                    resobj = {"code":404,"error":{"message":"appname {} 不存在".format(papp)}}
                    return Response(resobj, status=status.HTTP_404_NOT_FOUND)
            else:
                commitobj = commit.objects.filter(committername = pcommittername).order_by('-time')
                filter={"committer":pcommittername}
        else:
            if request.GET.get('app') is not None:
                papp=request.GET.get('app')
                appobj = app.objects.filter(appname=papp)
                if appobj.exists():
                    appobj=appobj[0]
                    print("appname exist!")
                    pappid = appobj.appid
                else:
                    resobj = {"code":404,"error":{"message":"appname {} 不存在".format(papp)}}
                    return Response(resobj, status=status.HTTP_404_NOT_FOUND)
                commitobj = commit.objects.filter(appid = pappid).order_by('-time')
                filter={"app":papp}
            else:
                commitobj = commit.objects.all().order_by('-time')
                filter={}
        if commitobj.exists():
            if not request.GET.get('page') is None:
                page = request.GET.get('page')
            else:
                page = 1
            if not request.GET.get('per_page') is None:
                per_page= request.GET.get('per_page')
            else:
                per_page=10
            res, pages_num,count=Paginate(page,per_page,commitobj)
            objSerializeList = []
            for obj in res:
                commitSerialize=commitModelSerializer(obj)
                objSerializeList.append(commitSerialize.data)
            resobj={"filter":filter,"commits":objSerializeList,"total_objects": count, "objects_per_page":per_page, "total_pages":pages_num}
            return Response(resobj, status=status.HTTP_200_OK)
        else:
            resobj = {"filter":filter,"commits": [], "total_objects": 0,"objects_per_page":0, "total_pages": 0}
            return Response(resobj, status=status.HTTP_200_OK)

@login_required
@api_view(['GET','DELETE'])
def getDeleteCommit(request, pappname,pcommitid):
    appobj = app.objects.filter(appname=pappname)
    if appobj.exists():
        appobj=appobj[0]
        print("appname exist!")
        pappid = appobj.appid
    else:
        resobj = {"code":404,"error":{"message":"appname {} 不存在".format(pappname)}}
        return Response(resobj, status=status.HTTP_404_NOT_FOUND)
    commitobj = commit.objects.filter(appid=pappid,commitid=pcommitid)
    if commitobj.exists():
        commitobj=commitobj[0]
    else:
        resobj = {"code":404, "error":{"message":"commitid {} 不存在".format(pcommitid)}}
        return Response(resobj, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        mfobj = modifiedfunction.objects.filter(commitpk=commitobj.commitpk)
        if mfobj.exists():
            mfarr=[]
            for mfitem in mfobj:
                modifiedfunctionSerialize=modifiedfunctionModelSerializer2(mfitem)
                mfarr.append(modifiedfunctionSerialize.data)
        else:
            mfarr="此 commit 没有函数修改"
        commitSerialize=commitModelSerializer(commitobj)
        return Response({"commit":commitSerialize.data, "related_modified_functions":mfarr}, status=status.HTTP_200_OK)
    else:
        commitobj.delete()
        return Response({"message":"删除 commit:{} 成功".format(pcommitid)}, status=status.HTTP_200_OK)

def findMainProblem(pappid, before_this_commit, functionid_list):
    """
    args:
        function_list in stack (idx big -> near system functions)
    return:
        main_problem_function_id OR None (if no commit changes stack's function)
    """
    print("------------FIND_MAIN_PROBLEM---------------")
    print(pappid)
    print(before_this_commit)
    print(functionid_list)
    latesttime=""
    latestidx = 4
    latestcommitpk=0
    for idx in range(len(functionid_list)):
        if before_this_commit == "None":
            mfobj=modifiedfunction.objects.filter(appid=pappid,functionid=functionid_list[idx]).order_by('-time')
            if mfobj.exists():
                mfobj=mfobj[0]
            else:
                mfobj=None
        else:
            btc = commit.objects.filter(commitid=before_this_commit)
            if btc.exists():
                btc_time = btc[0].time
                mfobj=modifiedfunction.objects.filter(appid=pappid,time__lt=btc_time,functionid=functionid_list[idx]).order_by('-time')
                if mfobj.exists():
                    mfobj=mfobj[0]
                else:
                    mfobj=None
            else:
                mfobj =modifiedfunction.objects.filter(appid=pappid,functionid=functionid_list[idx]).order_by('-time')
                if mfobj.exists():
                    mfobj=mfobj[0]
                else:
                    mfobj=None
        if mfobj is not None:
            if idx == 0:
                latesttime=mfobj.time
                latestidx=0
                latestcommitpk=mfobj.commitpk.commitpk
            else:
                if mfobj.time > latesttime:
                    latesttime=mfobj.time
                    latestidx=idx 
                    latestcommitpk=mfobj.commitpk.commitpk
    # end of searching mf in functionid_list
    print("latesttime:{}, functionid:{}, commitpk:{}".format(latesttime, functionid_list[latestidx], latestcommitpk))
    if not latestidx == 4:
        return functionid_list[latestidx], latesttime, latestcommitpk
    return None, None, None

def computePossibility(pappid,mainpid, functionid_list, mainp_commit_time):
    print("--------------COMPUTE_POSIIBILITY----------")
    commitobjs=commit.objects.filter(appid=pappid,time__lte=mainp_commit_time).order_by('-time')
    nopindex1=4
    nopindex2=4
    for i in range(len(functionid_list)):
        if functionid_list[i] == mainpid:
            mainpindex=i
        else:
            if nopindex1 == 4:
                nopindex1 = i
            else:
                nopindex2 = i
    index1percent=0
    index2percent=0
    count = 0
    result_mf = None
    commit_times=[0]*len(functionid_list)
    for c in commitobjs:
        if count > 40:
            break
        mf_functionids=[]
        mfobjs = modifiedfunction.objects.filter(commitpk=c.commitpk)
        for mf in mfobjs:
            mf_functionids.append(mf.functionid.functionid)
        # now mf_functionids contains those functionid that this commit has changed
        if len(mf_functionids) > 0:
            count=count+1
        else:
            continue
        for mfid in mf_functionids:
            modified_ids = []
            for i in range(len(functionid_list)):
                if functionid_list[i] == mfid:
                    modified_ids.append(i)
            # modified_ids now contains those functionid that this commit has changed and in stack
            # [], [0], [1], [2], [0,1], [0,2], [1,2], [0,1,2]
            if mainpindex in modified_ids:
                print("FIND MAIN_PROBLEM_FUNCTION -0.01 ")
                if result_mf is None:
                    result_mf = mf
                commit_times[mainpindex] = commit_times[mainpindex]+1
                if index1percent > 0:
                    index1percent=index1percent-0.01
                if index2percent > 0:
                    index2percent=index2percent-0.01
            elif nopindex1 in modified_ids:
                print("FIND A&C_PROBLEM_FUNCTION +0.01")
                commit_times[nopindex1] = commit_times[nopindex1]+1
                index1percent=index1percent+0.01
            elif nopindex2 in modified_ids:
                print("FIND A&C_PROBLEM_FUNCTION +0.01")
                commit_times[nopindex2] = commit_times[nopindex2]+1
                index2percent=index2percent+0.01
    respercent = 1 - index1percent-index2percent
    return respercent, commit_times

@login_required
@api_view(['GET','POST'])
@csrf_exempt
def findOwner(request):
    if request.method == 'GET':
        resobj = {"code":405,"error":{"message":"只允许使用 POST 方法"}}
        return Response(resobj, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    if request.method == 'POST':
        request_dict=request.data
        print(request_dict)
        if request_dict.get('appname') is None:
            resobj = {"code":400,"error":{"message":"参数不完整！", "requied_params":['appname','stacks(contain at least 1 file&function)'],"optional_params":['version']}}
            return Response(resobj, status=status.HTTP_400_BAD_REQUEST)
        pappname=request_dict.get('appname')
        if not request_dict.get('version') is None:
            pversion=request_dict.get('version')
        else:
            pversion="1.0"
        # 构建stack
        if request_dict.get('stacks') is None:
            resobj = {"code":400,"error":{"message":"Haven't update crash stacks！", "requied_params":['appname','stacks(contain at least 1 file&function)'],"optional_params":['version']}}
            return Response(resobj, status=status.HTTP_400_BAD_REQUEST)
        pstack=request_dict.get('stacks')
        if not isinstance(pstack, list) or len(pstack) == 0:
            resobj = {"code":400,"error":{"message":"STACK IS EMPTY！", "requied_params":['appname','stacks(contain at least 1 file&function)'],"optional_params":['version']}}
            return Response(resobj, status=status.HTTP_400_BAD_REQUEST)
        if pstack[0].get('file') is None:
            resobj = {"code":400,"error":{"message":"参数不完整！", "requied_params":['appname','stacks(contain at least 1 file&function)'],"optional_params":['version']}}
            return Response(resobj, status=status.HTTP_400_BAD_REQUEST)
        if pstack[0].get('function') is None:
            resobj = {"code":400,"error":{"message":"参数不完整！", "requied_params":['appname','stacks(contain at least 1 file&function)'],"optional_params":['version']}}
            return Response(resobj, status=status.HTTP_400_BAD_REQUEST)
        # 判断appname 是否存在,存在则取appid,不存在则error
        appobj = app.objects.filter(appname=pappname)
        if appobj.exists():
            appobj=appobj[0]
            print("appname exist!")
            pappid = appobj.appid
        else:
            resobj = {"code":404,"error":{"message":"appname {} 不存在".format(pappname)}}
            return Response(resobj, status=status.HTTP_404_NOT_FOUND)
        # loop
        resobj = {"app":pappname, "version":pversion, 'result':[]} 
        functionid_list = []
        for idx in range(len(pstack)):
            stack=pstack[idx]
            pfile = stack["file"]
            pfunction=stack["function"]
            pline=stack["line"]
            # resobj['result'].append({"file":pfile,"function":pfunction})
            fileobj = file.objects.filter(filename=pfile, appid=appobj)
            if fileobj.exists():
                fileobj=fileobj[0]
                print("file {} exist!".format(pfile))
                pfileid = fileobj.fileid
            else:
                # msg = "appname {} 中的filename {} 不存在".format(pappname,pfile)
                # resobj = {"code":404,"error":{"message":msg}}
                # return Response(resobj, status=status.HTTP_404_NOT_FOUND)
                continue
            funobj = function.objects.filter(functionname=pfunction, fileid = fileobj)
            if funobj.exists():
                funobj=funobj[0]
                print("function name {} exist!".format(pfunction))
                pfunctionid = funobj.functionid
            else:
                # msg = "appname {} 中的filename {} 中的function {} 不存在!".format(pappname, pfile, pfunction)
                # resobj = {"code":404,"error":{"message":msg}}
                # return Response(resobj, status=status.HTTP_404_NOT_FOUND)
                continue
            functionid_list.append(pfunctionid)
            # mfobj = modifiedfunction.objects.filter(appid=appobj,fileid=fileobj,functionid=funobj,version__lte=pversion).order_by('-time')
            # if not mfobj.exists():
            #     resobj['result'][idx]["related_commit"] = "未找到该函数的修改记录"
            #     continue
            # if len(mfobj) > 10:
            #     mfobj = mfobj[:10]
            # resobj['result'][idx]["commits_contain_crash_line"] = []
            # resobj['result'][idx]["latest_10_related_commit"] = []
            # for mf in mfobj:
            #     mfSerialize = modifiedfunctionModelSerializer(mf)
            #     if mf.lines is not None:
            #         lineslist=mf.lines.split(", ")
            #         strline = str(pline)
            #         if strline in lineslist:
            #             resobj['result'][idx]["commits_contain_crash_line"].append(mfSerialize.data)
            #     resobj['result'][idx]["latest_10_related_commit"].append(mfSerialize.data)
        # end of loop in pstack
        if len(functionid_list) == 0:
            return Response(resobj, status=status.HTTP_200_OK)
            
        if request_dict.get('before_this_commit') is None:
            mainpid , mainp_commit_time, mainp_commit_pk=findMainProblem(pappid, "None", functionid_list)
        else:
            mainpid , mainp_commit_time,mainp_commit_pk = findMainProblem(pappid, request_dict.get('before_this_commit'), functionid_list)

        if mainpid is not None:
            result_commit=commit.objects.filter(commitpk=mainp_commit_pk)[0]
            print("mainproblem_commit:{}".format(result_commit.commitid))
            print('------------------FIND_MAIN_PRO_OVER--------------')
            print("main_problem_funcid: {}".format(mainpid))
            percentage, commit_times=computePossibility(pappid,mainpid,functionid_list, mainp_commit_time)
            print('------------------CALCULATE_POSIIBILITY_OVER--------------')
            result_func=function.objects.filter(functionid=mainpid)[0]
            print(result_func.functionname)
            result_mf=modifiedfunction.objects.filter(commitpk=mainp_commit_pk, functionid=result_func)[0]
            mfSerialize = modifiedfunctionModelSerializer(result_mf)
            
            #timesobj={}
            #for ididx in range(len(functionid_list)):
            #    idfuncname=function.objects.filter(functionid=functionid_list[ididx])[0].functionname
            #    timesobj[idfuncname]=commit_times[ididx]  
            #resobj['result'].append({"function":result_func.functionname, "owner":result_commit.committername, "possibility": percentage, "function_latest_commit":mfSerialize.data, "latest_30commits_times":timesobj})
            resobj['result'].append({"function":result_func.functionname, "owner":result_commit.committername, "possibility": percentage, "function_latest_commit":mfSerialize.data})
            #resobj['percentage']=percentage
            print(resobj)
        return Response(resobj, status=status.HTTP_200_OK)
