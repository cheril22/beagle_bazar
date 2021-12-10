from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
from veloce.models.profile import Profile
from veloce.oauth import refetch_profile
import requests, json


def login_forbidden(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


def allowed_user(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.user.is_authenticated:
                if request.user.is_superuser:
                    return view_func(request, *args, **kwargs)
                else:
                    veloce_user = request.user.profile
                    account_type = veloce_user.account_type
                    if account_type in allowed_roles:
                        return view_func(request, *args, **kwargs)
                    else:
                        messages.warning(request, mark_safe(
                            "<b>Access Denied!</b> You are not a valid user for the entered url !"))
                        return redirect('index')

        return wrapper_func

    return decorator


def level_required(level=Profile.MIN_LEVEL):
    """
    Validate user has completed all the step or not
    """
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.user.profile.is_complete == level and request.user.profile.is_verified == level:
                return view_func(request, *args, **kwargs)
            else:
                refetch_profile(request.user)
                return HttpResponseRedirect(settings.FINTECH_URL + '/incomplete-profile')
        return wrapper_func

    return decorator

def all_level_approved():
    """
    Validate admin has approved all the step or not
    """
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            try:
                print(request.user.profile.user)
                data = {'uid': request.user.profile.user.email}
                res = requests.get('https://veloceinnovations.tech/check-updated-module-approved/', params=data).text
                response = json.loads(res)
                if response['status'] == False:
                    messages.error(request, mark_safe(
                            "<b>Access Denied!</b> Your updated profile info needs to be approved by admin first! <a href='https://veloceinnovations.tech/'>Click here</a> to check."))
                    return view_func(request, *args, **kwargs)
                return view_func(request, *args, **kwargs)
            except Exception as e:
                print(e)
                return view_func(request, *args, **kwargs)
        return wrapper_func

    return decorator
