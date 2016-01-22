from healthnetapp.models import *
from django.contrib.auth.models import User
from django import forms

class UserForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput())
	
	def is_vavlid(self):
		return True
		
	class Meta:
		model = User
		fields = ('username', 'email', 'password')
		
class PatientProfileForm(forms.ModelForm):
	class Meta:
		model = PatientProfile
		fields = ('firstname','lastname','birth','address','phone')
		
class DoctorProfileForm(forms.ModelForm):
	class Meta:
		model = DoctorProfile
		fields = ('firstname','lastname','degree','profession','birth','address')
		
class NurseProfileForm(forms.ModelForm):
	class Meta:
		model = NurseProfile
		fields = ('firstname','lastname','birth','address','phone','workhospital')

class ManagerProfileForm(forms.ModelForm):
	class Meta:
		model = ManagerProfile
		fields = ('firstname','lastname','birth','address','phone')

class SecretaryProfileForm(forms.ModelForm):
	class Meta:
		model = SecretaryProfile
		fields = ('firstname','lastname','birth','address','phone')

class AdminProfileForm(forms.ModelForm):
	class Meta:
		model = AdminProfile
		fields = ('firstname','lastname','birth','address','phone')
		
class MedicalInfoForm(forms.ModelForm):
	class Meta:
		model = MedicalInfo
		fields = ('ssn','insurance','provider','emergency','conditions','perscriptions','results')
		
class MessageForm(forms.ModelForm):
	class Meta:
		model = Message
		fields = ('message',)
		
		
class AppointmentForm(forms.ModelForm):
	class Meta:
		model = Entry
		fields = ('reason','cancel')
