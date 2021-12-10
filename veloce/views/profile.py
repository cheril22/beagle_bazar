from django.shortcuts import redirect
from django.conf import settings


def edit_profile(request):
    return redirect(settings.OAUTH_URL + '/overview')
