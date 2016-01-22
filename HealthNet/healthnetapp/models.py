from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.contrib import admin #unused
import datetime #unused

class UserStatus(models.Model):
	username = models.CharField(max_length=30, default = 'default')
	type = models.CharField(max_length=20, default = '')
	patient = models.BooleanField(default = False)
	
class PatientProfile(models.Model):
	username = models.CharField(max_length=30, default = 'default')
	firstname = models.CharField(max_length=20, default = 'default')
	lastname = models.CharField(max_length=40, default = 'default')
	email = models.EmailField(max_length = 50, default = 'default@gmail.com')
	phone = models.CharField(max_length=20, default = '(111) 111-1111')
	birth = models.DateField('Birth Date', default = date.today)
	address = models.CharField(max_length=50, default = '111 11th Avenue, New York, NY 10001')
	prefered = models.CharField(max_length=20, default = 'none selected')
	def copy(self, temp):
		self.firstname = temp.firstname
		self.lastname = temp.lastname
		self.email = temp.email
		self.phone = temp.phone
		self.birth = temp.birth
		self.address = temp.address
		self.prefered = temp.prefered
	def __str__(self):
		return self.username

class MedicalInfo(models.Model):
	username = models.CharField(max_length=30, default = 'default')
	emergency = models.CharField(max_length=50, default = '(222) 222-2222')
	ssn = models.CharField(max_length=11, default = '111-11-1111')
	insurance = models.CharField(max_length=20, default = '11-111-1111-1')
	provider = models.CharField(max_length=20, default = 'MedCorp Inc.')
	conditions = models.TextField(max_length=10000, blank=True, default = '')
	perscriptions = models.TextField(max_length=10000, blank=True, default = '')
	results = models.TextField(max_length=10000, blank=True, default = '')
	currenthospital = models.CharField(max_length=20, default = 'none')
	def copy(self,temp):
		self.ssn = temp.ssn
		self.insurance = temp.insurance
		self.provider = temp.provider
		self.emergency = temp.emergency
		self.conditions = temp.conditions
		self.perscriptions = temp.perscriptions
		self.results = temp.results
		self.currenthospital = temp.currenthospital
		
class DoctorProfile(models.Model):
	username = models.CharField(max_length=30, default = 'default')#same thing as above
	firstname = models.CharField(max_length=20, default = 'default')
	lastname = models.CharField(max_length=40, default = 'default')
	email = models.EmailField(max_length = 50, default = 'default@gmail.com')
	degree = models.CharField(max_length=200, default = 'Ph.D.')
	profession = models.CharField(max_length=200, default = 'Surgeon')
	birth = models.DateField('Birth Date', default = date.today)
	phone = models.CharField(max_length=20, default = '(111) 111-1111')
	address = models.CharField(max_length=50, default = '111 11th Avenue, New York, NY 10001')
	prefered = models.CharField(max_length=20, default = 'none selected')
	def __str__(self):
		return self.username
	def copy(self, temp):
		self.firstname = temp.firstname
		self.lastname = temp.lastname
		self.email = temp.email
		self.phone = temp.phone
		self.birth = temp.birth
		self.degree = temp.degree
		self.profession = temp.profession
		self.address = temp.address
		self.prefered = temp.prefered

class NurseProfile(models.Model):
	username = models.CharField(max_length=30, default = 'default')#same thing as above
	firstname = models.CharField(max_length=20, default = 'default')
	lastname = models.CharField(max_length=40, default = 'default')
	email = models.EmailField(max_length = 50, default = 'default@gmail.com')
	birth = models.DateField('Birth Date', default = date.today)
	phone = models.CharField(max_length=20, default = '(111) 111-1111')
	address = models.CharField(max_length=50, default = '111 11th Avenue, New York, NY 10001')
	prefered = models.CharField(max_length=20, default = 'none selected')
	workhospital = models.CharField(max_length=20, default = 'none selected')
	def __str__(self):
		return self.username
	def copy(self, temp):
		self.firstname = temp.firstname
		self.lastname = temp.lastname
		self.email = temp.email
		self.phone = temp.phone
		self.birth = temp.birth
		self.address = temp.address
		self.prefered = temp.prefered

class SecretaryProfile(models.Model):
	username = models.CharField(max_length=30, default = 'default')#same thing as above
	firstname = models.CharField(max_length=20, default = 'default')
	lastname = models.CharField(max_length=40, default = 'default')
	email = models.EmailField(max_length = 50, default = 'default@gmail.com')
	birth = models.DateField('Birth Date', default = date.today)
	phone = models.CharField(max_length=20, default = '(111) 111-1111')
	address = models.CharField(max_length=50, default = '111 11th Avenue, New York, NY 10001')
	prefered = models.CharField(max_length=20, default = 'none selected')
	def copy(self, temp):
		self.firstname = temp.firstname
		self.lastname = temp.lastname
		self.email = temp.email
		self.phone = temp.phone
		self.birth = temp.birth
		self.address = temp.address
		self.prefered = temp.prefered
		
class ManagerProfile(models.Model):
	username = models.CharField(max_length=30, default = 'default')#same thing as above
	firstname = models.CharField(max_length=20, default = 'default')
	lastname = models.CharField(max_length=40, default = 'default')
	email = models.EmailField(max_length = 50, default = 'default@gmail.com')
	birth = models.DateField('Birth Date', default = date.today)
	phone = models.CharField(max_length=20, default = '(111) 111-1111')
	address = models.CharField(max_length=50, default = '111 11th Avenue, New York, NY 10001')
	prefered = models.CharField(max_length=20, default = 'none selected')
	def copy(self, temp):
		self.firstname = temp.firstname
		self.lastname = temp.lastname
		self.email = temp.email
		self.phone = temp.phone
		self.birth = temp.birth
		self.address = temp.address
		self.prefered = temp.prefered
		
class AdminProfile(models.Model):
	username = models.CharField(max_length=30, default = 'default')#same thing as above
	firstname = models.CharField(max_length=20, default = 'default')
	lastname = models.CharField(max_length=40, default = 'default')
	email = models.EmailField(max_length = 50, default = 'default@gmail.com')
	birth = models.DateField('Birth Date', default = date.today)
	phone = models.CharField(max_length=20, default = '(111) 111-1111')
	address = models.CharField(max_length=50, default = '111 11th Avenue, New York, NY 10001')
	prefered = models.CharField(max_length=20, default = 'none selected')
	def copy(self, temp):
		self.firstname = temp.firstname
		self.lastname = temp.lastname
		self.email = temp.email
		self.phone = temp.phone
		self.birth = temp.birth
		self.address = temp.address
		self.prefered = temp.prefered
		
class Entry(models.Model):
	date = models.DateField(blank=True, default = '1111-01-01')
	time = models.CharField(max_length=4, default = '8am')
	owner = models.CharField(max_length=30, default = 'default')
	doctor = models.CharField(max_length=40, default = 'must select')
	reason = models.TextField(max_length=10000, blank=True, default = 'must add reason for visit')
	approved = models.BooleanField(default = False)
	cancel = models.BooleanField(default = False)
	submitted = models.BooleanField(default = False)
	idtag = models.CharField(max_length=10000, default = 'must select')
	def setid(self):
		self.idtag = str(self.date) + "," + str(self.time) + "," + str(self.owner)
		
class Hospital(models.Model):
	name = models.CharField(max_length=100, default = '')
	address = models.CharField(max_length=100, default = '')
	phone = models.CharField(max_length=100, default = '')
	email = models.EmailField(max_length = 50, default = 'default@gmail.com')
	hours = models.CharField(max_length=100, default = '')

class Message(models.Model):
	message = models.TextField(max_length=500, default = '')
	sender = models.CharField(max_length=30, default = 'default')
	reciever = models.CharField(max_length=30, default = 'default')
		
class Log(models.Model):
	type = models.CharField(max_length=30, default = 'default')
	username = models.CharField(max_length=30, default = 'default')
	event_time = models.DateTimeField(auto_now_add=True)
	def __str__(self):
		return(self.type + " : " + self.username)
	