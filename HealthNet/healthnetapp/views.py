from django.shortcuts import render, render_to_response, get_object_or_404
from healthnetapp.forms import *
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from healthnetapp.models import *
from datetime import date, datetime, timedelta
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from django.forms.models import modelformset_factory
import time
import calendar as cal


mnames = "January February March April May June July August September October November December".split()
"""
Request is the context for the user (ie username, permission
"""

def index(request):
		"""
		The main site (redirects to login page)
		"""
		return render(request, 'healthnetapp/index.html')
	
def register(request):
	"""
	Registers users
	"""
	#loads various data about user
	context = RequestContext(request)

	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		profile_form = PatientProfileForm(data=request.POST)
		medical_form = MedicalInfoForm(data=request.POST)
		if user_form.is_valid():
			user = user_form.save(commit=False)
			
			user.set_password(user.password)
			user.save()
			
			x = UserStatus()
			x.username = user.username
			x.type = "patient"
			x.patient = True
			x.save()
			
			m = medical_form.save(commit=False)
			m.username = user.username
			m.save()
			
			u = profile_form.save(commit=False)
			u.username = user.username
			u.email = user.email
			u.save()
			
			l = Log()
			l.type = "User registration"
			l.username = user.username
			l.save()
			
			if request.user.is_superuser:
				return render_to_response('healthnetapp/user.html', {}, context)
			return render_to_response('healthnetapp/login.html', {'type':'patient'}, context)
		else:
			return HttpResponse("Form is invalid or username already exists, hit back to try another.")
		
	else:
		user_form = UserForm()
		profile_form = PatientProfileForm()
		medical_form = MedicalInfoForm()
		return render_to_response(
				'healthnetapp/register.html',{'user_form': user_form, 'profile_form': profile_form, 'medical_form': medical_form},context)

def Login(request,type):
	"""
	Logs the user in
	type - determines if the user is staff or patient
	"""
	context = RequestContext(request)

	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']

		user = authenticate(username=username, password=password)

		if user:
			if user.is_active:
				login(request, user)
				
				x = UserStatus.objects.get(username = username)
				if(type == 'patient'):
					x.patient = True
					x.save()
				elif(type == 'staff' and( x.type == 'admin' or x.type == 'doctor' or x.type == 'nurse' or x.type == 'manager' or x.type == 'secretary')):
					x.patient = False
					x.save()
				else:
					return HttpResponse("URL missmatch")
					
				l = Log()
				l.type = "User Login"
				l.username = username
				l.save()
				
				return HttpResponseRedirect('/healthnetapp/user')
			else:
				return HttpResponse("Your Health Net account is disabled.")
		else:
			
			l = Log()
			l.type = "User Login Failed"
			l.username = "?"
			l.save()
			
			return HttpResponse("Invalid login details supplied.")

	else:
		return render_to_response('healthnetapp/login.html', {'type':type}, context)

@login_required
def user_logout(request):
	"""
	Logs the user out
	"""
	l = Log()
	l.type = "User Logout"
	l.username = request.user.username
	l.save()
	
	logout(request)	
	return HttpResponseRedirect('/healthnetapp/')		
		
@login_required
def Main(request):
	"""
	The main homepage for the user logged in
	"""
	context = RequestContext(request)
	if(isPatient(request.user)):
		type = 'patient'
		info = PatientProfile.objects.get(username = request.user.username)
	elif(isAdmin(request.user)):
		type = 'admin'
		info = AdminProfile.objects.get(username = request.user.username)
	elif(isDoctor(request.user)):
		type = 'doctor'
		info = DoctorProfile.objects.get(username = request.user.username)
	elif(isNurse(request.user)):
		type = 'nurse'
		info = NurseProfile.objects.get(username = request.user.username)
	elif(isManager(request.user)):
		type = 'manager'
		info = ManagerProfile.objects.get(username = request.user.username)
	elif(isSecretary(request.user)):
		type = 'secretary'
		info = SecretaryProfile.objects.get(username = request.user.username)
		
	medical = MedicalInfo.objects.get(username = request.user.username)

	dict = {'ProfileInfo':info,'MedicalInfo':medical,'type':type}
	return render_to_response('healthnetapp/user.html', dict , context)
	
@login_required
def calendar(request, year=None):
	"""
	The appointment calendar for the user
	"""
	context = RequestContext(request)
	if year: year = int(year)
	else:    year = time.localtime()[0]

	nowy, nowm = time.localtime()[:2]

	mlst = {'months': [], 'year':year}
	for n, month in enumerate(mnames):
		entry = current = False
		entries = Entry.objects.filter(date__year=nowy, date__month=nowm)

		if entries:
			entry = True
		if year == nowy and n == nowm:
			current = True
		#Code needs to be split	
		mlst['months'].append({'n': n+1,'name': month,'entry': entry,'current': current})
	return render_to_response("healthnetapp/calendar.html", mlst, context)
	
	
@login_required
def month(request, year, month, change=None):
	"""
	Determines the days of the month
	year - the year of the appointment
	month - the month of the appointment
	"""
	month = int(month)
	year = int(year)
	
	nowy, nowm, nowd = time.localtime()[:3]
	c = cal.Calendar(6)
	month_days = c.itermonthdays(year, month)
	week = 0
	lst=[[]]
	
	for day in month_days:
		entries = current = False   # are there entries for this day; current day?
		if day:
			entries = Entry.objects.filter(date__year=year, date__month=month, date__day=day, owner=request.user)
			if day == nowd and year == nowy and month == nowm:
				current = True

		lst[week].append((day, entries, current))
		if len(lst[week]) == 7:
			lst.append([])
			week += 1
	dict = {'year': year, 'month': month, 'user': request.user,'month_days':lst,'mname': month}
	return render_to_response("healthnetapp/month.html", dict)	
	
@login_required
def day(request, year, month, day):
	"""
	Shows the list of hours available for the day
	"""
	lst = {'8am':[],'9am':[],'10am':[],'11am':[],'12pm':[],'1pm':[],'2pm':[],'3pm':[],'4pm':[],'5pm':[],}
	if(isAdmin(request.user) or isNurse(request.user) or isManager(request.user) or isSecretary(request.user)):
		for hour in lst:
			entrylist = Entry.objects.filter(date__year=year, date__month=month, date__day=day,time = hour)
			lst[hour] = entrylist	
	elif(isDoctor(request.user)):
		for hour in lst:
			entrylist = Entry.objects.filter(date__year=year, date__month=month, date__day=day,time = hour,doctor = request.user.username)
			if(len(entrylist) > 1):
				lst[hour] = entrylist[0]
			else:
				lst[hour] =entrylist
	else:
		for hour in lst:
			doclist = list(DoctorProfile.objects.all())
			entrylist = Entry.objects.filter(date__year=year, date__month=month, date__day=day,time = hour)
			if(len(entrylist) > 0):
				for x,entry in enumerate(entrylist):
					for y,doc in enumerate(doclist):
						print(entry.doctor == doc.username)
						if(entry.doctor == doc.username):
							del doclist[y]
						print(doclist)
			lst[hour] = doclist
			
	type = UserStatus.objects.get(username = request.user.username).type
	dict = {'year': year, 'month': month,'day': day, 'list': lst,'type':type}
	return render_to_response("healthnetapp/day.html", dict)
	
@login_required
def appointment(request, year, month, day, hour, doctor, owner):
	"""
	Displays appointment for a day / create an appointment for that day
	year - the year of the appointment
	month - the month of the appointment
	day - the day of the appointment
	hour - the hour of the appointment
	doctor - the doctor selected for the appointment
	owner - the patient of the appointment
	"""
	context = RequestContext(request)
	
	if request.method == 'POST':
		formset = AppointmentForm(data = request.POST)
		if formset.is_valid():
			try:
				if(not(isPatient(request.user))):
					x = Entry.objects.get(date__year=year, date__month=month, date__day=day,time = hour,owner = owner)
				else:
					x = Entry.objects.get(date__year=year, date__month=month, date__day=day,time = hour,owner = request.user.username)
				t = formset.save(commit = False)
				if(t.cancel):
					x.delete()
					l = Log()
					l.type = "Appointment deleted."
					l.username = request.user.username
					l.save()
					return HttpResponseRedirect('/healthnetapp/user/')
				x.reason = t.reason
				x.doctor = doctor
				x.submitted = True
				x.approved = False
				x.setid()
				x.save()
				
				l = Log()
				l.type = "Appointment modification"
				l.username = request.user.username
				l.save()
				
			except:
				x = formset.save(commit = False)
				if(x.cancel):
					x.delete()
					l = Log()
					l.type = "Appointment deleted."
					l.username = request.user.username
					l.save()
					return HttpResponseRedirect('/healthnetapp/user/')
				x.owner = request.user.username
				x.date = date(int(year), int(month), int(day))
				x.time = hour
				x.doctor = doctor
				x.submitted = True
				x.setid()
				x.save()
				
				l = Log()
				l.type = "Appointment Created"
				l.username = request.user.username
				l.save()
				
			return HttpResponseRedirect('/healthnetapp/user/')
		else:
			try:
				x = Entry.objects.get(date__year=year, date__month=month, date__day=day,time = hour,owner = request.user.username,cancel = False)
				formset = AppointmentForm(instance = x)
				doctor = x.doctor
				approved = x.approved
				submitted = x.submitted
			except:
				formset = AppointmentForm()
				approved = False
				submitted = False
			lst = {'user':request.user,'entries':formset, 'year': year, 'month': month, 'day': day, 'hour': hour,'doctor': doctor, 'approved': approved, 'submitted': submitted,'owner':owner}
			return render_to_response("healthnetapp/appointment.html", lst, context)
	else:
		try:
			if(not(isPatient(request.user))):
				x = Entry.objects.get(date__year=year, date__month=month, date__day=day,time = hour,doctor = doctor)
				owner = x.owner
			else:
				x = Entry.objects.get(date__year=year, date__month=month, date__day=day,time = hour,owner = request.user.username)
				owner = x.owner
			formset = AppointmentForm(instance = x)
			doctor = x.doctor
			approved = x.approved
			submitted = x.submitted
		except:
			formset = AppointmentForm()
			approved = False
			submitted = False
		lst = {'user':request.user,'entries':formset, 'year': year, 'month': month, 'day': day, 'hour': hour,'doctor': doctor, 'approved': approved, 'submitted': submitted,'owner':owner}
		return render_to_response("healthnetapp/appointment.html", lst, context)	
	
@login_required
def doclist(request, year, month, day, hour, owner):
	"""
	Displays the list of doctors for appointments
	year - not used but needs to be pased back 
	month - not used but needs to be passed back
	day - not used but needs to be passed back
	hour - not used but needs to be passed back
	owner -  not used but needs to be passed back
	"""
	doclist = list(DoctorProfile.objects.all())
	entrylist = Entry.objects.filter(date__year=year, date__month=month, date__day=day,time = hour)
	for x,entry in enumerate(entrylist):
		for y,doc in enumerate(doclist):
			print(entry.doctor + "    " + doc.username)
			if(entry.doctor == doc.username):
				del doclist[y]
	lst = {'doctors': doclist, 'year': year,'month': month, 'day': day, 'hour': hour, 'owner':owner}
	return render_to_response("healthnetapp/doclist.html", lst)
	
@login_required
def update(request):
	"""
	Updates user information
	"""
	context = RequestContext(request)
	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		profile_form = PatientProfileForm(data=request.POST)
		y = PatientProfile.objects.filter(username = request.user.username)[0]
		tempy = profile_form.save(commit=False)
		y.copy(tempy)
		y.save()
		
		l = Log()
		l.type = "User Info Updated"
		l.username = request.user.username
		l.save()
				
		return HttpResponseRedirect('/healthnetapp/user/')

	else:
		y = PatientProfile.objects.filter(username = request.user.username)[0]
		profile_form = PatientProfileForm(instance = y)
	
		return render_to_response('healthnetapp/update.html',{ 'profile_form': profile_form},context)

def HospitalList(request):
	"""
	Displays the hospitals
	"""
	context = RequestContext(request)
	lst = {'hospitals': Hospital.objects.all()}
	return render_to_response('healthnetapp/hospital_list.html', lst, context)

@login_required
def SelectHospital(request,selected):
	"""
	Selects a preferred hospital for the user
	selected - Hospital selected
	"""
	context = RequestContext(request)
	if(isAdmin(request.user)):
		user = AdminProfile.objects.get(username = request.user.username)
	elif(isDoctor(request.user)):
		user = DoctorProfile.objects.get(username = request.user.username)
	elif(isNurse(request.user)):
		user = NurseProfile.objects.get(username = request.user.username)
	elif(isManager(request.user)):
		user = ManagerProfile.objects.get(username = request.user.username)
	elif(isSecretary(request.user)):
		user = SecretaryProfile.objects.get(username = request.user.username)
	else:
		user = PatientProfile.objects.get(username = request.user.username)
	user.prefered = selected
	user.save()
	return HttpResponseRedirect('/healthnetapp/user/')
	
@login_required	
def registerDoctor(request):
	"""
	Admin registers a doctor profile
	"""
	context = RequestContext(request)
	if request.user.is_superuser:
		
		if request.method == 'POST':
			user_form = UserForm(data=request.POST)
			profile_form = DoctorProfileForm(data=request.POST)
			medical_form = MedicalInfoForm(data=request.POST)
			
			if user_form.is_valid():
				doc = user_form.save(commit=False)
				doc.set_password(doc.password)
				doc.save()
				
				x = UserStatus()
				x.username = doc.username
				x.type = "doctor"
				x.patient = True
				x.save()
				
				m = medical_form.save(commit=False)
				m.username = doc.username
				m.save()
			
				u = profile_form.save(commit=False)
				u.username = doc.username
				u.email = doc.email
				u.save()

				l = Log()
				l.type = "Doctor Registered"
				l.username = request.user.username
				l.save()
			else:
				return HttpResponse("Form is invalid or username already exists, hit back to try another.")
			return render_to_response('healthnetapp/user.html', {}, context)

		else:
			user_form = UserForm()
			profile_form = DoctorProfileForm()
			medical_form = MedicalInfoForm()
			
			return render_to_response(
					'healthnetapp/register_doctor.html',{'user_form': user_form, 'profile_form': profile_form,'medical_form': medical_form},context)
	else:
		return HttpResponse("You are lacking permission to view this page.")

@login_required					
def registerNurse(request):
	"""
	Admin registers a nurse profile
	"""
	context = RequestContext(request)
	if isAdmin(request.user) or isManager(request.user):

		if request.method == 'POST':
			user_form = UserForm(data=request.POST)
			profile_form = NurseProfileForm(data=request.POST)
			medical_form = MedicalInfoForm(data=request.POST)
			
			if user_form.is_valid():
				nurse = user_form.save(commit=False)
				
				nurse.set_password(nurse.password)
				nurse.save()
				
				x = UserStatus()
				x.username = nurse.username
				x.type = "nurse"
				x.patient = True
				x.save()
				
				m = medical_form.save(commit=False)
				m.username = nurse.username
				m.save()
				
				u = profile_form.save(commit=False)
				u.username = nurse.username
				u.email = nurse.email
				u.save()
				
				l = Log()
				l.type = "Nurse Registered"
				l.username = request.user.username
				l.save()
			else:
				return HttpResponse("Form is invalid or username already exists, hit back to try another.")
			return render_to_response('healthnetapp/user.html', {}, context)

		else:
			user_form = UserForm()
			profile_form = NurseProfileForm()
			medical_form = MedicalInfoForm()
		
			return render_to_response(
					'healthnetapp/register_nurse.html',{'user_form': user_form, 'profile_form': profile_form, 'medical_form': medical_form},context)
	else:
		return HttpResponse("You are lacking permission to view this page.")

def registerManager(request):
	"""
	Admin registers a manager profile
	"""
	context = RequestContext(request)
	if isAdmin(request.user) or isManager(request.user):

		if request.method == 'POST':
			user_form = UserForm(data=request.POST)
			profile_form = ManagerProfileForm(data=request.POST)
			medical_form = MedicalInfoForm(data=request.POST)

			if user_form.is_valid():
				manager = user_form.save(commit=False)
				
				manager.set_password(manager.password)
				manager.save()
				
				x = UserStatus()
				x.username = manager.username
				x.type = "manager"
				x.patient = True
				x.save()
				
				m = medical_form.save(commit=False)
				m.username = manager.username
				m.save()
				
				u = profile_form.save(commit=False)
				u.username = manager.username
				u.email = manager.email
				u.save()
				
				l = Log()
				l.type = "Manager Registered"
				l.username = request.user.username
				l.save()
			else:
				return HttpResponse("Form is invalid or username already exists, hit back to try another.")
			return render_to_response('healthnetapp/user.html', {}, context)

		else:
			user_form = UserForm()
			profile_form = ManagerProfileForm()
			medical_form = MedicalInfoForm()
		
			return render_to_response(
					'healthnetapp/register_manager.html',{'user_form': user_form, 'profile_form': profile_form,'medical_form': medical_form},context)
	else:
		return HttpResponse("You are lacking permission to view this page.")
	
def registerSecretary(request):
	"""
	Admin registers a secretary profile
	"""
	context = RequestContext(request)
	if isAdmin(request.user) or isManager(request.user):
		
		if request.method == 'POST':
			user_form = UserForm(data=request.POST)
			profile_form = SecretaryProfileForm(data=request.POST)
			medical_form = MedicalInfoForm(data=request.POST)

			if user_form.is_valid():
				secretary = user_form.save(commit=False)
				
				secretary.set_password(secretary.password)
				secretary.save()
				
				x = UserStatus()
				x.username = secretary.username
				x.type = "secretary"
				x.patient = False
				x.save()
				
				m = medical_form.save(commit=False)
				m.username = secretary.username
				m.save()
				
				u = profile_form.save(commit=False)
				u.username = secretary.username
				u.email = secretary.email
				u.save()
				
				l = Log()
				l.type = "Secretary Registered"
				l.username = request.user.username
				l.save()
			else:
				return HttpResponse("Form is invalid or username already exists, hit back to try another.")
			return render_to_response('healthnetapp/user.html', {}, context)

		else:
			user_form = UserForm()
			profile_form = SecretaryProfileForm()
			medical_form = MedicalInfoForm()
		
			return render_to_response(
					'healthnetapp/register_secretary.html',{'user_form': user_form, 'profile_form': profile_form,'medical_form': medical_form},context)
	else:
		return HttpResponse("You are lacking permission to view this page.")

def registerAdmin(request):
	"""
	Admin registers an admin profile
	"""
	context = RequestContext(request)
	if isAdmin(request.user) or isManager(request.user):
		
		if request.method == 'POST':
			user_form = UserForm(data=request.POST)
			profile_form = AdminProfileForm(data=request.POST)
			medical_form = MedicalInfoForm(data=request.POST)

			if user_form.is_valid():
				admin = user_form.save(commit=False)
				
				a = User.objects.create_superuser(admin.username,admin.email,admin.password)
				a.save()
				
				x = UserStatus()
				x.username = admin.username
				x.type = "admin"
				x.patient = False
				x.save()
				
				m = medical_form.save(commit=False)
				m.username = admin.username
				m.save()
				
				u = profile_form.save(commit=False)
				u.username = admin.username
				u.email = admin.email
				u.save()
				
				l = Log()
				l.type = "Admin Registered"
				l.username = request.user.username
				l.save()
			else:
				return HttpResponse("Form is invalid or username already exists, hit back to try another.")
			return render_to_response('healthnetapp/user.html', {}, context)

		else:
			user_form = UserForm()
			profile_form = AdminProfileForm()
			medical_form = MedicalInfoForm()
		
			return render_to_response(
					'healthnetapp/register_admin.html',{'user_form': user_form, 'profile_form': profile_form,'medical_form': medical_form},context)
	else:
		return HttpResponse("You are lacking permission to view this page.")
		
@login_required
def updatePatient(request,username):
	"""
	Allows staff to update a patient's info
	username - the username of the patient
	"""
	context = RequestContext(request)
	print(request.user.username)
	print(username)
	if not(isPatient(request.user)) or request.user.username == username:
		
		if request.method == 'POST':
			user_form = UserForm(data=request.POST)
			profile_form = PatientProfileForm(data=request.POST)
			y = PatientProfile.objects.get(username = username)
			tempy = profile_form.save(commit=False)
			y.copy(tempy)
			y.save()
			
			try:
				medical_form = MedicalInfoForm(data=request.POST)
				x = MedicalInfo.objects.get(username = username)
				tempx = medical_form.save(commit=False)
				x.copy(tempx)
				x.save()
			except:
				pass
				
			l = Log()
			l.type = "User Info Updated"
			l.username = request.user.username
			l.save()
					
			return HttpResponseRedirect('/healthnetapp/user/')

		else:
			y = PatientProfile.objects.get(username = username)
			profile_form = PatientProfileForm(instance = y)
			if(request.user.username == username):
				return render_to_response('healthnetapp/update_patient.html',{ 'profile_form': profile_form,'username':username},context)
			else:
				x = MedicalInfo.objects.get(username = username)
				medical_form = MedicalInfoForm(instance = x)
				return render_to_response('healthnetapp/update_patient.html',{ 'profile_form': profile_form,'medical_form': medical_form,'username':username},context)
	else:
		return HttpResponse("You are lacking permission to view this page.")
@login_required		
def updateDoctor(request,username):
	"""
	Allows certain staff to update a doctor's info
	username - the username of the doctor
	"""
	context = RequestContext(request)
	if not(isPatient(request.user)):
		
		if request.method == 'POST':
			user_form = UserForm(data=request.POST)
			profile_form = DoctorProfileForm(data=request.POST)
			y = DoctorProfile.objects.get(username = username)
			tempy = profile_form.save(commit=False)
			y.copy(tempy)
			y.save()
			
			try:
				medical_form = MedicalInfoForm(data=request.POST)
				x = MedicalInfo.objects.get(username = username)
				tempx = medical_form.save(commit=False)
				x.copy(tempx)
				x.save()
			except:
				pass
			
			l = Log()
			l.type = "Doctor Info Updated."
			l.username = request.user.username
			l.save()
					
			return HttpResponseRedirect('/healthnetapp/user/')

		else:
			y = DoctorProfile.objects.get(username = username)
			profile_form = DoctorProfileForm(instance = y)
			if(request.user.username == username):
				return render_to_response('healthnetapp/update_doctor.html',{ 'profile_form': profile_form,'username':username},context)
			elif isDoctor(request.user) or isNurse(request.user):
				x = MedicalInfo.objects.get(username = username)
				medical_form = MedicalInfoForm(instance = x)
				return render_to_response('healthnetapp/update_doctor.html',{'username':username,'medical_form':medical_form},context)
			else:
				x = MedicalInfo.objects.get(username = username)
				medical_form = MedicalInfoForm(instance = x)
				return render_to_response('healthnetapp/update_doctor.html',{ 'profile_form': profile_form,'username':username,'medical_form':medical_form},context)
	else:
		return HttpResponse("You are lacking permission to view this page.")
@login_required	
def updateNurse(request,username):
	"""
	Allows certain staff to update a nurse's info
	username - the username of the nurse
	"""
	context = RequestContext(request)
	if not(isPatient(request.user)):
		
		if request.method == 'POST':
			user_form = UserForm(data=request.POST)
			try:
				profile_form = NurseProfileForm(data=request.POST)
				y = NurseProfile.objects.filter(username = username)[0]
				tempy = profile_form.save(commit=False)
				y.copy(tempy)
				y.save()
			except:
				pass
			
			try:
				medical_form = MedicalInfoForm(data=request.POST)
				x = MedicalInfo.objects.get(username = username)
				tempx = medical_form.save(commit=False)
				x.copy(tempx)
				x.save()
			except:
				pass
				
			l = Log()
			l.type = "Nurse Info Updated"
			l.username = request.user.username
			l.save()
			
			return HttpResponseRedirect('/healthnetapp/user/')
		else:
			y = NurseProfile.objects.filter(username = username)[0]
			profile_form = NurseProfileForm(instance = y)
			if(request.user.username == username):
				return render_to_response('healthnetapp/update_nurse.html',{ 'profile_form': profile_form,'username':username},context)
			elif isDoctor(request.user) or isNurse(request.user):
				x = MedicalInfo.objects.get(username = username)
				medical_form = MedicalInfoForm(instance = x)
				print(medical_form)
				return render_to_response('healthnetapp/update_nurse.html',{'medical_form': medical_form,'username':username},context)
			else:
				x = MedicalInfo.objects.get(username = username)
				medical_form = MedicalInfoForm(instance = x)
				return render_to_response('healthnetapp/update_nurse.html',{ 'profile_form': profile_form,'medical_form': medical_form,'username':username},context)
	else:
		return HttpResponse("You are lacking permission to view this page.")
		
def updateManager(request,username):
	"""
	Allows certain staff to update a manager's info
	username - the username of the patient
	"""
	context = RequestContext(request)
	if not(isPatient(request.user)):
		
		if request.method == 'POST':
			user_form = UserForm(data=request.POST)
			profile_form = ManagerProfileForm(data=request.POST)
			y = ManagerProfile.objects.filter(username = username)[0]
			tempy = profile_form.save(commit=False)
			y.copy(tempy)
			y.save()
			
			try:
				medical_form = MedicalInfoForm(data=request.POST)
				x = MedicalInfo.objects.get(username = username)
				tempx = medical_form.save(commit=False)
				x.copy(tempx)
				x.save()
			except:
				pass
				
			l = Log()
			l.type = "Manager Info Updated"
			l.username = request.user.username
			l.save()
			
			return HttpResponseRedirect('/healthnetapp/user/')
		else:
			y = ManagerProfile.objects.filter(username = username)[0]
			profile_form = ManagerProfileForm(instance = y)
			if(request.user.username == username):
				return render_to_response('healthnetapp/update_manager.html',{ 'profile_form': profile_form,'username':username},context)
			elif isDoctor(request.user) or isNurse(request.user):
				x = MedicalInfo.objects.get(username = username)
				medical_form = MedicalInfoForm(instance = x)
				return render_to_response('healthnetapp/update_manager.html',{'medical_form': medical_form,'username':username},context)
			else:
				x = MedicalInfo.objects.get(username = username)
				medical_form = MedicalInfoForm(instance = x)
				return render_to_response('healthnetapp/update_manager.html',{ 'profile_form': profile_form,'medical_form': medical_form,'username':username},context)
	else:
		return HttpResponse("You are lacking permission to view this page.")
def updateSecretary(request,username):
	"""
	Allows certain staff to update a secretary's info
	username - the username of the secretary
	"""
	context = RequestContext(request)
	if not(isPatient(request.user)):

		if request.method == 'POST':
			user_form = UserForm(data=request.POST)
			profile_form = SecretaryProfileForm(data=request.POST)
			y = SecretaryProfile.objects.filter(username = username)[0]
			tempy = profile_form.save(commit=False)
			y.copy(tempy)
			y.save()
			
			try:
				medical_form = MedicalInfoForm(data=request.POST)
				x = MedicalInfo.objects.get(username = username)
				tempx = medical_form.save(commit=False)
				x.copy(tempx)
				x.save()
			except:
				pass
				
			l = Log()
			l.type = "Secretary Info Updated"
			l.username = request.user.username
			l.save()
			
			return HttpResponseRedirect('/healthnetapp/user/')
		else:
			y = SecretaryProfile.objects.filter(username = username)[0]
			profile_form = SecretaryProfileForm(instance = y)
			if(request.user.username == username):
				return render_to_response('healthnetapp/update_secretary.html',{ 'profile_form': profile_form,'username':username},context)
			elif isDoctor(request.user) or isNurse(request.user):
				x = MedicalInfo.objects.get(username = username)
				medical_form = MedicalInfoForm(instance = x)
				return render_to_response('healthnetapp/update_secretary.html',{'medical_form': medical_form,'username':username},context)
			else:
				x = MedicalInfo.objects.get(username = username)
				medical_form = MedicalInfoForm(instance = x)
				return render_to_response('healthnetapp/update_secretary.html',{ 'profile_form': profile_form,'medical_form': medical_form,'username':username},context)
	else:
		return HttpResponse("You are lacking permission to view this page.")
		
def updateAdmin(request,username):
	"""
	Allows certain staff to update an admin's info
	username - the username of the admin
	"""
	context = RequestContext(request)
	if not(isPatient(request.user)):
		
		if request.method == 'POST':
			user_form = UserForm(data=request.POST)
			profile_form = AdminProfileForm(data=request.POST)
			y = AdminProfile.objects.filter(username = username)[0]
			tempy = profile_form.save(commit=False)
			y.copy(tempy)
			y.save()
			
			try:
				medical_form = MedicalInfoForm(data=request.POST)
				x = MedicalInfo.objects.get(username = username)
				tempx = medical_form.save(commit=False)
				x.copy(tempx)
				x.save()
			except:
				pass
				
			l = Log()
			l.type = "Admin Info Updated"
			l.username = request.user.username
			l.save()
			
			return HttpResponseRedirect('/healthnetapp/user/')
		else:
			y = AdminProfile.objects.filter(username = username)[0]
			profile_form = AdminProfileForm(instance = y)
			if(request.user.username == username):
				return render_to_response('healthnetapp/update_admin.html',{ 'profile_form': profile_form,'username':username},context)
			elif isDoctor(request.user) or isNurse(request.user):
				x = MedicalInfo.objects.get(username = username)
				medical_form = MedicalInfoForm(instance = x)
				return render_to_response('healthnetapp/update_admin.html',{'medical_form': medical_form,'username':username},context)
			else:
				x = MedicalInfo.objects.get(username = username)
				medical_form = MedicalInfoForm(instance = x)
				return render_to_response('healthnetapp/update_admin.html',{ 'profile_form': profile_form,'medical_form': medical_form,'username':username},context)
	else:
		return HttpResponse("You are lacking permission to view this page.")
		
@login_required	
def patientList(request):
	"""
	Lists the patients
	"""
	context = RequestContext(request)
	if isAdmin(request.user):
		modify = True
		dict = {'patients': PatientProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/patient_list.html', dict, context)
	if(isDoctor(request.user)):
		modify = True
		dict = {'patients': PatientProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/patient_list.html', dict, context)
	if(isNurse(request.user)):
		modify = True
		dict = {'patients': PatientProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/patient_list.html', dict, context)
	if(isManager(request.user)):
		modify = True
		dict = {'patients': PatientProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/patient_list.html', dict, context)
	if(isSecretary(request.user)):
		modify = True
		dict = {'patients': PatientProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/patient_list.html', dict, context)
	else:
		return HttpResponse("you are lacking permission to view this page")
		
@login_required		
def doctorList(request):
	"""
	Lists the doctors
	"""
	context = RequestContext(request)
	if isAdmin(request.user):
		modify = True
		dict = {'doctors': DoctorProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/doctor_list.html', dict, context)
	if(isDoctor(request.user)):
		modify = True
		dict = {'doctors': DoctorProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/doctor_list.html', dict, context)
	if(isNurse(request.user)):
		modify = True
		dict = {'doctors': DoctorProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/doctor_list.html', dict, context)
	if(isManager(request.user)):
		modify = True
		dict = {'doctors': DoctorProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/doctor_list.html', dict, context)
	if(isSecretary(request.user)):
		modify = True
		dict = {'doctors': DoctorProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/doctor_list.html', dict, context)
	else:
		modify = False
		dict = {'doctors': DoctorProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/doctor_list.html', dict, context)
		
@login_required		
def nurseList(request):
	"""
	Lists the nurses
	"""
	context = RequestContext(request)
	if isAdmin(request.user):
		modify = True
		dict = {'nurses': NurseProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/nurse_list.html', dict, context)
	if(isDoctor(request.user)):
		modify = True
		dict = {'nurses': NurseProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/nurse_list.html', dict, context)
	if(isNurse(request.user)):
		modify = True
		dict = {'nurses': NurseProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/nurse_list.html', dict, context)
	if(isManager(request.user)):
		modify = True
		dict = {'nurses': NurseProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/nurse_list.html', dict, context)
	if(isSecretary(request.user)):
		modify = True
		dict = {'nurses': NurseProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/nurse_list.html', dict, context)
	else:
		modify = False
		dict = {'nurses': NurseProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/nurse_list.html', dict, context)

@login_required		
def managerList(request):
	"""
	Lists the managers
	"""
	context = RequestContext(request)
	if isAdmin(request.user):
		modify = True
		dict = {'managers': ManagerProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/manager_list.html', dict, context)
	if(isDoctor(request.user)):
		modify = True
		dict = {'managers': ManagerProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/manager_list.html', dict, context)
	if(isNurse(request.user)):
		modify = True
		dict = {'managers': ManagerProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/manager_list.html', dict, context)
	if(isManager(request.user)):
		modify = True
		dict = {'managers': ManagerProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/manager_list.html', dict, context)
	if(isSecretary(request.user)):
		modify = True
		dict = {'managers': ManagerProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/manager_list.html', dict, context)
	else:
		modify = False
		dict = {'managers': ManagerProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/manager_list.html', dict, context)

@login_required		
def secretaryList(request):
	"""
	Lists the secretaries
	"""
	context = RequestContext(request)
	if isAdmin(request.user):
		modify = True
		dict = {'secretaries': SecretaryProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/secretary_list.html', dict, context)
	if(isDoctor(request.user)):
		modify = True
		dict = {'secretaries': SecretaryProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/secretary_list.html', dict, context)
	if(isNurse(request.user)):
		modify = True
		dict = {'secretaries': SecretaryProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/secretary_list.html', dict, context)
	if(isManager(request.user)):
		modify = True
		dict = {'secretaries': SecretaryProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/secretary_list.html', dict, context)
	if(isSecretary(request.user)):
		modify = True
		dict = {'secretaries': SecretaryProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/secretary_list.html', dict, context)
	else:
		modify = False
		dict = {'secretaries': SecretaryProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/secretary_list.html', dict, context)

@login_required		
def adminList(request):
	"""
	Lists the admins
	"""
	context = RequestContext(request)
	if isAdmin(request.user):
		modify = True
		dict = {'admins': AdminProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/admin_list.html', dict, context)
	if(isDoctor(request.user)):
		modify = True
		dict = {'admins': AdminProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/admin_list.html', dict, context)
	if(isNurse(request.user)):
		modify = True
		dict = {'admins': AdminProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/admin_list.html', dict, context)
	if(isManager(request.user)):
		modify = True
		dict = {'admins': AdminProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/admin_list.html', dict, context)
	if(isSecretary(request.user)):
		modify = True
		dict = {'admins': AdminProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/admin_list.html', dict, context)
	else:
		modify = False
		dict = {'admins': AdminProfile.objects.all() ,'modify':modify}
		return render_to_response('healthnetapp/secretary_list.html', dict, context)
		
@login_required	
def pending(request):
	"""
	Lists the appointments that need approval
	"""
	context = RequestContext(request)
	if(not(isPatient(request.user))):
		x = Entry.objects.filter(approved = False)
		dict = {'appointments': x}
		return render_to_response('healthnetapp/pending_list.html', dict, context)
		
@login_required
def approved(request, y, action):
	"""
	Approves / declines the appointments
	action - an approval / decline
	"""
	context = RequestContext(request)
	if(not(isPatient(request.user))):
		x = Entry.objects.filter(approved = False)
		for a in x:
			if(a.idtag == y):
				if(action == 'y'):
					a.approved = True
					a.save()
					l = Log()
					l.type = "Appointment Approved"
					l.username = request.user.username
					l.save()
				if(action == 'n'):
					a.delete()
					l = Log()
					l.type = "Appointment Declined"
					l.username = request.user.username
					l.save()
				return HttpResponseRedirect('/healthnetapp/user/')

@login_required
def viewInfo(request,username):
	"""
	Views the user's information
	username - the user that the information belongs to
	"""
	context = RequestContext(request)
	if(not(isPatient(request.user))):
		try:
			if(UserStatus.objects.get(username = username).type == 'admin'):
				x = AdminProfile.objects.get(username = username)
			elif(UserStatus.objects.get(username = username).type == 'doctor'):
				x = DoctorProfile.objects.get(username = username)
			elif(UserStatus.objects.get(username = username).type == 'nurse'):
				x = NurseProfile.objects.get(username = username)
			elif(UserStatus.objects.get(username = username).type == 'manager'):
				x = ManagerProfile.objects.get(username = username)
			elif(UserStatus.objects.get(username = username).type == 'secretary'):
				x = SecretaryProfile.objects.get(username = username)
			else:
				x = PatientProfile.objects.get(username = username)
		except:
			return HttpResponse("error")
		if isDoctor(request.user) or isNurse(request.user):
			y = MedicalInfo.objects.get(username = username)
			dict = {'ProfileInfo':x,'MedicalInfo':y,'medical':True}
			return render_to_response('healthnetapp/view_info.html', dict, context)
		else:
			dict = {'ProfileInfo':x,'medical':False}
			print("hit")
			return render_to_response('healthnetapp/view_info.html', dict, context)
	else:
		return HttpResponse("You do not have permission to view this page. Hit backspace to return to previous page.")
@login_required
def admit_a(request,patient):
	"""
	Displays patients that can be admitted to a hospital
	patient - the patient being admitted
	"""
	if( isDoctor(request.user) or isNurse(request.user)):
		context = RequestContext(request)
		x = Hospital.objects.all()
		dict = {'hospitals':x,'patient':patient}
		return render_to_response('healthnetapp/hospital_admit.html', dict, context)
	else:
		return HttpResponse("you are lacking permission to view this page")
@login_required
def admit_b(request,hospital,patient):
	"""
	Admits a patient to a hospital
	hospital - the hospital the patient is being admitted to
	patient - the patient being admitted
	"""
	if( isDoctor(request.user) or isNurse(request.user)):
		x = MedicalInfo.objects.get(username = patient)
		if(x.currenthospital == hospital):
			return HttpResponse("patient is already admitted to this hospital")
		else:	
			x.currenthospital = hospital
			x.save()
			l = Log()
			l.type = patient + " admitted to " + hospital
			l.username = request.user.username
			l.save()
		return HttpResponseRedirect('/healthnetapp/user/')
	else:
		return HttpResponse("you are lacking permission to view this page")
		
@login_required
def discharge(request,patient):
	"""
	Discharges a patient from a hospital
	patient - the patient being discharged
	"""
	context = RequestContext(request)
	if( isDoctor(request.user)):
		x = MedicalInfo.objects.get(username = patient)
		if(x.currenthospital == 'none'):
			return HttpResponse("Patient was not in hospital")
		l = Log()
		l.type = patient + " discharged from " + x.currenthospital
		l.username = request.user.username
		l.save()
		x.currenthospital = 'none'
		x.save()
		return HttpResponseRedirect('/healthnetapp/user/')
	else:
		return HttpResponse("you are lacking permission to view this page")
		
@login_required		
def messageList(request):
	"""
	Displays the messages received by the user
	"""
	context = RequestContext(request)
	messages = Message.objects.filter(reciever = request.user.username)
	dict = {'messages': messages}
	return render_to_response('healthnetapp/message_list.html', dict, context)
	
@login_required		
def writeMessage(request,reciever):
	"""
	Writes a message to another user
	receiver - the person receiving the message
	"""
	context = RequestContext(request)
	if request.method == 'POST':
		form = MessageForm(data=request.POST)

		if form.is_valid():
			message = form.save(commit=False)
			
			message.sender = request.user.username
			message.reciever = reciever
			message.save()
			
			l = Log()
			l.type = "message sent"
			l.username = request.user.username
			l.save()
			return render_to_response('healthnetapp/user.html', {}, context)
		else:
			return HttpResponse("form is invalid")
		
	else:
		form = MessageForm()
		return render_to_response('healthnetapp/write_message.html',{'form': form,'reciever':reciever},context)
	
@login_required	
def logList(request):
	"""
	Displays the actions done by users
	"""
	context = RequestContext(request)
	if request.user.is_superuser:
		dict = {'logs':reversed(Log.objects.all())}
		return render_to_response('healthnetapp/logs_list.html', dict, context)
	else:
		return HttpResponse("You are lacking permission to view this page.")

@login_required
def statistics(request):
	"""
	Shows the statistics for the site
	"""
	context = RequestContext(request)
	if isAdmin(request.user):
		hoslist = []
		for hos in Hospital.objects.all():
			hoslist.append([hos.name,0])
			for user in MedicalInfo.objects.all():
				if(hos.name == user.currenthospital):
					hoslist[-1][1] += 1
		patcount = len(PatientProfile.objects.all())
		doccount = len(DoctorProfile.objects.all())
		nurcount = len(NurseProfile.objects.all())
		mancount = len(ManagerProfile.objects.all())
		seccount = len(SecretaryProfile.objects.all())
		admcount = len(AdminProfile.objects.all())
		average = len(Entry.objects.all()) / len(PatientProfile.objects.all())
		dict = {'hoslist':hoslist,'patcount':patcount,'doccount':doccount,'nurcount':nurcount,'mancount':mancount,'seccount':seccount,'admcount':admcount,'average':average}
		return render_to_response('healthnetapp/statistics.html',dict,context)
	
def isPatient(user):
	"""
	Checks if the user is a patient
	user - the user being tested
	"""
	return(UserStatus.objects.get(username = user.username).patient)
def isAdmin(user):
	"""
	Checks if the user is an admin
	user - the user being tested
	"""
	return(UserStatus.objects.get(username = user.username).type == 'admin')
def isDoctor(user):
	"""
	Checks if the user is a doctor
	user - the user being tested
	"""
	return(UserStatus.objects.get(username = user.username).type == 'doctor')
def isNurse(user):
	"""
	Checks if the user is a nurse
	user - the user being tested
	"""
	return(UserStatus.objects.get(username = user.username).type == 'nurse')
def isManager(user):
	"""
	Checks if the user is a manager
	user - the user being tested
	"""
	return(UserStatus.objects.get(username = user.username).type == 'manager')
def isSecretary(user):
	"""
	Checks if the user is a secretary
	user - the user being tested
	"""
	return(UserStatus.objects.get(username = user.username).type == 'secretary')
