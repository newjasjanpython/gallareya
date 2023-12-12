from django.urls import path
from .views import *

app_name = 'cadmin'

urlpatterns = [
    path('', IndexView.as_view()),
    path('<str:name>-admin-page-view', ListElementsView.as_view()),
    path('<str:name>-admin-page-view/create', CreateView.as_view()),
    path('<str:name>-admin-page-view/<int:pk>/delete', DeleteView.as_view()),
    path('<str:name>-admin-page-view/<int:pk>/edit', EditView.as_view()),
]
