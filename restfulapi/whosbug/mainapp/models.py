from django.db import models

class app(models.Model):
    appid = models.AutoField(primary_key = True)
    appname = models.CharField(max_length=30)
    class Meta:
        db_table = 'app'
    def __str__(self):
        return self.appname

class file(models.Model):
    fileid = models.AutoField(primary_key = True)
    filename = models.CharField(max_length=200)
    appid = models.ForeignKey('app',on_delete=models.CASCADE,default=1)
    class Meta:
        db_table = 'file'
    def __str__(self):
        return "{}: {}".format(str(self.appid),self.filename)

class function(models.Model):
    functionid = models.AutoField(primary_key = True)
    fileid = models.ForeignKey('file',on_delete=models.CASCADE)
    functionname = models.CharField(max_length=200)
    class Meta:
        db_table = 'function'
    def __str__(self):
        return "{}: {}".format(str(self.fileid),self.functionname)

class commit(models.Model):
    commitpk=models.AutoField(primary_key = True)
    commitid = models.CharField(max_length=45)  
    version = models.CharField(max_length=10)
    appid = models.ForeignKey('app',on_delete=models.CASCADE)
    committername = models.CharField(max_length=50)
    committeremail = models.CharField(max_length=70)
    tree = models.CharField(max_length=40)
    parent = models.CharField(max_length=125)
    message = models.CharField(max_length=400)
    time = models.CharField(max_length=30)
    timezone = models.CharField(max_length=7)
    class Meta:
        db_table = 'commit'
    def __str__(self):
        return "{}：{}版, 提交者:{}, {}".format(str(self.appid),self.version,self.committername, self.commitid)

class modifiedfunction(models.Model):
    appid = models.ForeignKey('app',on_delete=models.CASCADE,default=1)
    functionid = models.ForeignKey('function',on_delete=models.CASCADE)
    fileid = models.ForeignKey('file',on_delete=models.CASCADE)
    commitpk = models.ForeignKey('commit',on_delete=models.CASCADE)
    time = models.CharField(max_length=30)
    lines = models.CharField(max_length=400)
    version = models.CharField(max_length=10)
    functionscale = models.CharField(max_length=17)
    functionerror = models.CharField(max_length=200)
    class Meta:
        db_table = 'modifiedfunction'
    def __str__(self):
        return "{}版本 {}".format(self.version,str(self.functionid))
