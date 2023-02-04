from .models import app, file, function, commit, modifiedfunction
from rest_framework import serializers
import time, datetime

class appSerializers(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = app
        fields = ('appid', 'appname')

class appModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = app
        fields = "__all__"

class fileSerializers(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = file
        fields = ('fileid', 'filename')

class fileModelSerializer(serializers.ModelSerializer):
    appname=serializers.CharField(source='appid.appname')
    # appid=appModelSerializer(source="appid")
    class Meta:
        model = file
        fields = ('fileid','appid','appname','filename')

class functionSerializers(serializers.HyperlinkedModelSerializer):
    filename=serializers.CharField(source='fileid.filename')
    class Meta:
        model = function
        fields = ('functionid', 'fileid', 'filename','functionname')

class functionModelSerializer(serializers.ModelSerializer):
    filename=serializers.CharField(source='fileid.filename')
    class Meta:
        model = function
        fields = ('functionid', 'fileid', 'filename','functionname')

class commitModelSerializer(serializers.ModelSerializer):
    time=serializers.SerializerMethodField()
    appid=serializers.CharField(source='appid.appname')
    class Meta:
        model = commit
        fields = "__all__"
    def get_time(self, obj):
        timeStamp = int(obj.time)
        dateArray = datetime.datetime.utcfromtimestamp(timeStamp)
        otherStyleTime = dateArray.strftime("%Y.%m.%dT%H:%M:%S")
        return otherStyleTime


class commitSerializers(serializers.Serializer):
    class Meta:
        # model = commit
        commitid = serializers.CharField(max_length=40)
        version = serializers.FloatField()
        appid = serializers.IntegerField()
        committername = serializers.CharField(max_length=30)
        committeremail = serializers.CharField(max_length=50)
        tree = serializers.CharField(max_length=40)
        parent = serializers.CharField(max_length=40)
        message = serializers.CharField(max_length=300)
        time = serializers.CharField(max_length=30)
        # fields = '__all__'

class modifiedfunctionModelSerializer(serializers.ModelSerializer):
    changed_lines = serializers.CharField(source='lines')
    detect_function_error = serializers.CharField(source='functionerror')
    committer_name = serializers.CharField(source='commitpk.committername')
    committer_email = serializers.CharField(source='commitpk.committeremail')
    time=serializers.SerializerMethodField()
    tree = serializers.CharField(source='commitpk.tree')
    parent = serializers.CharField(source='commitpk.parent')
    commit_message = serializers.CharField(source='commitpk.message')
    commitid = serializers.CharField(source='commitpk.commitid')

    class Meta:
        model = modifiedfunction
        fields = ('commitid', 'version', 'tree', 'parent','committer_name', 'committer_email','time', 'commit_message','functionscale', 'changed_lines', 'detect_function_error' )
   
    def get_time(self, obj):
        timeStamp = int(obj.time)
        dateArray = datetime.datetime.utcfromtimestamp(timeStamp)
        otherStyleTime = dateArray.strftime("%Y.%m.%dT%H:%M:%S")
        return otherStyleTime

class modifiedfunctionModelSerializer2(serializers.ModelSerializer):
    changed_lines = serializers.CharField(source='lines')
    detect_function_error = serializers.CharField(source='functionerror')
    function_name=serializers.CharField(source='functionid.functionname')
    file_name=serializers.CharField(source='fileid.filename')

    class Meta:
        model = modifiedfunction
        fields = ('file_name','function_name','functionscale', 'changed_lines', 'detect_function_error' )
  
    def get_time(self, obj):
        timeStamp = int(obj.time)
        dateArray = datetime.datetime.utcfromtimestamp(timeStamp)
        otherStyleTime = dateArray.strftime("%Y.%m.%dT%H:%M:%S")
        return otherStyleTime


class modifiedfunctionSerializers(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = modifiedfunction
        fields = ('appid', 'functionid', 'fileid', 'commitid', 'lines')
