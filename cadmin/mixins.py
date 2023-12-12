from django.shortcuts import redirect
from django.contrib.auth.mixins import AccessMixin


class IsAdmin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return super().dispatch(request, *args, **kwargs)
        return redirect('/')
