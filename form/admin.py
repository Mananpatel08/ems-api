from django.contrib import admin
from .models import RootForm, PersonalDetails, ServiceDetails, ExamDetail

admin.site.register(RootForm)
admin.site.register(PersonalDetails)
admin.site.register(ServiceDetails)
admin.site.register(ExamDetail)