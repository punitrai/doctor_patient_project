from django.shortcuts import render

from rest_framework.response import Response
from .models import *
from django.views import *
from rest_framework import viewsets
from django.contrib.auth.models import User 
from rest_framework.response import Response
from .models import *
from django.utils.timezone import now, timedelta
from oauth2_provider.settings import oauth2_settings
from oauthlib.common import generate_token
from oauth2_provider.models import AccessToken, Application, RefreshToken
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings    
from django.contrib.auth import get_user_model
from adminpanel.models import *
import datetime

User = get_user_model()


class registerViewSet(viewsets.ViewSet):
	# permission_classes = [TokenHasReadWriteScope]
	def list(self, request):
		
		User_data = User.objects.all()
		User_data_list = []
		for user in User_data:
			User_data_list.append({
				"email":user.email,
				"Name":user.full_name,
				"password":user.password,
				"mobile_number":user.mobile_number,
				
				
			})
			
		return Response({"users":User_data_list})
	
	def create(self, request):
		full_name =request.data.get('full_name')
		email = request.data.get('email')
		mobile_number=request.data.get('mobile_number')
		password=request.data.get('password')      
		date_of_birth = request.data.get('date_of_birth')
		gender = request.data.get('gender')
		blood_group = request.data.get('blood_group')
		address = request.data.get('address')
		user_type = request.data.get('user_type')
		education = request.data.get('education')
		document = request.data.get('document')
			
		
		user = MyUser()       
		
		user.full_name = full_name
		user.set_password(password)
		user.email = email
		user.mobile_number = mobile_number
		user.date_of_birth = date_of_birth
		user.gender = gender
		user.blood_group = blood_group
		user.address = address
		
		user.user_type = user_type      
	  
		user.save()
		print(user.user_type=="Patient")
		if  not (user.user_type=="Patient"):
			for val in education:
				edu = Educations()
				edu.doctor_degree = val['doctor_degree']
				edu.university = val['university']
				edu.passing_year = val['passing_year']
				edu.user=user
				edu.save()
				
			for val in document:
				edu = Documents()
				edu.documents_name = val['documents_name']
				edu.date_uploaded = val['date_uploaded']
				edu.file_size = val['file_size']
				edu.user=user
				edu.save()	
		
		
			app = Application.objects.create(user=user)
			token = generate_token()
			refresh_token = generate_token()
			expires = now() + timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS)
			scope = "read write"
			access_token = AccessToken.objects.create(user=user,
													application=app,
													expires=expires,
													token=token,
													scope=scope,
													)
			print("access token ------->", access_token)
			RefreshToken.objects.create(user=user,
										application=app,
										token=refresh_token,
										access_token=access_token
										)
			response = {
				'access_token': access_token.token,
				'expires_in': oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
				'token_type': 'Bearer',
				'refresh_token': access_token.refresh_token.token,
				'client_id': app.client_id,
				'client_secret': app.client_secret
				} 
			# send_mail(
			#     'try',
			#     'you just registered',
			#     'punit.innotical@gmail.com',
			#     ['faiz.innotical@gmail.com'],
			# fail_silently=False)           
			return Response({"response of doctor":response})
		else:
			app = Application.objects.create(user=user)
			token = generate_token()
			refresh_token = generate_token()
			expires = now() + timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS)
			scope = "read write"
			access_token = AccessToken.objects.create(user=user,
													application=app,
													expires=expires,
													token=token,
													scope=scope,
													)
			print("access token ------->", access_token)
			RefreshToken.objects.create(user=user,
										application=app,
										token=refresh_token,
										access_token=access_token
										)
			response = {
				'access_token': access_token.token,
				'expires_in': oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
				'token_type': 'Bearer',
				'refresh_token': access_token.refresh_token.token,
				'client_id': app.client_id,
				'client_secret': app.client_secret
				} 
			return Response({"response of patient":response})

class LoginViewSet(viewsets.ViewSet):
	def create(self, request): 
		email = request.data.get('email')
		password=request.data.get('password')  
		user = authenticate(email=email, password=password)

		if user is not None:
			app = Application.objects.get(user=user)
			token = generate_token()
			refresh_token = generate_token()
			expires = now() + timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS)
			scope = "read write"
			access_token = AccessToken.objects.create(user=user,
			application=app,
			expires=expires,
			token=token,
			scope=scope,
			)
			RefreshToken.objects.create(user=user,
										application=app,
										token=refresh_token,
										access_token=access_token
										)
			response = {
					'access_token': access_token.token,
					'expires_in': oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
					'token_type': 'Bearer',
					'refresh_token': access_token.refresh_token.token,
					'client_id': app.client_id,
					'client_secret': app.client_secret
				}
		#     send_mail(
		#     'try',
		#     'you just registered',
		#     'punit.innotical@gmail.com',
		#     ['faiz.innotical@gmail.com'],
		# fail_silently=False)     
			return Response({"response":response})

		else:
			return Response("excess denied")
		
class PatientViewSet(viewsets.ViewSet):
	def list(self,request):
		Patients = MyUser.objects.filter(user_type='Patient')
		Patients_List=[]
		for ptt in Patients:
			Patients_List.append({
			"full_name":ptt.full_name,
			"date_of_birth":ptt.date_of_birth,
			"email":ptt.email,
			"mobile_number":ptt.mobile_number,
			# "family_number":ptt.family_number,
		  })
		return Response({"Patients":Patients_List})

	def retrieve(self,request,pk=None):
		patients = MyUser.objects.get(id=pk)
		familymember = Familymember.objects.filter(user=patients)
		patients_List=[]
		for ptt in familymember:
			patients_List.append({
				"member_name":ptt.member_name,
		 		"relation_type":ptt.relation_type
			
		  })
		
		# apointt = Apointments.objects.filter(id=pk)
		# apoint_List=[]
		# for aptt in apointt:
		# 	apoint_List.append({


		# 	})
		return Response({"patient_full_name":patients.full_name,"family_member_details":patients_List
						})
	# ,"patient_apointment":apoint_List
class DoctorViewSet(viewsets.ViewSet):
	def list(self,request):
		Doctor = MyUser.objects.filter(user_type='Doctor')
		Doctor_list=[]
		for doc in Doctor:

		    Doctor_list.append({
				"full_name":doc.full_name,
				"email":doc.email,
				"mobile_number":doc.mobile_number,
				"address":doc.address
				

		})
		return Response({"Doctor":Doctor_list})

	def retrieve(self,request,pk=None):
		doctor = MyUser.objects.get(id=pk)
		education_doctor = Educations.objects.filter(user=doctor)
		doc_edu=[]
		for doc in education_doctor:
			doc_edu.append({
				"doctor_degree":doc.doctor_degree,
				"university":doc.university,
				"passing_year":doc.passing_year,
				
			})
		doc_document = Documents.objects.filter(user=doctor)
		doc_document_list=[]
		for edu in doc_document:
			doc_document_list.append({
				"documents_name":edu.documents_name,
				"date_uploaded":edu.date_uploaded,
				"file_size":edu.file_size
			})
		
		doc_apointt = Apointments.objects.filter(doctor=doctor)
		doc_apointt_list=[]
		for doc in doc_apointt:
			doc_apointt_list.append({
				"full_name":doc.patient.full_name,
				"date":doc.date,
				"time":doc.time,
				"mobile_numb4er":doc.patient.mobile_number,
				"email":doc.patient.email
			})
		return Response({"Doctor_name":doctor.full_name,"doctor":doc_edu,
		"Doctor_document":doc_document_list,"Apointment_list_for_doctor":doc_apointt_list})
		
		#  ,"doc_edu":doc_edu_list,"doc_docu":doc_docu_list,"doc_apointt":doc_apointt_list