from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from django.utils.safestring import mark_safe
from veloce import methods


def register(request):
    """
    This method is built to perform user creation functionality
    :param request:
    :return:
    """
    return HttpResponseRedirect(settings.OAUTH_URL + "/accounts/register/")


def login(request):
    return HttpResponseRedirect('/login/vauth')


def logout(request):
    """
    This function end the user login session.
    :param request:
    :return:
    """
    methods.auth.logout(request)
    next_url = request.build_absolute_uri("/")
    return redirect(settings.OAUTH_URL + "/accounts/logout?next=" + next_url)


@login_required
def change_password(request):
    """
    This functiona allow auth user to look the profile of its own.
    :param request:
    :return:
    """
    return redirect(settings.OAUTH_URL + "/accounts/change-password/")

def profile_overview(request):
    """
    This functiona allow auth user to change his password by macthing old.
    :param request:
    :return:
    """
    return redirect(settings.OAUTH_URL + "/step/1/1")


@login_required
def change_profile(request, pk):
    """
    This function allow auth user to change his/her profile.
    :param request:
    :param pk:
    :return:
    """
    error = ''
    if request.user.id == pk:
        return HttpResponseRedirect(settings.OAUTH_URL + "/overview")
    else:
        messages.warning(request, mark_safe("<b>Access Denied!</b> You are not a valid user for the entered url !"))
        return redirect('dashboard')


def check_auth(request):
    if request.user.is_authenticated:
        if request.user.profile.is_complete and request.user.profile.is_verified:
            context = {
                "status": True,
                "message": "Auth User"
            }
        else:
            context = {
                "status": False,
                "url": settings.FINTECH_URL + '/incomplete-profile'
            }
        return JsonResponse(context)
    else:
        context = {
            "status": False,
            "url": "/login/vauth"
        }
        return JsonResponse(context)