from django.contrib import auth
from django.contrib.auth.models import User
from veloce import models
from django.shortcuts import get_object_or_404
import requests, json
from datetime import datetime, timezone
from django.http import JsonResponse

def register(form, request):
    user = form.save(commit=False)
    user.user = User.objects.create_user(
        user.email_address, password=form.cleaned_data['password']
    )
    user.save()


def login(form, request):
    get_user = User.objects.filter(username=form.data['username'])
    if get_user.count() > 0:
        if get_user[0].is_active:
            user = auth.authenticate(
                username=form.data['username'],
                password=form.data['password']
            )
            if user is not None:
                auth.login(request, user)
                context = {
                    "status": True,
                    "message": form.data['username'] + " login successfully!"
                }
                return context
            else:
                context = {
                    "status": False,
                    "message": "Login unsuccessful. Please check your email and password again."
                }
                return context
        else:
            context = {
                "status": False,
                "message": form.data['username'] + " your account is inactive ! Contact Admin."
            }
            return context
    else:
        context = {
            "status": False,
            "message": form.data['username'] + " account does not exists!"
        }
        return context


def logout(request):
    auth.logout(request)


def change_password(form, request):
    user = auth.get_user(request)
    if auth.authenticate(username=user.username, password=form.data['current_password']):
        user.set_password(form.data['new_password'])
        user.save()
        return True
    return False


def check_user_level_status(user_id):
    check_user_eligibility_level = models.Profile.objects.get(user_id=user_id)
    if check_user_eligibility_level.completion_level == 0 and check_user_eligibility_level.verification_level == 0:
        context = {
            'status' : False,
            'complete_level': check_user_eligibility_level.completion_level,
            'verification_level': check_user_eligibility_level.verification_level,
            'level': 0,
            'msg': "You are currently initial stage, please complete your profile."
        }
    elif check_user_eligibility_level.completion_level == 1 and check_user_eligibility_level.verification_level == 0:
        context = {
            'status': False,
            'complete_level': check_user_eligibility_level.completion_level,
            'verification_level': check_user_eligibility_level.verification_level,
            'level': 0,
            'msg': "Please make sure that your level 1 info is approved !!!"
        }
    elif check_user_eligibility_level.completion_level == 1 and check_user_eligibility_level.verification_level == 1:
        context = {
            'status': True,
            'complete_level': check_user_eligibility_level.completion_level,
            'verification_level': check_user_eligibility_level.verification_level,
            'level': 1,
        }
    elif check_user_eligibility_level.completion_level == 2 and check_user_eligibility_level.verification_level == 0:
        context = {
            'status': False,
            'complete_level': check_user_eligibility_level.completion_level,
            'verification_level': check_user_eligibility_level.verification_level,
            'level': 1,
            'msg': "Please make sure that your level 2 info is approved !!!"
        }
    elif check_user_eligibility_level.completion_level == 2 and check_user_eligibility_level.verification_level == 0:
        context = {
            'status': False,
            'complete_level': check_user_eligibility_level.completion_level,
            'verification_level': check_user_eligibility_level.verification_level,
            'level': 1,
            'msg': "Please make sure that your level 2 info is approved !!!"
        }
    return context


def get_finance_scheme_details_by_billno(request, bill_no, borrower_email):
    data = {
        'bill_no': bill_no,
        'borrower_email': borrower_email
    }
    response = requests.get('https://velocefintech.com/get-finance-scheme-details/', params=data)
    if response.status_code == 200:
        final_data = json.loads(response.text)
        data = final_data
    else:
        data = ''
    return data



def get_active_scheme(schemes):
    current_date = datetime.now()
    current_date = datetime.strftime(current_date, '%Y-%m-%d %H:%M:%S')
    expired = []
    for scheme in schemes:
        end_date = scheme.end_date.strftime('%Y-%m-%d %H:%M:%S')
        if end_date < current_date:
            print(scheme)
            expired.append(scheme.id)
    return expired
