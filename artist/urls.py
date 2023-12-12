from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import *

app_name = 'artist'

urlpatterns = [
    path('<str:slug>', IndexPage.as_view()),
    path('<str:slug>/drafts', ListDrafts.as_view()),
    path('<str:slug>/messages', ListNotifications.as_view()),
    path('<str:slug>/comments', CommentsView.as_view()),
    path('<str:slug>/socials', SocialsView.as_view()),
    path('<str:slug>/arts-only', ListArtistArts.as_view()),
    path('<str:slug>/privacy', privacy),

    path('<int:pk>/edit-name', edit_name),
    path('<int:pk>/edit-about', edit_about),
    path('<str:slug>/edit-about-no1/', csrf_exempt(EditAboutApi.as_view())),
    path('<int:pk>/edit-image', edit_image),

    path('api/reply/<int:art>', csrf_exempt(AddMessageView.as_view())),
    path('api/on-verificaion-view', csrf_exempt(OnVerificationCreateView.as_view())),
    path('api/on-verificaion-manage', csrf_exempt(OnVerificationManageView.as_view())),
    path('api/verify-view', csrf_exempt(VerifyView.as_view())),
    path('api/get-categories', get_categories),
    path('api/exists/<str:sk>', is_artist),
]
