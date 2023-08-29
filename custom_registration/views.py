from registration.backends.default.views import RegistrationView
from django.shortcuts import render


class CustomRegistrationView(RegistrationView):
    def get(self, request, *args, **kwargs):
        # Customize your registration view here, e.g., render a page with a message.
        return render(request, 'custom_registration/registration_disabled.html')
