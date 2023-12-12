from django.http.response import HttpResponse
from django.contrib.auth.mixins import AccessMixin
from django.conf import settings

class TokenMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        token = request.headers.get('token')

        if token == settings.ACCEPT_TOKEN:
            return super().dispatch(request, *args, **kwargs)
        return HttpResponse(f"{token} is not allowed")
