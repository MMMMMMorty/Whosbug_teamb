from django.contrib import admin

from mainapp import models
admin.site.register(models.app)
admin.site.register(models.file)
admin.site.register(models.function)
admin.site.register(models.commit)
admin.site.register(models.modifiedfunction)
