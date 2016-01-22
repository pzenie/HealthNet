from django.contrib import admin
from healthnetapp.models import *
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User

# Register your models here.
admin.site.register(PatientProfile)
admin.site.register(DoctorProfile)
admin.site.register(Entry)
admin.site.register(Hospital)
admin.site.register(NurseProfile)
admin.site.register(Message)
admin.site.register(SecretaryProfile)
admin.site.register(ManagerProfile)
admin.site.register(UserStatus)
admin.site.register(MedicalInfo)
admin.site.register(AdminProfile)

class LogAdmin(admin.ModelAdmin):
	readonly_fields = ('type','username','event_time',)
admin.site.register(Log,LogAdmin)
