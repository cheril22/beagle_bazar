from django.conf import settings


class MenuItem:
    def __init__(self, url, name, subitem=False):
        self.url = url
        self.name = name
        self.classname = "btn" if not subitem else "btn subitem"


class MenuInjectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        menu = self.generate_menu(request)
        for item in menu:
            if request.get_full_path() == item.url:
                item.classname += " active"
        response.context_data["menu"] = menu
        response.context_data["authenticated"] = request.user.is_authenticated
        return response

    def generate_menu(self, request):
        if request.user.is_authenticated:
            return [

                MenuItem(settings.OAUTH_URL + "/overview", "Edit Profile", True),
                MenuItem(settings.OAUTH_URL + "/accounts/change-password/", "Change Password", True),

            ]

        # Unauthenticated menu
        return [
            MenuItem(settings.OAUTH_URL + "/accounts/register/", "Register", True),
            MenuItem("/login/vauth", "Sign In", True),

        ]
